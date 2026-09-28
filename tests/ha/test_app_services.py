"""Use real HA service registration, with an offline operator transport."""
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import (
    HomeAssistantError,
    ServiceValidationError,
    Unauthorized,
)

from custom_components.my_dom_ru.app_api import AppApiError
from custom_components.my_dom_ru.app_services import (
    _validate_scope,
    async_register_app_services,
)


@pytest.fixture
def coordinator():
    return SimpleNamespace(data={"places": [{"place": {"id": 10}}]}, api=SimpleNamespace(
        query_cameras=AsyncMock(return_value=[{"id": 20, "externalCameraId": 999}]),
        query_access_controls=AsyncMock(return_value=[{"id": 30}]),
        http=Mock(),
    ))


@pytest.mark.asyncio
async def test_camera_scope_rejects_external_forpost_id(coordinator):
    with pytest.raises(AppApiError, match="personal_camera_not_found"):
        await _validate_scope(coordinator, "camera_set_recording", {"place_id": 10, "camera_id": 999, "mode": "off"}, Mock())


@pytest.mark.asyncio
async def test_account_scope_rejects_other_place_without_http(coordinator):
    with pytest.raises(AppApiError, match="place_not_in_account"):
        await _validate_scope(coordinator, "camera_set_recording", {"place_id": 999, "camera_id": 20, "mode": "off"}, Mock())
    coordinator.api.query_cameras.assert_not_called()


@pytest.mark.asyncio
async def test_pass_lifetime_and_doors_checked(coordinator):
    api = Mock(execute=AsyncMock(side_effect=[[60], [{"id": 30}]]))
    with pytest.raises(AppApiError, match="access_control_not_allowed"):
        await _validate_scope(coordinator, "create_temp_pass", {"place_id": 10, "ttl": 60, "access_control_ids": [999]}, api)
    assert api.execute.await_count == 2


@pytest.mark.asyncio
async def test_sensitivity_bound_checked_before_put(coordinator):
    api = Mock(execute=AsyncMock(return_value={"data": {"minSensitivityValue": 1, "maxSensitivityValue": 5}}))
    with pytest.raises(AppApiError, match="sensitivity_out_of_range"):
        await _validate_scope(coordinator, "camera_set_sensitivity", {"place_id": 10, "camera_id": 20, "sensitivity": 10}, api)


@pytest.mark.asyncio
async def test_admin_service_returns_result_and_survives_entry_unload(tmp_path, coordinator):
    hass = HomeAssistant(str(tmp_path))
    async_register_app_services(hass)
    with patch("custom_components.my_dom_ru.app_services.async_get_coordinator", return_value=coordinator), patch(
        "custom_components.my_dom_ru.app_services.AppApi.execute", new=AsyncMock(return_value=[{"id": 3}]),
    ):
        result = await hass.services.async_call("my_dom_ru", "list_access_keys", {"config_entry_id": "account", "place_id": 10}, blocking=True, return_response=True)
        assert result == {"result": [{"id": 3}]}
    with patch("custom_components.my_dom_ru.app_services.async_get_coordinator", return_value=None):
        with pytest.raises(ServiceValidationError, match="не загружена"):
            await hass.services.async_call("my_dom_ru", "list_access_keys", {"config_entry_id": "account", "place_id": 10}, blocking=True, return_response=True)
    await hass.async_stop()


@pytest.mark.asyncio
async def test_non_admin_cannot_manage_passes(tmp_path, coordinator):
    hass = HomeAssistant(str(tmp_path))
    hass.auth = SimpleNamespace(async_get_user=AsyncMock(return_value=SimpleNamespace(is_admin=False)))
    async_register_app_services(hass)
    with patch.object(hass.auth, "async_get_user", new=AsyncMock(return_value=SimpleNamespace(is_admin=False))), patch(
        "custom_components.my_dom_ru.app_services.async_get_coordinator", return_value=coordinator,
    ):
        with pytest.raises(Unauthorized):
            await hass.services.async_call("my_dom_ru", "list_access_keys", {"config_entry_id": "account", "place_id": 10}, blocking=True, return_response=True, context=Context(user_id="non_admin"))
    await hass.async_stop()


@pytest.mark.asyncio
async def test_network_error_is_sanitized_without_exception_chain(tmp_path, coordinator):
    hass = HomeAssistant(str(tmp_path))
    async_register_app_services(hass)
    with patch("custom_components.my_dom_ru.app_services.async_get_coordinator", return_value=coordinator), patch(
        "custom_components.my_dom_ru.app_services.AppApi.execute", new=AsyncMock(side_effect=TimeoutError("secret-token")),
    ):
        with pytest.raises(HomeAssistantError) as exc:
            await hass.services.async_call("my_dom_ru", "list_access_keys", {"config_entry_id": "account", "place_id": 10}, blocking=True, return_response=True)
        assert "secret-token" not in str(exc.value)
        assert exc.value.__suppress_context__
    await hass.async_stop()
