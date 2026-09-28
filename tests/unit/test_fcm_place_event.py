"""Unit tests for the `placeEvent` FCM push parser."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "custom_components"))

from my_dom_ru.fcm import parse_place_event  # noqa: E402


def make_push(
    *,
    event_type: str = "accessKeyActivated",
    timestamp: object = "1777213000",
    message: str = "Адрес открыта ключом 098b987y",
    source_type: str = "accessControl",
    source_id: int = 101,
    place_id: int = 55,
    event_id: str = "26865176",
) -> str:
    """Build a push body shaped like the app's `placeEvent` payload."""
    return json.dumps(
        {
            "event": {
                "type": "placeEvent",
                "payload": {
                    "message": message,
                    "timestamp": timestamp,
                    "id": event_id,
                    "source": {"id": source_id, "type": source_type},
                    "placeId": place_id,
                    "eventTypeName": event_type,
                    "actions": None,
                },
            }
        }
    )


class TestParsePlaceEvent:
    def test_parses_key_activation(self) -> None:
        parsed = parse_place_event(make_push())
        assert parsed == {
            "event_type": "accessKeyActivated",
            "event_id": "26865176",
            "timestamp": 1777213000,
            "message": "Адрес открыта ключом 098b987y",
            "place_id": "55",
            "source_type": "accessControl",
            "source_id": "101",
        }

    def test_accepts_numeric_timestamp(self) -> None:
        # REST returns a JSON number, the push a JSON string. Both must work.
        parsed = parse_place_event(make_push(timestamp=1777213000))
        assert parsed is not None
        assert parsed["timestamp"] == 1777213000

    @pytest.mark.parametrize(
        "bad",
        [
            "",
            "not json",
            "[]",
            '"a string"',
            "null",
            "{}",
            '{"event": null}',
            '{"event": {"type": "other", "payload": {}}}',
            '{"event": {"type": "placeEvent"}}',
            '{"event": {"type": "placeEvent", "payload": "nope"}}',
        ],
    )
    def test_rejects_malformed(self, bad: str) -> None:
        assert parse_place_event(bad) is None

    def test_rejects_missing_required_fields(self) -> None:
        body = json.loads(make_push())
        del body["event"]["payload"]["eventTypeName"]
        assert parse_place_event(json.dumps(body)) is None

        body = json.loads(make_push())
        body["event"]["payload"]["source"] = {"id": 1}
        assert parse_place_event(json.dumps(body)) is None

    def test_rejects_unparseable_timestamp(self) -> None:
        assert parse_place_event(make_push(timestamp="не число")) is None

    def test_missing_message_becomes_empty_string(self) -> None:
        body = json.loads(make_push())
        del body["event"]["payload"]["message"]
        parsed = parse_place_event(json.dumps(body))
        assert parsed is not None
        assert parsed["message"] == ""

    def test_non_string_message_becomes_empty_string(self) -> None:
        parsed = parse_place_event(make_push(message=None))
        assert parsed is not None
        assert parsed["message"] == ""

    def test_numeric_event_id_is_stringified(self) -> None:
        parsed = parse_place_event(make_push(event_id=42))
        assert parsed is not None
        assert parsed["event_id"] == "42"

    def test_other_event_types_still_parse(self) -> None:
        # cameraMoving and friends are consumed here (and ignored) rather than
        # falling through to the call-channel mapping.
        parsed = parse_place_event(make_push(event_type="cameraMoving"))
        assert parsed is not None
        assert parsed["event_type"] == "cameraMoving"
