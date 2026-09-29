"""Diagnostics for access events must never log the operator's text.

The event `message` embeds the access key code. Debug logging is exactly what
a user turns on to work out why a key activation did not surface, so this is
the most likely moment for that code to leak into home-assistant.log — a file
users routinely paste into issues.

These tests pin the property on the log records themselves rather than on the
call sites, so a future edit to the format string cannot quietly reintroduce a
leak.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "custom_components"))

from my_dom_ru.api import HistoryEvent, HistoryPage  # noqa: E402
from my_dom_ru.const import EVENT_KEY_ACTIVATED  # noqa: E402
from my_dom_ru.history import (  # noqa: E402
    HistoryPoller,
    HistoryWatermark,
    map_general_event_type,
)

CODE = "454e6fb3"
MESSAGE = f"Адрес открыта ключом {CODE}"

# The integration's LOGGER is defined in const.py, so its name is not
# `my_dom_ru.history`. Target the whole package to be safe against that.
LOGGER_NAME = "my_dom_ru"


class FakeApi:
    def __init__(self, events: list[HistoryEvent]) -> None:
        self._events = events

    async def query_events(self, place_ids, page: int = 0) -> HistoryPage:
        return HistoryPage(events=tuple(self._events), number=0, last=True)

    async def query_camera_events(self, camera_id, lower_date, upper_date):
        return ()


class FakeCoordinator:
    def __init__(self, events, key_names=""):
        self.data = {"places": [{"place": {"id": 55}}], "cameras": []}
        self.api = FakeApi(events)
        self.entry_options_snapshot = {"key_names": key_names}


def key_event(**overrides: Any) -> HistoryEvent:
    base: dict[str, Any] = {
        "id": "e1",
        "place_id": "55",
        "event_type": "accessKeyActivated",
        "timestamp": 1777213000,
        "source_type": "accessControl",
        "source_id": "101",
        "message": MESSAGE,
    }
    base.update(overrides)
    return HistoryEvent(**base)


@pytest.fixture
def records(caplog):
    """Return a callable that reads the records logged *so far*.

    `caplog.records` is a snapshot property, so returning it directly from a
    fixture would capture an empty list at setup time, before the test body
    has produced anything.
    """

    def read() -> list[logging.LogRecord]:
        return [
            record
            for record in caplog.records
            if record.name == LOGGER_NAME
            or record.name.startswith(f"{LOGGER_NAME}.")
        ]

    caplog.set_level(logging.DEBUG, logger=LOGGER_NAME)
    return read


def blob_of(records) -> str:
    return "\n".join(record.getMessage() for record in records())


async def run(events, key_names=""):
    from my_dom_ru.access_keys import parse_key_names

    # Seed the stream each event actually belongs to. A stream with no prior
    # watermark is a *silent baseline* and yields nothing, so seeding the wrong
    # key would silently turn every "new event" case into a no-op.
    streams = {
        f"general:{event.place_id}:{event.source_type}:{event.source_id}": ["seed"]
        for event in events
    }
    emitted: list[dict[str, Any]] = []
    poller = HistoryPoller(
        FakeCoordinator(events, key_names),
        HistoryWatermark(streams),
        emitted.append,
        key_names=lambda: parse_key_names(key_names),
    )
    await poller.async_poll()
    return emitted


class TestDebugLoggingDoesNotLeak:
    @pytest.mark.asyncio
    async def test_poller_logs_never_contain_the_code(self, records) -> None:
        await run([key_event()], f"{CODE} = Денис")
        assert records(), "expected diagnostic records"
        blob = blob_of(records)
        assert CODE not in blob
        assert CODE.upper() not in blob
        # The message text itself must not appear either.
        assert MESSAGE not in blob

    @pytest.mark.asyncio
    async def test_unmatched_key_logs_the_reason(self, records) -> None:
        # NO_LABEL_MATCH tells the user the mapping failed, without saying
        # which code failed to match.
        await run([key_event()], "OTHERCODE = Денис")
        blob = blob_of(records)
        assert "NO_LABEL_MATCH" in blob
        assert CODE not in blob

    @pytest.mark.asyncio
    async def test_matched_key_logs_the_label(self, records) -> None:
        await run([key_event()], f"{CODE} = Денис")
        blob = blob_of(records)
        assert "Денис" in blob
        assert CODE not in blob

    @pytest.mark.asyncio
    async def test_poll_success_is_logged(self, records) -> None:
        # Distinguishes "poll failed" from "poll returned nothing", which are
        # otherwise indistinguishable from the UI.
        await run([key_event()])
        assert "History poll ok" in blob_of(records)

    @pytest.mark.asyncio
    async def test_backend_type_and_source_are_logged(self, records) -> None:
        # The fields needed to fix ownership matching when a key activation
        # arrives but no entity claims it.
        await run([key_event(source_type="mystery", source_id="777")])
        blob = blob_of(records)
        assert "mystery" in blob
        assert "777" in blob
        assert "accessKeyActivated" in blob

    @pytest.mark.asyncio
    async def test_unmapped_backend_type_is_still_logged(self, records) -> None:
        # Seeing a type we do not map is how a missing feature gets noticed.
        await run([key_event(event_type="someNewType")])
        blob = blob_of(records)
        assert "someNewType" in blob
        assert "mapped=-" in blob


class TestMappingUnchanged:
    def test_key_activation_still_maps(self) -> None:
        assert map_general_event_type("accessKeyActivated") == EVENT_KEY_ACTIVATED

    @pytest.mark.asyncio
    async def test_unmapped_type_is_not_emitted(self) -> None:
        # The diagnostic must not change behaviour: an unknown type is logged
        # and still dropped.
        assert await run([key_event(event_type="someNewType")]) == []
