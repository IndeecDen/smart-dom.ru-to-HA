"""Unit tests for the `placeEvent` FCM push parser."""
from __future__ import annotations

import json
import sys
from unittest.mock import MagicMock, patch
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


class TestHandlePlaceEvent:
    """The handler that turns a parsed push into a dispatched payload.

    `parse_place_event` was well covered while the handler around it was not,
    and that gap let a live bug through: `by_content` was only assigned inside
    the `by_type` branch, so the common path — a key opening arriving as
    `infoNotification` — raised UnboundLocalError *after* the event had been
    recognised, and was then dropped on the floor.
    """

    KEYS = [{"id": 1, "accessKey": {"accessKeyCode": "5034 0C4B", "name": "Денис"}}]

    def make_listener(self, keys=None):
        from my_dom_ru.access_keys import build_key_index
        from my_dom_ru.fcm import DoorbellFcmListener

        listener = DoorbellFcmListener.__new__(DoorbellFcmListener)
        listener._hass = MagicMock()
        listener._key_index = {"55": build_key_index(keys)} if keys else {}
        dispatched: list[tuple[str, dict]] = []
        return listener, dispatched

    def handle(self, listener, dispatched, push: str) -> bool:
        with patch(
            "my_dom_ru.fcm.async_dispatcher_send",
            side_effect=lambda hass, signal, payload: dispatched.append(
                (signal, payload)
            ),
        ):
            return listener._async_handle_place_event({"u": push})

    def test_info_notification_with_a_key_becomes_key_activated(self) -> None:
        from my_dom_ru.const import EVENT_KEY_ACTIVATED, SIGNAL_ACCESS_KEY

        listener, dispatched = self.make_listener(self.KEYS)
        self.handle(
            listener,
            dispatched,
            make_push(
                event_type="infoNotification",
                source_type="billingSystem",
                source_id=18,
                message="30 Лет Октября 6 (п. 3) открыта ключом Денис.",
            ),
        )
        assert len(dispatched) == 1
        signal, payload = dispatched[0]
        assert signal == SIGNAL_ACCESS_KEY
        assert payload["event_type"] == EVENT_KEY_ACTIVATED
        assert payload["key_name"] == "Денис"
        # The regression: this flag was unset on the content path.
        assert payload["by_content"] is True

    def test_typed_key_event_is_not_flagged_as_content(self) -> None:
        listener, dispatched = self.make_listener(self.KEYS)
        self.handle(
            listener,
            dispatched,
            make_push(message="открыта ключом Денис", source_id=101),
        )
        assert dispatched[0][1]["by_content"] is False

    def test_unknown_event_without_a_key_is_ignored(self) -> None:
        listener, dispatched = self.make_listener(self.KEYS)
        assert self.handle(
            listener,
            dispatched,
            make_push(event_type="billingNotification", message="Счёт выставлен"),
        )
        assert dispatched == []

    def test_raw_text_never_reaches_the_payload(self) -> None:
        listener, dispatched = self.make_listener(self.KEYS)
        self.handle(
            listener,
            dispatched,
            make_push(event_type="infoNotification",
                      message="открыта ключом Денис"),
        )
        # The operator text embeds the address; it must not reach the recorder.
        assert "message" not in dispatched[0][1]
        assert "30 Лет" not in str(dispatched[0][1])

    def test_missing_event_push_is_left_to_the_call_channel(self) -> None:
        listener, dispatched = self.make_listener(self.KEYS)
        assert listener._async_handle_place_event({}) is False
        assert dispatched == []

