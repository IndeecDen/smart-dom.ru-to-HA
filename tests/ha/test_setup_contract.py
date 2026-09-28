"""Lifecycle smoke checks against the installed Home Assistant API."""
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from homeassistant.core import HomeAssistant

from custom_components.my_dom_ru import async_setup, async_update_options
from custom_components.my_dom_ru.app_api import OPERATIONS


@pytest.mark.asyncio
async def test_setup_registers_sip_and_all_extra_services(tmp_path):
    hass = HomeAssistant(str(tmp_path))
    assert await async_setup(hass, {})
    assert all(hass.services.has_service("my_dom_ru", name) for name in ["answer", "hangup", "get_inventory", *OPERATIONS])
    await hass.async_stop()


@pytest.mark.asyncio
async def test_token_rotation_does_not_reload_running_call():
    reload = AsyncMock()
    coordinator = SimpleNamespace(entry_options_snapshot={"use_go2rtc": True}, entry_non_token_snapshot={"account": 1})
    entry = SimpleNamespace(entry_id="entry", runtime_data=coordinator,
        options={"use_go2rtc": True}, data={"account": 1, "access_token": "new", "refresh_token": "new"})
    hass = SimpleNamespace(data={}, config_entries=SimpleNamespace(async_reload=reload))
    await async_update_options(hass, entry)
    reload.assert_not_awaited()
    entry.data["fcm_credentials"] = {"token": "rotated"}
    await async_update_options(hass, entry)
    reload.assert_not_awaited()


@pytest.mark.asyncio
async def test_option_change_still_reloads():
    reload = AsyncMock()
    coordinator = SimpleNamespace(entry_options_snapshot={"use_go2rtc": False}, entry_non_token_snapshot={"account": 1})
    entry = SimpleNamespace(entry_id="entry", runtime_data=coordinator,
        options={"use_go2rtc": True}, data={"account": 1})
    hass = SimpleNamespace(data={}, config_entries=SimpleNamespace(async_reload=reload))
    await async_update_options(hass, entry)
    reload.assert_awaited_once_with("entry")
