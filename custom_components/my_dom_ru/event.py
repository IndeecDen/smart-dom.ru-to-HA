"""Doorbell call `event` entity — приём realtime-события вызова домофона.

Событие приходит по FCM data-push (см. fcm.py), парсится и рассылается через
dispatcher (`SIGNAL_DOORBELL`). Эта сущность ловит его и стреляет `event`:
- `ring`  — входящий вызов (`CALL_INCOMING`);
- `ended` — вызов завершён/принят на другом устройстве (`CALL_END_ANSWERED_MOBILE`).

Источник канала и payload — research/intercom-call-probe/FINDINGS.md.

Одна сущность на домофон `(place_id, access_control_id)` — дедуп по AC из
`coordinator.data["locks"]`. Device — общий с lock/intercom-camera того же
entrance (см. lock.py). Открытие двери — существующий lock; видео — go2rtc.
"""
from __future__ import annotations

from typing import Any

from homeassistant.components.event import EventDeviceClass, EventEntity
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util, slugify

from .const import (
    AREA_INTERCOM,
    AREA_INDOOR_CAM,
    AREA_NEIGHBOR_CAM,
    AREA_PUBLIC_CAM,
    CONF_ACCOUNT_ID,
    CONF_SUBSCRIBER_ID,
    DOMAIN,
    DOORBELL_CALL_WINDOW_FALLBACK_SEC,
    EVENT_KEY_ACTIVATED,
    LOGGER,
    SIGNAL_ACCESS_KEY,
    SIGNAL_DOORBELL,
)
from .coordinator import MyDomRuConfigEntry, MyDomRuUpdateCoordinator
from .device import linked_to_place, place_device_id, place_identifier
from .history import (
    camera_history_unique_id,
    history_signal,
    place_display_name,
)

# Сущности не опрашивают оператора поодиночке: данные приходят из
# координатора одним циклом на всю запись, поэтому ограничивать параллельные
# обновления нечем и незачем. Константа объявлена явно — правило Silver
# `parallel-updates` требует не полагаться на умолчание ядра, которое зависит
# от того, синхронный ли `update` у сущности.
PARALLEL_UPDATES = 0

EVENT_RING = "ring"
EVENT_ENDED = "ended"
EVENT_CALL_ACCEPTED = "call_accepted"
EVENT_CALL_MISSED = "call_missed"
EVENT_MOTION = "motion"

# How many backend event IDs one access entity remembers for dedup. The
# realtime push and the durable poll both carry `event_id`, so this only has
# to span one poll interval (5 min) plus slack.
_RECENT_EVENT_ID_LIMIT = 128

# Авто-`ended`: оператор присылает `ended` только при «принят на другом
# устройстве». На сброс у домофона / истечение времени ответа end-пуша нет —
# иначе статус навсегда завис бы на `ring`. Закрываем вызов сами ровно в момент
# `call_invalidated` (операторское окно из payload, не угаданная константа).
# Без margin: по прод-данным реальный `ended` прилетает за ~20с ДО call_invalidated
# (и снимает таймер через _cancel_auto_end), так что буфер ничего не ловил.
# Fallback-окно (нет/невалиден call_invalidated) — shared с sip/call_controller.py.
_AUTO_END_FALLBACK_SEC = DOORBELL_CALL_WINDOW_FALLBACK_SEC


def _place_history_unique_id(
    account_id: str,
    subscriber_id: str,
    place_id: str,
) -> str:
    """Return the stable registry ID for one place-history stream."""
    return (
        f"{DOMAIN}_event_history_place_"
        f"{account_id}_{subscriber_id}_{place_id}"
    )


def _place_history_entity_id(account_id: str, place_id: str) -> str:
    """Return an explicit account/place-scoped default entity ID."""
    return f"event.{slugify(f'account_{account_id}_place_{place_id}_event_history')}"


@callback
def _migrate_single_place_account_history_entity(
    hass: HomeAssistant,
    account_id: str,
    subscriber_id: str,
    place_ids: list[str],
) -> None:
    """Migrate the prerelease account stream when it maps to one place."""
    if len(place_ids) != 1:
        return
    registry = er.async_get(hass)
    legacy_unique_id = (
        f"{DOMAIN}_event_history_account_{account_id}_{subscriber_id}"
    )
    legacy_entity_id = registry.async_get_entity_id(
        "event", DOMAIN, legacy_unique_id
    )
    if legacy_entity_id is None:
        return

    place_id = place_ids[0]
    new_unique_id = _place_history_unique_id(
        account_id,
        subscriber_id,
        place_id,
    )
    if registry.async_get_entity_id("event", DOMAIN, new_unique_id) is not None:
        return

    legacy_object_id = legacy_entity_id.split(".", 1)[1]
    suffix = legacy_object_id.removeprefix("account_event_history")
    default_entity_id = suffix == "" or (
        suffix.startswith("_") and suffix[1:].isdigit()
    )
    new_entity_id = _place_history_entity_id(account_id, place_id)
    # Явные kwargs, а не распакованный dict: при `**update` проверка типов
    # раскладывает `str` по всем параметрам `async_update_entity` (их два
    # десятка) и перестаёт видеть настоящую сигнатуру.
    if default_entity_id and registry.async_get(new_entity_id) is None:
        registry.async_update_entity(
            legacy_entity_id,
            new_unique_id=new_unique_id,
            new_entity_id=new_entity_id,
        )
    else:
        registry.async_update_entity(legacy_entity_id, new_unique_id=new_unique_id)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MyDomRuConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Dom.ru Smart Home doorbell call events based on a config entry."""
    coordinator = entry.runtime_data
    locks = (coordinator.data or {}).get("locks") or []

    # Дедуп по (place_id, access_control_id) — одна event-сущность на домофон
    # (FCM-payload несёт AccessControlId, не entrance). При multi-entrance AC
    # берём lock с min entrance_id → стабильный intercom-device между рестартами.
    # str(), always: both ids arrive from the JSON API as numbers, while every
    # comparison downstream is against string fields of the payload. Keeping
    # the raw values made `interlocks_per_place` below int-keyed and its
    # `str(...)` lookup miss every time — which silently pinned
    # `sole_intercom` to False and left the intercom entity mute for key
    # events on an account that has exactly one intercom.
    by_ac: dict[tuple[str, str], dict] = {}
    for lk in locks:
        raw_place_id = lk.get("place_id")
        raw_ac_id = lk.get("access_control_id")
        if raw_place_id is None or raw_ac_id is None:
            continue
        key = (str(raw_place_id), str(raw_ac_id))
        cur = by_ac.get(key)
        if cur is None or str(lk.get("entrance_id") or "") < str(
            cur.get("entrance_id") or ""
        ):
            by_ac[key] = lk

    entities: list[EventEntity] = []
    entry_history_signal = history_signal(entry.entry_id)
    account_id = str(entry.data.get(CONF_ACCOUNT_ID) or "")
    subscriber_id = str(entry.data.get(CONF_SUBSCRIBER_ID) or "")
    if account_id and subscriber_id:
        place_ids = sorted({place_id for place_id, _ in by_ac})
        _migrate_single_place_account_history_entity(
            hass,
            account_id,
            subscriber_id,
            place_ids,
        )
        entities.extend(
            MyDomRuPlaceHistoryEvent(
                coordinator,
                account_id,
                subscriber_id,
                place_id,
                entry_history_signal,
                [
                    lock
                    for (source_place_id, _), lock in by_ac.items()
                    if source_place_id == place_id
                ],
            )
            for place_id in place_ids
        )
    entities.extend(
        MyDomRuDoorbellEvent(
            coordinator,
            lock_info,
            place_device_id(hass, entry.entry_id, str(lock_info["place_id"])),
        )
        for lock_info in by_ac.values()
    )
    # How many distinct interlocks each place has. A key event names the
    # address, not the entrance, so it is only attributable to a door when
    # the place has exactly one.
    interlocks_per_place: dict[str, set[str]] = {}
    for place_id, access_control_id in by_ac:
        interlocks_per_place.setdefault(place_id, set()).add(access_control_id)
    entities.extend(
        MyDomRuAccessHistoryEvent(
            coordinator,
            lock_info,
            entry_history_signal,
            place_device_id(hass, entry.entry_id, str(lock_info["place_id"])),
            sole_intercom=(
                len(interlocks_per_place.get(str(lock_info["place_id"]), ())) == 1
            ),
        )
        for lock_info in by_ac.values()
    )
    entities.extend(
        MyDomRuCameraHistoryEvent(
            coordinator,
            camera_info,
            entry_history_signal,
            place_device_id(
                hass, entry.entry_id, str(camera_info.get("place_id") or "")
            ),
        )
        for camera_info in (coordinator.data or {}).get("cameras") or []
        if camera_info.get("source") in ("intercom", "public")
    )
    LOGGER.debug(
        "Event setup: сущностей=%d, из них access=%d, account=%d",
        len(entities),
        len(by_ac),
        sum(1 for e in entities if isinstance(e, MyDomRuPlaceHistoryEvent)),
    )
    for (raw_place_id, raw_ac_id), lock_info in by_ac.items():
        LOGGER.debug(
            "Lock: place_id=%r (%s) ac_id=%r (%s) sole=%s",
            raw_place_id,
            type(raw_place_id).__name__,
            raw_ac_id,
            type(raw_ac_id).__name__,
            len(interlocks_per_place.get(str(lock_info["place_id"]), ())) == 1,
        )
    async_add_entities(entities)


class _AccessEventEntity(CoordinatorEntity[MyDomRuUpdateCoordinator], EventEntity):
    """Shared plumbing for intercom access events.

    Two delivery paths feed the same entity: the durable REST poll and the
    realtime `placeEvent` FCM push. Both carry the backend `event_id`, so the
    same activation can legitimately arrive twice; `_emit` deduplicates on it,
    and the push (seconds) normally wins the race over the poll (5 min).
    """

    _attr_has_entity_name = True

    def __init__(self, coordinator: MyDomRuUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._history_signal = ""
        # A dict, not a set: insertion order is what makes evicting the
        # *oldest* half well defined. `None` values keep membership O(1).
        self._recent_event_ids: dict[str, None] = {}

    async def async_added_to_hass(self) -> None:
        """Subscribe to the durable poll and the realtime push."""
        await super().async_added_to_hass()
        LOGGER.debug(
            "Event %s: подписан на push (типы=%s)",
            self.entity_id,
            self._attr_event_types,
        )
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, self._history_signal, self._emit
            )
        )
        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_ACCESS_KEY, self._emit)
        )

    @callback
    def _emit(self, payload: dict[str, Any]) -> None:
        """Fire one access event if it belongs here and has not been seen."""
        event_id = str(payload.get("event_id") or "")
        if payload.get("event_type") not in self._attr_event_types:
            LOGGER.debug(
                "Event %s: тип %s не в списке",
                self.entity_id,
                payload.get("event_type"),
            )
            return
        if not self._owns(payload):
            LOGGER.debug(
                "Event %s: не владеет payload place=%s source=%s by_content=%s",
                self.entity_id,
                payload.get("place_id"),
                payload.get("source_type"),
                payload.get("by_content"),
            )
            return

        if event_id:
            if event_id in self._recent_event_ids:
                LOGGER.debug(
                    "Event %s: дубликат %s", self.entity_id, event_id
                )
                return
            self._recent_event_ids[event_id] = None
            if len(self._recent_event_ids) > _RECENT_EVENT_ID_LIMIT:
                for stale in list(self._recent_event_ids)[
                    : _RECENT_EVENT_ID_LIMIT // 2
                ]:
                    del self._recent_event_ids[stale]
        LOGGER.debug(
            "Event %s: СРАБОТАЛА, тип=%s key_name=%s id=%s",
            self.entity_id,
            payload["event_type"],
            payload.get("key_name"),
            event_id,
        )

        attributes = {
            key: payload[key]
            for key in ("event_id", "occurred_at", "key_name")
            if payload.get(key) is not None
        }
        attributes.update(self._extra_attributes(payload))
        self._trigger_event(payload["event_type"], attributes)
        self.async_write_ha_state()

    def _owns(self, payload: dict[str, Any]) -> bool:
        """Return whether this event belongs to this entity."""
        raise NotImplementedError

    def _extra_attributes(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Return additional safe attributes for the fired event."""
        return {}


class MyDomRuPlaceHistoryEvent(_AccessEventEntity):
    """Aggregate intercom access history for one configured place."""

    _attr_translation_key = "account_history"
    _attr_event_types = [
        EVENT_CALL_ACCEPTED,
        EVENT_CALL_MISSED,
        EVENT_KEY_ACTIVATED,
    ]

    def __init__(
        self,
        coordinator: MyDomRuUpdateCoordinator,
        account_id: str,
        subscriber_id: str,
        place_id: str,
        history_dispatch_signal: str,
        locks: list[dict[str, Any]],
    ) -> None:
        super().__init__(coordinator)
        # str(), always: place ids arrive from the API as JSON numbers, and
        # the payloads reaching `_owns` carry them as strings. Comparing the
        # two directly would never match, which silently killed this entity.
        self._place_id = str(place_id)
        LOGGER.debug(
            "Account history entity: id=%s place_id=%r unique=%s",
            _place_history_entity_id(account_id, place_id),
            self._place_id,
            _place_history_unique_id(account_id, subscriber_id, place_id),
        )
        self._history_signal = history_dispatch_signal
        self._sources = {
            (str(lock["place_id"]), str(lock["access_control_id"])): str(
                lock.get("name") or lock["access_control_id"]
            )
            for lock in locks
        }
        self._attr_unique_id = _place_history_unique_id(
            account_id,
            subscriber_id,
            place_id,
        )
        self.entity_id = _place_history_entity_id(account_id, place_id)
        self._attr_device_info = DeviceInfo(
            identifiers={place_identifier(place_id)},
            name=place_display_name(coordinator.data, place_id),
            manufacturer="Умный Дом.ру",
            model="Place",
        )

    def _owns(self, payload: dict[str, Any]) -> bool:
        """Own events from a known intercom at this place.

        A key event identified by its text is also owned when it belongs to
        this place, whatever its source: the operator files those under
        `billingSystem` and names the address rather than the entrance, so
        this place-level stream is the only place they can honestly be
        reported. `source_name` is then absent, because there is no intercom
        to name.
        """
        if str(payload.get("place_id") or "") != self._place_id:
            return False
        if payload.get("by_content"):
            return True
        if payload.get("source_type") != "accessControl":
            return False
        source_key = (
            str(payload.get("place_id") or ""),
            str(payload.get("source_id") or ""),
        )
        return source_key in self._sources

    def _extra_attributes(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Add the intercom this event came from, when there is one."""
        source_key = (
            str(payload.get("place_id") or ""),
            str(payload.get("source_id") or ""),
        )
        name = self._sources.get(source_key)
        if name is None:
            return {"place_id": source_key[0]}
        return {
            "place_id": source_key[0],
            "source_id": source_key[1],
            "source_name": name,
        }


class MyDomRuAccessHistoryEvent(_AccessEventEntity):
    """Durable access history for one access control.

    Carries three event types:

    * `call_accepted` / `call_missed` — a video call to the intercom;
    * `key_activated` — an access key opened the door, reported within seconds
      via the realtime FCM push and backfilled by the durable poll if HA was
      down at the time.
    """

    _attr_translation_key = "access_history"
    _attr_event_types = [
        EVENT_CALL_ACCEPTED,
        EVENT_CALL_MISSED,
        EVENT_KEY_ACTIVATED,
    ]

    def __init__(
        self,
        coordinator: MyDomRuUpdateCoordinator,
        lock_info: dict[str, Any],
        history_dispatch_signal: str,
        via_device_id: str | None = None,
        *,
        sole_intercom: bool = False,
    ) -> None:
        super().__init__(coordinator)
        place_id = str(lock_info["place_id"])
        access_control_id = str(lock_info["access_control_id"])
        self._place_id = place_id
        self._access_control_id = access_control_id
        self._sole_intercom = sole_intercom
        self._history_signal = history_dispatch_signal
        entrance_id = lock_info.get("entrance_id")
        self._attr_unique_id = (
            f"{DOMAIN}_event_history_access_{place_id}_{access_control_id}"
        )
        device_uid = (
            f"entrance_{place_id}_{access_control_id}_{entrance_id or 'main'}"
        )
        self._attr_device_info = linked_to_place(
            DeviceInfo(
                identifiers={(DOMAIN, device_uid)},
                name=lock_info["name"],
                manufacturer="Умный Дом.ру",
                model="Intercom",
                suggested_area=AREA_INTERCOM,
            ),
            via_device_id,
        )

    def _owns(self, payload: dict[str, Any]) -> bool:
        """Own events for this intercom at this place.

        Call events identify the intercom through a source of type
        `accessControl`.

        Key events are harder. On a verified account the operator reports them
        under `source=billingSystem`, and the message names the *address*,
        never the entrance — so the door genuinely cannot be read off the
        event. The event is claimed only when this is the sole intercom at the
        place, where "the door" is unambiguous. With several entrances the
        place-level entity still reports it and this one stays silent, rather
        than firing once per door and being wrong most of the time.
        """
        if str(payload.get("place_id") or "") != self._place_id:
            return False
        if str(payload.get("source_id") or "") == self._access_control_id:
            return True
        if payload.get("by_content"):
            return self._sole_intercom
        return (
            payload.get("event_type") == EVENT_KEY_ACTIVATED
            and payload.get("source_type") == "subscriberPlace"
            and str(payload.get("source_id") or "") == self._place_id
        )


class MyDomRuCameraHistoryEvent(
    CoordinatorEntity[MyDomRuUpdateCoordinator], EventEntity
):
    """Durable verified motion history for one forpost camera."""

    _attr_has_entity_name = True
    _attr_translation_key = "camera_history"
    _attr_device_class = EventDeviceClass.MOTION
    _attr_event_types = [EVENT_MOTION]
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: MyDomRuUpdateCoordinator,
        camera_info: dict[str, Any],
        history_dispatch_signal: str,
        via_device_id: str | None = None,
    ) -> None:
        super().__init__(coordinator)
        camera_id = str(camera_info["id"])
        self._camera_id = camera_id
        self._history_signal = history_dispatch_signal
        self._attr_unique_id = camera_history_unique_id(camera_id)

        source = camera_info.get("source") or "public"
        place_id = camera_info.get("place_id")
        access_control_id = camera_info.get("access_control_id")
        entrance_id = camera_info.get("entrance_id")
        if source == "intercom" and place_id and access_control_id:
            device_uid = (
                f"entrance_{place_id}_{access_control_id}_{entrance_id or 'main'}"
            )
            self._attr_device_info = linked_to_place(
                DeviceInfo(
                    identifiers={(DOMAIN, device_uid)},
                    name=camera_info.get("name") or camera_id,
                    manufacturer="Умный Дом.ру",
                    model="Intercom",
                    suggested_area=AREA_INTERCOM,
                ),
                via_device_id,
            )
        else:
            if source == "place":
                model, area = "Indoor Camera", AREA_INDOOR_CAM
            elif source == "neighbor":
                model, area = "Neighbor Camera", AREA_NEIGHBOR_CAM
            else:
                model, area = "Public Camera", AREA_PUBLIC_CAM
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, f"camera_{camera_id}")},
                name=camera_info.get("name") or camera_id,
                manufacturer="Умный Дом.ру",
                model=model,
                suggested_area=area,
            )

    async def async_added_to_hass(self) -> None:
        """Subscribe to sanitized durable-history events."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                self._history_signal,
                self._handle_history,
            )
        )

    @callback
    def _handle_history(self, payload: dict[str, Any]) -> None:
        """Route one verified motion event to this camera entity."""
        event_type = payload.get("event_type")
        if (
            event_type != EVENT_MOTION
            or str(payload.get("camera_id")) != self._camera_id
        ):
            return
        attributes = {
            key: payload[key]
            for key in (
                "event_id",
                "occurred_at",
                "duration",
                "recording_available",
            )
            if key in payload
        }
        self._trigger_event(event_type, attributes)
        self.async_write_ha_state()


class MyDomRuDoorbellEvent(
    CoordinatorEntity[MyDomRuUpdateCoordinator], EventEntity
):
    """`event`-сущность вызова домофона (EventDeviceClass.DOORBELL)."""

    _attr_has_entity_name = True
    _attr_translation_key = "doorbell"
    _attr_device_class = EventDeviceClass.DOORBELL
    _attr_event_types = [EVENT_RING, EVENT_ENDED]

    def __init__(
        self,
        coordinator: MyDomRuUpdateCoordinator,
        lock_info: dict[str, Any],
        via_device_id: str | None = None,
    ) -> None:
        super().__init__(coordinator)
        self._place_id: str = lock_info["place_id"]
        self._access_control_id: str = lock_info["access_control_id"]
        self._entrance_id = lock_info.get("entrance_id")
        self._name: str = lock_info["name"]
        self._auto_end_cancel: CALLBACK_TYPE | None = None
        self._ring_attributes: dict[str, Any] = {}

        self._attr_unique_id = (
            f"{DOMAIN}_event_doorbell_{self._place_id}_{self._access_control_id}"
        )
        # Тот же device, что у lock/intercom-camera этого entrance.
        device_uid = (
            f"entrance_{self._place_id}_{self._access_control_id}_"
            f"{self._entrance_id or 'main'}"
        )
        self._attr_device_info = linked_to_place(
            DeviceInfo(
                identifiers={(DOMAIN, device_uid)},
                name=self._name,
                manufacturer="Умный Дом.ру",
                model="Intercom",
                suggested_area=AREA_INTERCOM,
            ),
            via_device_id,
        )

    async def async_added_to_hass(self) -> None:
        """Подписка на realtime-сигнал вызова + baseline «нет вызова»."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_DOORBELL, self._handle_doorbell)
        )
        self.async_on_remove(self._cancel_auto_end)
        # EventEntity(RestoreEntity) сам восстанавливает последнее событие после
        # рестарта HA / reload. Если восстанавливать нечего (самый первый запуск) —
        # state=None («Неизвестно»). Ставим условный baseline `ended` = нет
        # активного вызова, чтобы сущность не висела в Unknown. В момент первой
        # установки реальный вызов крайне маловероятен, а настоящий `ring` его
        # сразу перепишет. На рестартах baseline не трогаем (state уже восстановлен)
        # — синтетическое событие стреляет максимум один раз, до появления автоматизаций.
        if self.state is None:
            self._trigger_event(EVENT_ENDED)
            self.async_write_ha_state()

    @callback
    def _handle_doorbell(self, payload: dict[str, Any]) -> None:
        """Dispatcher callback. Стреляем event, если вызов для нашего домофона.

        payload (от fcm.py): {"event_type": "ring"|"ended", "place_id",
        "access_control_id", "attributes": {...}}.
        """
        if (
            str(payload.get("place_id")) != str(self._place_id)
            or str(payload.get("access_control_id")) != str(self._access_control_id)
        ):
            return
        event_type = payload.get("event_type")
        if event_type not in self._attr_event_types:
            LOGGER.debug("Doorbell: неизвестный event_type %s — пропуск", event_type)
            return
        attributes = dict(payload.get("attributes") or {})
        # Apartment/Sender в пуше у калиток gate-кодированы префиксом корпуса/секции;
        # канонический номер квартиры жильца — в place.address оператора
        # (coordinator.data["places"]). Подъезд шлёт уже чистый номер.
        canonical_apartment = self._resident_apartment()
        if canonical_apartment:
            attributes["apartment"] = canonical_apartment
        self._trigger_event(event_type, attributes)
        self.async_write_ha_state()
        if event_type == EVENT_RING:
            self._schedule_auto_end(attributes)
        else:  # реальный `ended` — снять авто-таймер, чтобы не было дубля
            self._cancel_auto_end()

    def _resident_apartment(self) -> str | None:
        """Канонический номер квартиры жильца из place.address оператора.

        Место истины — `apartment` в subscriber-places (coordinator.data["places"]),
        а не gate-кодированный `Apartment`/`Sender` из FCM-пуша.
        """
        for sp in (self.coordinator.data or {}).get("places") or []:
            place = sp.get("place") or {}
            if str(place.get("id")) == str(self._place_id):
                address = place.get("address")
                if isinstance(address, dict):
                    return address.get("apartment")
        return None

    @callback
    def _schedule_auto_end(self, ring_attributes: dict[str, Any]) -> None:
        """Взвести авто-`ended` к моменту `call_invalidated` из push.

        Оператор шлёт `ended` только при «принят на другом устройстве». На сброс
        у домофона / истечение времени ответа end-пуша нет — без этого статус
        завис бы на `ring`. Берём операторское окно (`call_invalidated`), не
        угадываем константу; при отсутствии/невалидности — fallback.
        """
        self._cancel_auto_end()
        self._ring_attributes = ring_attributes
        delay = _AUTO_END_FALLBACK_SEC
        invalidated = ring_attributes.get("call_invalidated")
        if invalidated:
            parsed = dt_util.parse_datetime(invalidated)
            if parsed is not None:
                remaining = (parsed - dt_util.utcnow()).total_seconds()
                delay = max(remaining, 1.0)
        self._auto_end_cancel = async_call_later(self.hass, delay, self._auto_end_fire)

    @callback
    def _auto_end_fire(self, _now: Any) -> None:
        """Сработал таймер: реального `ended` не пришло → закрываем вызов сами."""
        self._auto_end_cancel = None
        self._trigger_event(
            EVENT_ENDED,
            {
                "reason": "timeout",
                "call_id": self._ring_attributes.get("call_id"),
                "gate_name": self._ring_attributes.get("gate_name"),
            },
        )
        self.async_write_ha_state()

    @callback
    def _cancel_auto_end(self) -> None:
        """Снять отложенный авто-`ended` (реальный конец / новый вызов / удаление)."""
        if self._auto_end_cancel is not None:
            self._auto_end_cancel()
            self._auto_end_cancel = None
