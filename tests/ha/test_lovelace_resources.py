"""Card registration against HA's real, lazily loaded resource collection."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from homeassistant.components.lovelace.const import LOVELACE_DATA
from homeassistant.components.lovelace.dashboard import LovelaceStorage
from homeassistant.components.lovelace.resources import (
    ResourceStorageCollection,
    ResourceYAMLCollection,
)
from homeassistant.core import HomeAssistant

from custom_components.my_dom_ru.lovelace import async_register_card_resources
from custom_components.my_dom_ru.uplink_ws import (
    CALL_CARD_URL,
    CARD_URL,
    async_register_uplink_card,
)

URLS = (CALL_CARD_URL, CARD_URL)


@pytest_asyncio.fixture
async def card_hass(tmp_path):
    hass = HomeAssistant(str(tmp_path))
    resources = ResourceStorageCollection(hass, LovelaceStorage(hass, None))
    hass.data[LOVELACE_DATA] = SimpleNamespace(resources=resources)
    with patch(
        "custom_components.my_dom_ru.lovelace.async_get_integration",
        AsyncMock(return_value=SimpleNamespace(version="0.1.3")),
    ):
        yield hass
    await hass.async_stop()


@pytest.mark.asyncio
async def test_new_install_and_concurrent_account_reload_are_idempotent(card_hass):
    resources = card_hass.data[LOVELACE_DATA].resources
    with patch.object(resources.store, "async_load", AsyncMock(return_value={"items": []})), patch.object(
        resources, "async_create_item", wraps=resources.async_create_item
    ) as create:
        await asyncio.gather(*(
            async_register_card_resources(card_hass, URLS) for _ in range(3)
        ))
        assert create.await_count == 2
    assert resources.loaded
    assert {(item["url"], item["type"]) for item in resources.async_items()} == {
        (f"{url}?v=0.1.3", "module") for url in URLS
    }


@pytest.mark.asyncio
async def test_upgrade_manual_resources_preserves_ids_and_unrelated_items(card_hass):
    resources = card_hass.data[LOVELACE_DATA].resources
    unrelated = {"id": "other", "url": "/local/other.js?v=1", "type": "module"}
    foreign = {"id": "foreign", "url": f"https://example.com{CALL_CARD_URL}", "type": "module"}
    items = [
        {"id": "call", "url": f"{CALL_CARD_URL}?v=0.1.2", "type": "js"},
        {"id": "duplicate", "url": CALL_CARD_URL, "type": "module"},
        {"id": "mic", "url": CARD_URL, "type": "module"},
        unrelated, foreign,
    ]
    with patch.object(resources.store, "async_load", AsyncMock(return_value={"items": items})):
        await async_register_card_resources(card_hass, URLS)
    current = {item["id"]: item for item in resources.async_items()}
    assert set(current) == {"call", "mic", "other", "foreign"}
    assert current["other"] == unrelated
    assert current["foreign"] == foreign
    assert current["call"] == {"id": "call", "url": f"{CALL_CARD_URL}?v=0.1.3", "type": "module"}
    assert current["mic"]["url"] == f"{CARD_URL}?v=0.1.3"
    with patch.object(resources, "async_update_item", wraps=resources.async_update_item) as update:
        await async_register_card_resources(card_hass, URLS)
        update.assert_not_awaited()


@pytest.mark.asyncio
async def test_yaml_loads_missing_module_without_loading_existing_one_twice(card_hass):
    items = [{"url": f"{CALL_CARD_URL}?v=custom", "type": "module"}]
    card_hass.data[LOVELACE_DATA].resources = ResourceYAMLCollection(items.copy())
    with patch("custom_components.my_dom_ru.lovelace.add_extra_js_url") as add:
        await async_register_card_resources(card_hass, URLS)
        add.assert_called_once_with(card_hass, f"{CARD_URL}?v=0.1.3")
    assert card_hass.data[LOVELACE_DATA].resources.async_items() == items


@pytest.mark.asyncio
async def test_concurrent_setups_register_static_path_once_and_retry_resources():
    hass = SimpleNamespace(data={}, http=SimpleNamespace(async_register_static_paths=AsyncMock()))
    with patch("custom_components.my_dom_ru.uplink_ws.async_register_card_resources", AsyncMock()) as register:
        register.side_effect = [OSError("storage unavailable"), None, None]
        with pytest.raises(OSError):
            await async_register_uplink_card(hass)
        await asyncio.gather(async_register_uplink_card(hass), async_register_uplink_card(hass))
    hass.http.async_register_static_paths.assert_awaited_once()
    assert register.await_count == 3
