"""Authenticated, read-only WebSocket browser for previous call history."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import voluptuous as vol

from homeassistant.auth.permissions.const import POLICY_READ
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import Unauthorized
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er

from .coordinator import async_get_coordinator
from .const import CONF_ACCOUNT_ID, CONF_SUBSCRIBER_ID, DOMAIN, EVENT_KEY_ACTIVATED, LOGGER
from .access_keys import build_key_index, resolve_key_identity
from .history import map_general_event_type, place_display_name


_WS_REGISTERED = f"{DOMAIN}_history_ws_registered"


@dataclass(frozen=True, slots=True)
class HistoryBrowseTarget:
    """Resolved entity-scoped history source."""

    coordinator: Any
    place_ids: tuple[str, ...]
    sources: dict[tuple[str, str], str]
    source_name: str
    aggregate: bool


def _access_control_sources(
    coordinator: Any,
) -> dict[tuple[str, str], dict[str, Any]]:
    """Return one stable representative per place/access-control pair."""
    sources: dict[tuple[str, str], dict[str, Any]] = {}
    for lock_info in (coordinator.data or {}).get("locks") or []:
        place_id = str(lock_info.get("place_id") or "")
        access_control_id = str(lock_info.get("access_control_id") or "")
        if not place_id or not access_control_id:
            continue
        key = (place_id, access_control_id)
        current = sources.get(key)
        if current is None or str(lock_info.get("entrance_id") or "") < str(
            current.get("entrance_id") or ""
        ):
            sources[key] = lock_info
    return sources


def _resolve_target(
    hass: HomeAssistant,
    entity_id: str,
) -> HistoryBrowseTarget | None:
    """Resolve a registered account/place/access history entity by stable ID."""
    registry_entry = er.async_get(hass).async_get(entity_id)
    if (
        registry_entry is None
        or registry_entry.platform != DOMAIN
        or not registry_entry.config_entry_id
    ):
        return None
    coordinator = async_get_coordinator(hass, registry_entry.config_entry_id)
    if coordinator is None:
        return None
    source_locks = _access_control_sources(coordinator)
    entry = hass.config_entries.async_get_entry(registry_entry.config_entry_id)
    if entry is not None:
        account_id = str(entry.data.get(CONF_ACCOUNT_ID) or "")
        subscriber_id = str(entry.data.get(CONF_SUBSCRIBER_ID) or "")
        account_unique_id = (
            f"{DOMAIN}_event_history_account_{account_id}_{subscriber_id}"
        )
        if (
            account_id
            and subscriber_id
            and registry_entry.unique_id == account_unique_id
        ):
            return HistoryBrowseTarget(
                coordinator=coordinator,
                place_ids=tuple(sorted({key[0] for key in source_locks})),
                sources={
                    key: str(lock.get("name") or key[1])
                    for key, lock in source_locks.items()
                },
                source_name=entry.title,
                aggregate=True,
            )

        if account_id and subscriber_id:
            for place_id in sorted({key[0] for key in source_locks}):
                place_unique_id = (
                    f"{DOMAIN}_event_history_place_"
                    f"{account_id}_{subscriber_id}_{place_id}"
                )
                if registry_entry.unique_id != place_unique_id:
                    continue
                place_sources = {
                    key: str(lock.get("name") or key[1])
                    for key, lock in source_locks.items()
                    if key[0] == place_id
                }
                return HistoryBrowseTarget(
                    coordinator=coordinator,
                    place_ids=(place_id,),
                    sources=place_sources,
                    source_name=place_display_name(coordinator.data, place_id),
                    aggregate=True,
                )

    for (place_id, access_control_id), lock_info in source_locks.items():
        expected_unique_id = (
            f"{DOMAIN}_event_history_access_{place_id}_{access_control_id}"
        )
        if registry_entry.unique_id == expected_unique_id:
            return HistoryBrowseTarget(
                coordinator=coordinator,
                place_ids=(place_id,),
                sources={
                    (place_id, access_control_id): str(
                        lock_info.get("name") or access_control_id
                    )
                },
                source_name=str(lock_info.get("name") or access_control_id),
                aggregate=False,
            )
    return None


async def async_handle_history(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return one sanitized backend page for an authorized history entity."""
    entity_id = msg["entity_id"]
    user = connection.user
    if user is None or (
        not user.is_admin
        and not user.permissions.check_entity(entity_id, POLICY_READ)
    ):
        raise Unauthorized

    target = _resolve_target(hass, entity_id)
    if target is None:
        connection.send_error(
            msg["id"],
            "history_entity_not_found",
            "History entity is not available",
        )
        return
    try:
        place_ids = [int(place_id) for place_id in target.place_ids]
    except ValueError:
        connection.send_error(
            msg["id"],
            "history_entity_invalid",
            "History entity has an invalid place identifier",
        )
        return
    if not place_ids:
        connection.send_error(
            msg["id"],
            "history_entity_invalid",
            "History entity has no places",
        )
        return

    try:
        page = await target.coordinator.api.query_events(
            place_ids,
            page=msg["page"],
        )
    except Exception as ex:  # noqa: BLE001 - optional feature degradation
        LOGGER.debug("History browse fetch failed (%s)", type(ex).__name__)
        connection.send_error(
            msg["id"],
            "history_unavailable",
            "History is temporarily unavailable",
        )
        return

    indexes = {}
    for place_id in target.place_ids:
        if not any(
            event.place_id == place_id
            and event.event_type in ("infoNotification", "accessKeyActivated")
            for event in page.events
        ):
            continue
        try:
            keys = await target.coordinator.api.query_access_keys(place_id)
        except Exception:  # noqa: BLE001 - browsing calls still works without names
            keys = None
        indexes[place_id] = build_key_index(keys)

    all_sources = _access_control_sources(target.coordinator)
    events = []
    for event in page.events:
        if event.place_id not in target.place_ids:
            continue
        event_type = map_general_event_type(event.event_type)
        key_name = resolve_key_identity(event.message, indexes.get(event.place_id, {}))
        by_content = event.event_type == "infoNotification" and key_name is not None
        if by_content:
            event_type = EVENT_KEY_ACTIVATED
        source_key = (event.place_id, event.source_id)
        source_name = target.sources.get(source_key)
        if event_type is None:
            continue
        if event.source_type != "accessControl" or source_key not in target.sources:
            place_scoped = event_type == EVENT_KEY_ACTIVATED and (
                by_content
                or (event.source_type in ("place", "subscriberPlace")
                    and event.source_id == event.place_id)
            )
            if not place_scoped:
                continue
            place_sources = [key for key in all_sources if key[0] == event.place_id]
            if len(place_sources) == 1:
                source_key = place_sources[0]
                source_name = target.sources.get(source_key)
            elif target.aggregate:
                source_key = (event.place_id, "")
                source_name = place_display_name(target.coordinator.data, event.place_id)
            else:
                continue
            if not target.aggregate and source_key not in target.sources:
                continue
        result = {
            "event_id": event.id,
            "event_type": event_type,
            "occurred_at": event.timestamp,
        }
        if event_type == EVENT_KEY_ACTIVATED and key_name:
            result["key_name"] = key_name
        if target.aggregate:
            result.update(
                {
                    "place_id": event.place_id,
                    "source_id": source_key[1],
                    "source_name": source_name,
                }
            )
        events.append(result)

    connection.send_result(
        msg["id"],
        {
            "entity_id": entity_id,
            "source_name": target.source_name,
            "events": events,
            "page": page.number,
            "last": page.last,
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/history",
        vol.Required("entity_id"): cv.entity_id,
        vol.Optional("page", default=0): vol.All(
            int,
            vol.Range(min=0, max=100),
        ),
    }
)
@websocket_api.async_response
async def ws_history(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle a browser request without mutating EventEntity state."""
    await async_handle_history(hass, connection, msg)


@callback
def async_register_history_ws_command(hass: HomeAssistant) -> None:
    """Register the global history command once for all config entries."""
    if hass.data.get(_WS_REGISTERED):
        return
    websocket_api.async_register_command(hass, ws_history)
    hass.data[_WS_REGISTERED] = True
