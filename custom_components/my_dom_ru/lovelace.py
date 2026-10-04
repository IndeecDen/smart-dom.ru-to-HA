"""Register bundled cards and migrate manually added Lovelace resources."""
from __future__ import annotations

import asyncio
from urllib.parse import urlsplit

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.lovelace.const import LOVELACE_DATA
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

from .const import DOMAIN

_LOCK = f"{DOMAIN}_lovelace_lock"


async def async_register_card_resources(
    hass: HomeAssistant, urls: tuple[str, ...]
) -> None:
    """Load cards once per URL, including on installations using YAML resources."""
    async with hass.data.setdefault(_LOCK, asyncio.Lock()):
        integration = await async_get_integration(hass, DOMAIN)
        resources = hass.data[LOVELACE_DATA].resources
        # This public method also loads the lazy storage collection before we
        # inspect it. Serializing entry setups avoids duplicate registrations.
        await resources.async_get_info()
        for path in urls:
            url = f"{path}?v={integration.version}"
            matches = [
                item for item in resources.async_items()
                if urlsplit(item["url"]).path == path
                and not urlsplit(item["url"]).netloc
            ]
            if not isinstance(resources, ResourceStorageCollection):
                # YAML belongs to the user. Existing resources already load in
                # Lovelace; register missing modules through the frontend API.
                if not matches:
                    add_extra_js_url(hass, url)
                continue

            if not matches:
                await resources.async_create_item({"url": url, "res_type": "module"})
                continue

            first, *duplicates = matches
            if first["url"] != url or first["type"] != "module":
                await resources.async_update_item(
                    first["id"], {"url": url, "res_type": "module"}
                )
            for duplicate in duplicates:
                await resources.async_delete_item(duplicate["id"])
