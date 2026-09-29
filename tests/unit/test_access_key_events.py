"""Access-key events: label resolution in the poll path and entity dedup."""
from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "custom_components"))

from my_dom_ru.access_keys import parse_key_names  # noqa: E402
from my_dom_ru.api import HistoryEvent, HistoryPage  # noqa: E402
from my_dom_ru.history import (  # noqa: E402
    HistoryPoller,
    HistoryWatermark,
    map_general_event_type,
)

KEY_NAMES = "098b987y = Сын\n098c112z = Жена"
STREAM = "general:55:accessControl:101"


def make_event(
    *,
    event_type: str = "accessKeyActivated",
    event_id: str = "e1",
    message: str = "Адрес открыта ключom 098b987y",
    source_type: str = "accessControl",
    source_id: str = "101",
) -> HistoryEvent:
    return HistoryEvent(
        id=event_id,
        place_id="55",
        event_type=event_type,
        # A key named in the message only counts inside the poller's
        # _KEY_LOOKBACK window, so the timestamp has to be current.
        timestamp=int(datetime.now(UTC).timestamp()),
        source_type=source_type,
        source_id=source_id,
        message=message,
    )


class FakeApi:
    """Minimal coordinator.api returning one fixed page."""

    def __init__(self, events: list[HistoryEvent]) -> None:
        self._events = events

    async def query_events(self, place_ids, page: int = 0) -> HistoryPage:
        return HistoryPage(events=tuple(self._events), number=0, last=True)

    async def query_camera_events(self, camera_id, lower_date, upper_date):
        return ()


class FakeCoordinator:
    def __init__(self, events: list[HistoryEvent], options: dict | None = None):
        self.data = {"places": [{"place": {"id": 55}}], "cameras": []}
        self.api = FakeApi(events)
        self.entry_options_snapshot = options or {}


async def run_poll(events, options=None, watermark=None):
    """Run one poll against a baseline and return the emitted payloads."""
    emitted: list[dict[str, Any]] = []
    poller = HistoryPoller(
        FakeCoordinator(events, options),
        watermark if watermark is not None else HistoryWatermark(),
        emitted.append,
        key_index=lambda: parse_key_names((options or {}).get("key_names")),
    )
    await poller.async_poll()
    return emitted


async def run_poll_after_baseline(events, options=None):
    """Run a poll against a seeded watermark so events count as new."""
    return await run_poll(events, options, HistoryWatermark({STREAM: ["seed"]}))


class TestMapGeneralEventType:
    def test_key_activation_is_whitelisted(self) -> None:
        # Before this change accessKeyActivated arrived and was silently
        # dropped, because only the two call types were mapped.
        assert map_general_event_type("accessKeyActivated") == "key_activated"

    def test_call_types_still_map(self) -> None:
        assert map_general_event_type("accessControlCallAccepted") == "call_accepted"
        assert map_general_event_type("accessControlCallMissed") == "call_missed"

    def test_unknown_type_is_none(self) -> None:
        assert map_general_event_type("billingNotification") is None


@pytest.mark.asyncio
class TestPollPath:
    async def test_first_poll_is_a_silent_baseline(self) -> None:
        # Existing behaviour: no watermark stream means nothing is emitted, so
        # enabling this does not replay the operator's whole history at once.
        assert await run_poll([make_event()], {"key_names": KEY_NAMES}) == []

    async def test_emits_key_event_with_label(self) -> None:
        emitted = await run_poll_after_baseline([make_event()], {"key_names": KEY_NAMES})
        assert len(emitted) == 1
        assert emitted[0]["event_type"] == "key_activated"
        assert emitted[0]["key_name"] == "Сын"
        assert emitted[0]["source_id"] == "101"

    async def test_raw_message_is_not_propagated(self) -> None:
        emitted = await run_poll_after_baseline(
            [make_event(message="Адрес открыта ключом 098b987y")],
            {"key_names": KEY_NAMES},
        )
        # The operator text carries the key code and must not reach entities,
        # the recorder or diagnostics.
        assert "message" not in emitted[0]
        assert "098b987y" not in str(emitted[0])

    async def test_unlabelled_key_emits_without_key_name(self) -> None:
        emitted = await run_poll_after_baseline(
            [make_event(message="Дверь открыта приложением")],
            {"key_names": KEY_NAMES},
        )
        assert len(emitted) == 1
        assert "key_name" not in emitted[0]

    async def test_empty_mapping_still_emits_event(self) -> None:
        emitted = await run_poll_after_baseline([make_event()], {})
        # Users who do not label keys still get the activation, just anonymous.
        assert len(emitted) == 1
        assert "key_name" not in emitted[0]

    async def test_call_event_gets_no_key_attribute(self) -> None:
        from my_dom_ru.access_keys import parse_key_names

        emitted: list[dict[str, Any]] = []
        poller = HistoryPoller(
            FakeCoordinator(
                [make_event(event_type="accessControlCallAccepted", message="")],
                {"key_names": KEY_NAMES},
            ),
            HistoryWatermark({STREAM: ["seed"]}),
            emitted.append,
            key_index=lambda: parse_key_names(KEY_NAMES),
        )
        await poller.async_poll()
        assert emitted[0]["event_type"] == "call_accepted"
        assert "key_name" not in emitted[0]
