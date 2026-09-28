"""Additional 9.10.0 API contracts, verified against Retrofit/Moshi in the APK.

This module has no HA dependency so validation and wire contracts can be tested
without a running installation. It never accepts a caller-provided URL.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode


class AppApiError(Exception):
    """A safe error, without upstream URLs, bodies or access codes."""


@dataclass(frozen=True)
class Operation:
    method: str
    path: str
    fields: tuple[str, ...] = ()
    query: tuple[tuple[str, str], ...] = ()
    body: tuple[tuple[str, str], ...] = ()
    camera: bool = False


CAMERA = "/rest/v1/places/{place_id}/cameras/{camera_id}"
PERSONAL = "/api/mh-camera-personal/mobile/v1"
PASSES = "/api/mh-temp-pass/mobile/v1/rest/v1/temp-passes"
KEYS = "/api/mh-access-key/mobile/v1/rest/v1/access-keys"
PLACE_QUERY = (("place_id", "placeId"),)

# Fields are HA names; wire names come from the application's JSON adapters.
OPERATIONS: dict[str, Operation] = {
    "list_temp_passes": Operation("GET", PASSES, query=PLACE_QUERY),
    "temp_pass_options": Operation("GET", PASSES + "/access-controls", query=PLACE_QUERY),
    "temp_pass_lifetimes": Operation("GET", PASSES + "/time-to-life", query=PLACE_QUERY),
    "create_temp_pass": Operation("POST", PASSES, ("ttl", "access_control_ids"),
        body=(("place_id", "placeId"), ("ttl", "ttl"), ("access_control_ids", "accessControlIds"))),
    "delete_temp_pass": Operation("DELETE", PASSES + "/{pass_id}", ("pass_id",),
        body=PLACE_QUERY),
    "list_access_keys": Operation("GET", KEYS, query=PLACE_QUERY),
    "add_access_key": Operation("POST", KEYS, ("key_code",),
        body=(("key_code", "accessKeyCode"), ("place_id", "placeId"))),
    "delete_access_key": Operation("DELETE", KEYS, ("key_id", "key_code"),
        body=(("key_id", "customerServiceId"), ("place_id", "placeId"), ("key_code", "accessKeyCode"))),
    "reactivate_access_key": Operation("POST", KEYS + "/{key_id}/reactivate", ("key_id", "key_code"),
        body=(("key_code", "accessKeyCode"), ("place_id", "placeId"))),
    "rename_access_key": Operation("PUT", KEYS + "/{key_id}/rename", ("key_id", "name"),
        body=(("name", "name"),)),
    # This is a toggle in the APK, not an idempotent set(on/off) operation.
    "toggle_key_notifications": Operation("PUT", KEYS + "/{key_id}/notification-status", ("key_id",)),
    "camera_motion_parameters": Operation("GET", CAMERA + "/motionDetectionParameters", camera=True),
    "camera_set_sensitivity": Operation("PUT", CAMERA + "/sensitivity/{sensitivity}", ("sensitivity",), camera=True),
    "camera_set_recording": Operation("PUT", CAMERA + "/recordmode/{mode}", ("mode",), camera=True),
    "camera_set_event_recording": Operation("PUT", PERSONAL + "/cameras/{camera_id}/event-record-mode/{enabled}", ("enabled",), camera=True),
    "camera_rename": Operation("PUT", CAMERA, ("name",), body=(("name", "name"),), camera=True),
    "camera_mirror": Operation("PUT", CAMERA + "/mirror/{axis}", ("axis",), camera=True),
    "camera_ptz": Operation("POST", CAMERA + "/ptz/rotate", ("direction", "movement"),
        query=(("direction", "direction"), ("movement", "action")), camera=True),
    "camera_audio_volumes": Operation("GET", PERSONAL + CAMERA + "/audioVolumes", camera=True),
    "camera_set_microphone_volume": Operation("PUT", PERSONAL + CAMERA + "/microphoneVolumes/{volume}", ("volume",), camera=True),
    "camera_set_speaker_volume": Operation("PUT", PERSONAL + CAMERA + "/speakerVolumes/{volume}", ("volume",), camera=True),
    "camera_features": Operation("GET", "/api/mh-camera/mobile/v1/places/{place_id}/cameras/features/info"),
    "get_finances": Operation("GET", "/api/mh-payment/mobile/v1/finance", query=PLACE_QUERY),
    "list_requests": Operation("GET", "/api/mh-technical-request/mobile/v1/requests", ("page",),
        query=PLACE_QUERY + (("page", "page"),)),
    "create_maintenance_request": Operation("POST", "/api/mh-technical-request/mobile/v1/requests",
        ("phone", "full_name", "message"),
        body=(("phone", "phone"), ("full_name", "fio"), ("message", "message"), ("place_id", "placeId"))),
    "list_documents": Operation("GET", "/api/mh-documents/mobile/v1/documents", query=PLACE_QUERY),
    "acknowledge_document": Operation("PUT", "/api/mh-documents/mobile/v1/documents/{document_id}", ("document_id",)),
    "get_screen_sections": Operation("GET", "/rest/v1/places/{place_id}/screen-sections"),
}


def positive_id(value: Any) -> int:
    """Reject booleans, traversal, floating-point and non-positive IDs."""
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise AppApiError("invalid_id")
    if not str(value).isascii() or not str(value).isdigit():
        raise AppApiError("invalid_id")
    result = int(value)
    if result < 1 or result > 2**63 - 1:
        raise AppApiError("invalid_id")
    return result


def _integer(value: Any, minimum: int = 0, maximum: int = 2**31 - 1) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise AppApiError("invalid_integer")
    return value


def validate_values(name: str, supplied: dict[str, Any]) -> dict[str, Any]:
    """Validate a complete operation before starting any network operation."""
    if name not in OPERATIONS:
        raise AppApiError("unknown_operation")
    op = OPERATIONS[name]
    required = {"place_id", *op.fields}
    if op.camera:
        required.add("camera_id")
    if set(supplied) != required:
        raise AppApiError("invalid_fields")
    values = dict(supplied)
    for field in required:
        value = values[field]
        if field.endswith("_id"):
            values[field] = positive_id(value)
        elif field in ("ttl", "page", "volume", "sensitivity"):
            values[field] = _integer(value, minimum=1 if field == "ttl" else 0)
        elif field == "access_control_ids":
            if not isinstance(value, list) or not 1 <= len(value) <= 100:
                raise AppApiError("invalid_access_controls")
            values[field] = list(dict.fromkeys(positive_id(item) for item in value))
        elif field in ("name", "key_code", "phone", "full_name", "message"):
            max_length = 4000 if field == "message" else 128
            if not isinstance(value, str) or not value.strip() or len(value) > max_length:
                raise AppApiError("invalid_text")
            if any(ord(char) < 32 for char in value):
                raise AppApiError("invalid_text")
        elif field == "enabled":
            if type(value) is not bool:
                raise AppApiError("invalid_boolean")
        else:
            allowed = {
                "mode": ("on", "off"), "axis": ("vertical", "horizontal"),
                "direction": ("up", "down", "left", "right"),
                "movement": ("start", "stop"),
            }
            if value not in allowed[field]:
                raise AppApiError("invalid_choice")
    return values


def build_request(name: str, supplied: dict[str, Any]) -> tuple[str, str, str | None]:
    """Build one allowlisted wire request. No arbitrary URL or body is accepted."""
    values = validate_values(name, supplied)
    op = OPERATIONS[name]
    path_values = {k: str(v).lower() if type(v) is bool else v for k, v in values.items()}
    endpoint = op.path.format_map(path_values)
    if op.query:
        endpoint += "?" + urlencode({wire: values[key] for key, wire in op.query})
    body = json.dumps({wire: values[key] for key, wire in op.body}) if op.body else None
    return op.method, endpoint, body


class AppApi:
    """Typed extra operations over the integration's authenticated transport."""

    def __init__(self, http: Any) -> None:
        self.http = http

    async def execute(self, name: str, supplied: dict[str, Any]) -> Any:
        method, endpoint, body = build_request(name, supplied)
        if method == "GET":
            response = await self.http.get(endpoint)
        else:
            response = await getattr(self.http, method.lower())(endpoint, body)
        try:
            if response.status == 204 or response.content_length == 0:
                return None
            raw = await response.read()
            if not raw.strip():
                return None
            try:
                return json.loads(raw)
            except (ValueError, UnicodeError):
                raise AppApiError("invalid_response") from None
        finally:
            response.release()


def unwrap(payload: Any) -> Any:
    """Unwrap the application's optional ResponseRaw envelope."""
    return payload.get("data") if isinstance(payload, dict) and "data" in payload else payload
