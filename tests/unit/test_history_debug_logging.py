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
from datetime import UTC, datetime, timedelta
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


def now() -> int:
    """Current epoch seconds.

    A key is only recognised as a fresh opening inside _KEY_LOOKBACK, so a
    hardcoded timestamp from when the test was written would age out and start
    failing for reasons unrelated to what is being tested.
    """
    return int(datetime.now(UTC).timestamp())

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
        "timestamp": now(),
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
        key_index=lambda: parse_key_names(key_names),
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
    async def test_unmapped_backend_type_is_still_surfaced(self, records) -> None:
        # Seeing a type we do not map is how a missing feature gets noticed.
        # Unmapped types are skipped before the watermark, so they no longer
        # produce a per-event line; they are summarised instead, once per poll.
        await run([key_event(event_type="someNewType")])
        blob = blob_of(records)
        assert "unmapped backend type" in blob
        assert "someNewType" in blob
        # Still no per-event record for something we do not act on.
        assert "History event" not in blob

    @pytest.mark.asyncio
    async def test_unmapped_summary_keeps_the_message_out(self, records) -> None:
        await run([key_event(event_type="someNewType")], f"{CODE} = Денис")
        blob = blob_of(records)
        assert CODE not in blob
        assert MESSAGE not in blob


class TestKeyDetectionIsBoundedInTime:
    """A key named in an old message is history, not a fresh opening.

    Without the bound, configuring labels would replay every retained
    notification in one burst the next time the poller ran.
    """

    @pytest.mark.asyncio
    async def test_recent_key_message_is_acted_on(self, records) -> None:
        await run([key_event()], f"{CODE} = Денис")
        assert "resolved=Денис" in blob_of(records)

    @pytest.mark.asyncio
    async def test_stale_key_message_is_not_acted_on(self, records) -> None:
        stale = key_event(
            timestamp=now() - int(timedelta(minutes=45).total_seconds())
        )
        await run([stale], f"{CODE} = Денис")
        blob = blob_of(records)
        assert "Денис" not in blob

    @pytest.mark.asyncio
    async def test_stale_message_of_a_mapped_type_still_maps(self) -> None:
        # The bound only suppresses the content-based *key* interpretation.
        # A real call event from yesterday is still a real call event.
        stale = key_event(
            event_type="accessControlCallMissed",
            timestamp=now() - int(timedelta(hours=3).total_seconds()),
        )
        emitted = await run([stale], f"{CODE} = Денис")
        assert [item["event_type"] for item in emitted] == ["call_missed"]


class TestMappingUnchanged:
    def test_key_activation_still_maps(self) -> None:
        assert map_general_event_type("accessKeyActivated") == EVENT_KEY_ACTIVATED

    @pytest.mark.asyncio
    async def test_unmapped_type_is_not_emitted(self) -> None:
        # The diagnostic must not change behaviour: an unknown type is logged
        # and still dropped.
        assert await run([key_event(event_type="someNewType")]) == []


class TestUnmappedTypesAreNotBurned:
    """Regression: an unmapped type must not be recorded as already seen.

    0.1.0 ingested every event id into the watermark and *then* dropped the
    types it did not map. `accessKeyActivated` had no mapping, so its id was
    remembered and the event discarded — permanently, since a later poll saw
    an already-seen id. Adding the mapping afterwards could never surface it,
    which is exactly why a real key opening never appeared in Home Assistant.
    """

    @pytest.mark.asyncio
    async def test_unmapped_event_stays_new_across_polls(self) -> None:
        event = key_event(event_type="someNewType")
        # Seeded so the first poll has a baseline, mirroring a running system.
        watermark = HistoryWatermark({"general:55:accessControl:101": ["seed"]})

        poller = HistoryPoller(
            FakeCoordinator([event]),
            watermark,
            lambda payload: None,
        )
        await poller.async_poll()
        # The id must not have been remembered.
        assert "e1" not in watermark._seen["general:55:accessControl:101"]

    @pytest.mark.asyncio
    async def test_newly_mapped_type_surfaces_its_history(self) -> None:
        # Simulates the upgrade path: the id was never burned, so once a
        # mapping exists the event is treated as new and emitted.
        event = key_event(event_type="accessKeyActivated")
        watermark = HistoryWatermark({"general:55:accessControl:101": ["seed"]})
        emitted: list[dict[str, Any]] = []

        poller = HistoryPoller(
            FakeCoordinator([event]),
            watermark,
            emitted.append,
        )
        await poller.async_poll()
        assert [item["event_type"] for item in emitted] == ["key_activated"]

    @pytest.mark.asyncio
    async def test_mapped_type_is_still_deduplicated(self) -> None:
        # The fix must not turn every poll into a replay.
        event = key_event()
        emitted: list[dict[str, Any]] = []
        coordinator = FakeCoordinator([event])

        first = HistoryPoller(
            coordinator,
            HistoryWatermark({"general:55:accessControl:101": ["seed"]}),
            emitted.append,
        )
        await first.async_poll()

        second = HistoryPoller(
            coordinator,
            first._watermark,
            emitted.append,
        )
        await second.async_poll()
        assert len(emitted) == 1
