"""Wire contracts and rejection cases; no HA installation or live account needed."""
import importlib.util
import json
import re
import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("standalone_app_api", ROOT / "custom_components/my_dom_ru/app_api.py")
app_api = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = app_api
spec.loader.exec_module(app_api)


def test_guest_pass_uses_verified_moshi_body():
    method, endpoint, raw = app_api.build_request("create_temp_pass", {
        "place_id": "12", "ttl": 3600, "access_control_ids": [45, "45", 46],
    })
    assert method == "POST"
    assert endpoint == "/api/mh-temp-pass/mobile/v1/rest/v1/temp-passes"
    assert json.loads(raw) == {"placeId": 12, "ttl": 3600, "accessControlIds": [45, 46]}


def test_delete_pass_keeps_required_delete_body():
    method, endpoint, raw = app_api.build_request("delete_temp_pass", {"place_id": 12, "pass_id": 8})
    assert method == "DELETE"
    assert endpoint.endswith("/temp-passes/8")
    assert json.loads(raw) == {"placeId": 12}


def test_ptz_parameters_are_query_not_body():
    method, endpoint, raw = app_api.build_request("camera_ptz", {
        "place_id": 12, "camera_id": 13, "direction": "left", "movement": "stop",
    })
    assert (method, endpoint, raw) == ("POST", "/rest/v1/places/12/cameras/13/ptz/rotate?direction=left&action=stop", None)


def test_event_recording_boolean_is_lowercase_path():
    assert app_api.build_request("camera_set_event_recording", {"place_id": 12, "camera_id": 13, "enabled": False}) == (
        "PUT", "/api/mh-camera-personal/mobile/v1/cameras/13/event-record-mode/false", None,
    )


def test_key_code_remains_in_json_body():
    method, url, body = app_api.build_request("add_access_key", {"place_id": 12, "key_code": 'ABC/../?token="&x=1'})
    assert method == "POST" and "ABC" not in url
    assert json.loads(body)["accessKeyCode"] == 'ABC/../?token="&x=1'


def test_maintenance_request_uses_apk_body_fields():
    method, endpoint, body = app_api.build_request("create_maintenance_request", {
        "place_id": 12, "phone": "+79990000000", "full_name": "Иван", "message": "Не работает домофон",
    })
    assert method == "POST"
    assert endpoint.endswith("/requests")
    assert json.loads(body) == {
        "phone": "+79990000000", "fio": "Иван", "message": "Не работает домофон", "placeId": 12,
    }


@pytest.mark.parametrize("bad", [True, False, 0, -1, 1.2, "../2", "1/2", "1?x=y", "https://evil.test", "１２", "", None, 2**63])
def test_invalid_identifiers_cannot_enter_url(bad):
    with pytest.raises(app_api.AppApiError):
        app_api.build_request("camera_audio_volumes", {"place_id": bad, "camera_id": 5})


@pytest.mark.parametrize("extra", [{"url": "https://example.com"}, {"headers": {"Authorization": "x"}}, {"token": "x"}])
def test_no_arbitrary_transport_escape(extra):
    with pytest.raises(app_api.AppApiError, match="invalid_fields"):
        app_api.build_request("list_access_keys", {"place_id": 1, **extra})


@pytest.mark.parametrize("name,values", [
    ("camera_set_recording", {"camera_id": 2, "mode": "continuous"}),
    ("camera_set_event_recording", {"camera_id": 2, "enabled": "false"}),
    ("create_temp_pass", {"ttl": True, "access_control_ids": [1]}),
    ("create_temp_pass", {"ttl": 10, "access_control_ids": []}),
    ("camera_set_microphone_volume", {"camera_id": 2, "volume": -1}),
    ("rename_access_key", {"key_id": 2, "name": "\n"}),
])
def test_invalid_values_fail_before_network(name, values):
    with pytest.raises(app_api.AppApiError):
        app_api.build_request(name, {"place_id": 1, **values})


def normalize_path(path):
    return re.sub(r"\{[^}]+\}", "{}", path)


@pytest.mark.parametrize("name", list(app_api.OPERATIONS))
def test_every_new_endpoint_method_and_payload_matches_apk_inventory(name):
    catalog = json.loads((ROOT / "docs/apk-api-9.10.0.json").read_text(encoding="utf-8"))["endpoints"]
    op = app_api.OPERATIONS[name]
    matches = [item for item in catalog if item["method"] == op.method and normalize_path(item["path"]) == normalize_path(op.path)]
    assert matches, (name, op.method, op.path)
    assert any(set(item["query_parameters"]) == {wire for _, wire in op.query} for item in matches)
    if op.body:
        assert any(set(item.get("body_fields", [])) == {wire for _, wire in op.body} for item in matches)


@pytest.mark.asyncio
@pytest.mark.parametrize("status,body,expected", [(204, b"", None), (200, b"", None), (200, b'{"data":[]}', {"data": []})])
async def test_response_empty_or_json_releases_connection(status, body, expected):
    response = Mock(status=status, content_length=None, read=AsyncMock(return_value=body))
    transport = Mock(get=AsyncMock(return_value=response))
    assert await app_api.AppApi(transport).execute("list_access_keys", {"place_id": 1}) == expected
    response.release.assert_called_once()


@pytest.mark.asyncio
async def test_malformed_response_is_safe_and_connection_released():
    response = Mock(status=200, content_length=None, read=AsyncMock(return_value=b"<html>secret</html>"))
    transport = Mock(get=AsyncMock(return_value=response))
    with pytest.raises(app_api.AppApiError, match="^invalid_response$"):
        await app_api.AppApi(transport).execute("list_access_keys", {"place_id": 1})
    response.release.assert_called_once()


@pytest.mark.asyncio
async def test_timeout_does_not_retry_mutation():
    transport = Mock(post=AsyncMock(side_effect=TimeoutError))
    with pytest.raises(TimeoutError):
        await app_api.AppApi(transport).execute("create_temp_pass", {"place_id": 1, "ttl": 60, "access_control_ids": [2]})
    transport.post.assert_awaited_once()
