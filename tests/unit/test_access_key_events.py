"""Access-key events: name resolution in the durable poll path.

Names come from the operator's `list_access_keys`, not from a setting — see
`test_no_key_label_option.py` for why the option was removed. Here the index
is supplied directly, which is what `HistoryManager` does at runtime.
"""
from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "custom_components"))

from my_dom_ru.access_keys import build_key_index  # noqa: E402
from my_dom_ru.api import HistoryEvent, HistoryPage  # noqa: E402
from my_dom_ru.history import (  # noqa: E402
    HistoryPoller,
    HistoryWatermark,
    map_general_event_type,
)

CODE = "098b987y"

# What the operator's list_access_keys yields for this account.
OPERATOR_KEYS = [
    {"id": 1, "placeId": 55,
     "accessKey": {"accessKeyCode": "098b987y", "name": "Сын"}},
    {"id": 2, "placeId": 55,
     "accessKey": {"accessKeyCode": "098c112z", "name": "Жена"}},
]
INDEX = build_key_index(OPERATOR_KEYS)


def make_event(
    *,
    event_type: str = "accessKeyActivated",
    event_id: str = "e1",
    message: str = f"Адрес открыта ключом {CODE}",
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
    def __init__(self, events: list[HistoryEvent]):
        self.data = {"places": [{"place": {"id": 55}}], "cameras": []}
        self.api = FakeApi(events)


async def run_poll(events, *, index=INDEX, baseline=True):
    """Run one poll and return the emitted payloads.

    A stream with no prior watermark is a *silent baseline* and yields
    nothing, so the seed is derived from the events themselves: hardcoding one
    stream would quietly turn a `billingSystem` case into a no-op.
    """
    streams = (
        {
            f"general:{event.place_id}:{event.source_type}:{event.source_id}": [
                "seed"
            ]
            for event in events
        }
        if baseline
        else {}
    )
    emitted: list[dict[str, Any]] = []
    poller = HistoryPoller(
        FakeCoordinator(events),
        HistoryWatermark(streams),
        emitted.append,
        key_index=lambda place_id: index if place_id == "55" else {},
    )
    await poller.async_poll()
    return emitted


async def run_after_baseline(events, *, index=INDEX):
    return await run_poll(events, index=index)


class TestMapGeneralEventType:
    def test_key_activation_is_whitelisted(self) -> None:
        assert map_general_event_type("accessKeyActivated") == "key_activated"

    def test_call_types_still_map(self) -> None:
        assert map_general_event_type("accessControlCallAccepted") == "call_accepted"
        assert map_general_event_type("accessControlCallMissed") == "call_missed"

    def test_unknown_type_is_none(self) -> None:
        assert map_general_event_type("infoNotification") is None


@pytest.mark.asyncio
class TestPollPath:
    async def test_first_poll_is_a_silent_baseline(self) -> None:
        # Existing behaviour: no watermark stream means nothing is emitted, so
        # a new install does not replay the operator's whole history at once.
        assert await run_poll([make_event()], baseline=False) == []

    async def test_emits_key_event_with_operator_name(self) -> None:
        emitted = await run_after_baseline([make_event()])
        assert len(emitted) == 1
        assert emitted[0]["event_type"] == "key_activated"
        # Resolved from the cloud, not from any setting.
        assert emitted[0]["key_name"] == "Сын"
        assert emitted[0]["source_id"] == "101"

    async def test_resolves_by_name_as_well_as_code(self) -> None:
        # The verified live message says "открыта ключом Денис" with no code.
        emitted = await run_after_baseline(
            [make_event(message="открыта ключом Жена.")]
        )
        assert emitted[0]["key_name"] == "Жена"

    async def test_raw_message_is_not_propagated(self) -> None:
        emitted = await run_after_baseline([make_event()])
        # The operator text carries the key code and must not reach entities,
        # the recorder or diagnostics.
        assert "message" not in emitted[0]
        assert CODE not in str(emitted[0])

    async def test_unmatched_key_emits_without_key_name(self) -> None:
        emitted = await run_after_baseline(
            [make_event(message="Дверь открыта приложением")]
        )
        assert len(emitted) == 1
        assert "key_name" not in emitted[0]

    async def test_empty_index_still_emits_event(self) -> None:
        emitted = await run_after_baseline([make_event()], index={})
        # A failed key lookup degrades the event to anonymous rather than
        # dropping it.
        assert len(emitted) == 1
        assert "key_name" not in emitted[0]

    async def test_call_event_gets_no_key_attribute(self) -> None:
        emitted = await run_after_baseline(
            [make_event(event_type="accessControlCallAccepted", message="")]
        )
        assert emitted[0]["event_type"] == "call_accepted"
        assert "key_name" not in emitted[0]

    async def test_content_key_event_is_flagged(self) -> None:
        # The operator files these under billingSystem, so downstream needs to
        # know the identity came from the text.
        emitted = await run_after_baseline(
            [make_event(event_type="infoNotification", source_type="billingSystem",
                        source_id="18")]
        )
        assert emitted[0]["event_type"] == "key_activated"
        assert emitted[0]["by_content"] is True

    async def test_typed_key_event_is_not_flagged(self) -> None:
        emitted = await run_after_baseline([make_event()])
        assert emitted[0]["by_content"] is False
