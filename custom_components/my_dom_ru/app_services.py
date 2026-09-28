"""Home Assistant actions for application features beyond intercom streaming."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from aiohttp import ClientError
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.service import async_register_admin_service

from .app_api import (
    OPERATIONS,
    AppApi,
    AppApiError,
    positive_id,
    unwrap,
    validate_values,
)
from .const import DOMAIN
from .coordinator import async_get_coordinator
from .http import error_status


def _service_schema(operation: str) -> vol.Schema:
    op = OPERATIONS[operation]
    fields = {"place_id", *op.fields}
    if op.camera:
        fields.add("camera_id")
    validators = {
        "enabled": cv.boolean,
        "access_control_ids": [vol.All(vol.Coerce(int), vol.Range(min=1))],
        "mode": vol.In(("on", "off")),
        "axis": vol.In(("vertical", "horizontal")),
        "direction": vol.In(("up", "down", "left", "right")),
        "movement": vol.In(("start", "stop")),
    }
    schema: dict[Any, Any] = {vol.Required("config_entry_id"): cv.string}
    for field in fields:
        if field in validators:
            validator = validators[field]
        elif field.endswith("_id") or field in ("ttl", "page", "volume", "sensitivity"):
            validator = vol.All(vol.Coerce(int), vol.Range(min=0 if field in ("page", "volume", "sensitivity") else 1))
        else:
            validator = cv.string
        schema[vol.Required(field, default=0) if field == "page" else vol.Required(field)] = validator
    return vol.Schema(schema)


async def _validate_scope(coordinator: Any, name: str, values: dict[str, Any], api: AppApi) -> None:
    """Fail closed on an account/place/camera mismatch before sending a mutation."""
    place_id = values["place_id"]
    places = (coordinator.data or {}).get("places", [])
    if not any(str(item.get("place", {}).get("id")) == str(place_id) for item in places):
        raise AppApiError("place_not_in_account")
    if OPERATIONS[name].camera:
        # /places/.../cameras uses the internal ID, not forpost externalCameraId.
        cameras = await coordinator.api.query_cameras(str(place_id))
        if not any(str(cam.get("id")) == str(values["camera_id"]) for cam in cameras or []):
            raise AppApiError("personal_camera_not_found")
    if name == "create_temp_pass":
        lifetimes = unwrap(await api.execute("temp_pass_lifetimes", {"place_id": place_id}))
        options = unwrap(await api.execute("temp_pass_options", {"place_id": place_id}))
        if not isinstance(lifetimes, list) or values["ttl"] not in lifetimes:
            raise AppApiError("ttl_not_supported")
        allowed = {str(item.get("id")) for item in options or [] if isinstance(item, dict)}
        if not all(str(item) in allowed for item in values["access_control_ids"]):
            raise AppApiError("access_control_not_allowed")
    if name == "delete_temp_pass":
        passes = unwrap(await api.execute("list_temp_passes", {"place_id": place_id}))
        if not any(str(item.get("id")) == str(values["pass_id"]) for item in passes or []):
            raise AppApiError("pass_not_in_place")
    if name == "acknowledge_document":
        documents = unwrap(await api.execute("list_documents", {"place_id": place_id}))
        if not any(str(item.get("id")) == str(values["document_id"]) for item in documents or []):
            raise AppApiError("document_not_in_place")
    if "key_id" in values:
        keys = unwrap(await api.execute("list_access_keys", {"place_id": place_id}))
        if not any(str(item.get("id")) == str(values["key_id"]) for item in keys or []):
            raise AppApiError("key_not_in_place")
    if name == "camera_set_sensitivity":
        settings = unwrap(await api.execute("camera_motion_parameters", {
            "place_id": place_id, "camera_id": values["camera_id"],
        }))
        if not isinstance(settings, dict) or not all(k in settings for k in ("minSensitivityValue", "maxSensitivityValue")):
            raise AppApiError("sensitivity_range_unavailable")
        if not settings["minSensitivityValue"] <= values["sensitivity"] <= settings["maxSensitivityValue"]:
            raise AppApiError("sensitivity_out_of_range")
    if name in ("camera_set_microphone_volume", "camera_set_speaker_volume"):
        settings = unwrap(await api.execute("camera_audio_volumes", {
            "place_id": place_id, "camera_id": values["camera_id"],
        }))
        key = "microphoneVolumeRange" if "microphone" in name else "speakerVolumeRange"
        if not isinstance(settings, dict) or values["volume"] not in settings.get(key, []):
            raise AppApiError("volume_not_supported")


def async_register_app_services(hass: HomeAssistant) -> None:
    """Register once at async_setup; no account-dependent closure is retained."""

    async def handle(call: ServiceCall) -> dict[str, Any]:
        coordinator = async_get_coordinator(hass, call.data["config_entry_id"])
        if coordinator is None:
            raise ServiceValidationError("Запись «Умный Дом.ру» не загружена")
        values = {key: value for key, value in call.data.items() if key != "config_entry_id"}
        try:
            values = validate_values(call.service, values)
            api = AppApi(coordinator.api.http)
            await _validate_scope(coordinator, call.service, values, api)
            result = await api.execute(call.service, values)
        except AppApiError as err:
            raise ServiceValidationError(str(err)) from None
        except (ClientError, TimeoutError) as err:
            status = error_status(err)
            if status == 401:
                entry = hass.config_entries.async_get_entry(call.data["config_entry_id"])
                if entry is not None:
                    entry.async_start_reauth(hass)
            # Never chain a response exception containing URLs or a key code.
            raise HomeAssistantError(f"Ошибка API Дом.ру ({status or 'соединение'}). Команда не повторялась.") from None
        return {"result": result}

    async def inventory(call: ServiceCall) -> dict[str, Any]:
        coordinator = async_get_coordinator(hass, call.data["config_entry_id"])
        if coordinator is None:
            raise ServiceValidationError("Запись «Умный Дом.ру» не загружена")
        places = []
        try:
            for item in (coordinator.data or {}).get("places", []):
                place_id = positive_id(item["place"]["id"])
                cameras = await coordinator.api.query_cameras(str(place_id))
                controls = await coordinator.api.query_access_controls(str(place_id))
                places.append({
                    "place_id": place_id,
                    "personal_cameras": [{"camera_id": cam.get("id"), "name": cam.get("name")} for cam in cameras or []],
                    "access_controls": [{"access_control_id": ac.get("id"), "name": ac.get("name")} for ac in controls or []],
                })
        except (ClientError, TimeoutError, AppApiError):
            raise HomeAssistantError("Не удалось получить устройства Дом.ру") from None
        return {"places": places}

    for name, op in OPERATIONS.items():
        async_register_admin_service(
            hass, DOMAIN, name, handle, schema=_service_schema(name),
            supports_response=SupportsResponse.ONLY if op.method == "GET" else SupportsResponse.OPTIONAL,
        )
    async_register_admin_service(
        hass, DOMAIN, "get_inventory", inventory,
        schema=vol.Schema({vol.Required("config_entry_id"): cv.string}),
        supports_response=SupportsResponse.ONLY,
    )
