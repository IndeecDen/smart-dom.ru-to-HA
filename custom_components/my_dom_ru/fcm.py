"""FCM listener — серверный приём realtime-пуша о вызове домофона.

Эмулирует регистрацию Android-устройства в FCM (firebase-messaging, project
myhome-3b9cc), привязывает токен у оператора (api.register_push_device) и держит
MTalk-сокет. На CALL_INCOMING / CALL_END_ANSWERED_MOBILE рассылает SIGNAL_DOORBELL
→ event-сущность (event.py).

⚠️ Флоу опирается на приватные API Google (ADR-0011) и работает под graceful
degradation: сбой подключения логируется warning'ом, setup entry не падает,
polling-данные (камеры, замки, баланс, история) продолжают работать — не
стреляет только событие вызова. Единственное исключение из «сбой не мешает
ничему» — неподтверждённая остановка receiver'а при выгрузке: `async_stop()`
вернёт False, `async_unload_entry` в `__init__.py` тоже вернёт False, и HA
сообщит, что нужен рестарт. Так мы не оставляем два живых receiver'а на один
аккаунт — см. `docs/specs/2026-08-10-fcm-circuit-breaker-design.md`.

Источник канала и payload — research/intercom-call-probe/FINDINGS.md.
"""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import dt as dt_util

from .access_keys import (
    build_key_index,
    describe_key_payload,
    mask_secrets,
    resolve_key_identity,
)
from .api import MyDomRuAPI
from .const import (
    CONF_FCM_CREDENTIALS,
    DOMAIN,
    EVENT_KEY_ACTIVATED,
    FCM_API_KEY,
    FCM_APP_ID,
    FCM_BUNDLE_ID,
    FCM_PROJECT_ID,
    FCM_SENDER_ID,
    LOGGER,
    SIGNAL_ACCESS_KEY,
    SIGNAL_DOORBELL,
)

def parse_place_event(raw: str) -> dict[str, Any] | None:
    """Parse one `placeEvent` push body into a flat, sanitized dict.

    Kept free of Home Assistant imports so it can be unit tested directly.

    Args:
        raw: The JSON string carried under the `u` bundle key.

    Returns:
        A dict with `event_type`, `event_id`, `timestamp`, `message`,
        `place_id`, `source_type` and `source_id`, or None when the payload is
        not a well formed `placeEvent` carrying the fields we need.

    Note:
        `timestamp` arrives as a JSON *string* in the push (the app's Moshi
        model types it as String) but as a JSON *number* in the REST history
        response. Both are accepted and normalized to int.
    """
    try:
        envelope = json.loads(raw)
    except (TypeError, ValueError):
        return None
    if not isinstance(envelope, dict):
        return None
    event = envelope.get("event")
    if not isinstance(event, dict) or event.get("type") != _PLACE_EVENT_TYPE:
        return None
    payload = event.get("payload")
    if not isinstance(payload, dict):
        return None

    event_type = payload.get("eventTypeName")
    event_id = payload.get("id")
    place_id = payload.get("placeId")
    source = payload.get("source")
    if not isinstance(event_type, str) or not isinstance(event_id, str | int):
        return None
    if not isinstance(place_id, int):
        return None
    if not isinstance(source, dict):
        return None
    source_type = source.get("type")
    source_id = source.get("id")
    if not isinstance(source_type, str) or not isinstance(source_id, int):
        return None

    try:
        timestamp = int(payload.get("timestamp"))
    except (TypeError, ValueError):
        return None
    message = payload.get("message")
    return {
        "event_type": event_type,
        "event_id": str(event_id),
        "timestamp": timestamp,
        "message": message if isinstance(message, str) else "",
        "place_id": str(place_id),
        "source_type": source_type,
        "source_id": str(source_id),
    }


# PushType (FCM) → event_type сущности. Таксономия `ended`/`reason` — в
# docs/architecture/api-reference.md (раздел «Вызов домофона»).
_PUSH_TYPE_EVENT = {
    "CALL_INCOMING": "ring",
    "CALL_END_ANSWERED_MOBILE": "ended",
}

#: Bundle key holding a `placeEvent` push, as used by the Android app. Unlike
#: the call channel (flat `PushType` keys), every non-call event arrives as a
#: JSON blob under this key:
#: ``{"event": {"payload": {...}, "type": "placeEvent"}}``.
#:
#: Only `accessKeyActivated` is acted on. The other event types the app
#: renders (cameraMoving, billingNotification, emergencyNotification, …) are
#: either covered by the REST poll or deliberately not wired up here — an
#: emergency push in particular should not be swallowed by a home automation.
_EVENT_PUSH_KEY = "u"
_PLACE_EVENT_TYPE = "placeEvent"
_PUSH_ACCESS_KEY_EVENT = "accessKeyActivated"

# How often the access-key name index is reloaded from the operator. Names
# change when someone renames a key in the phone app, which is rare; a
# door opening is judged against a warm cache because the push handler is
# synchronous.
KEY_INDEX_INTERVAL = timedelta(minutes=10)

# Предохранитель самой firebase-messaging: после N подряд ошибок соединения
# библиотека сама останавливает receiver (`_terminate()` → run_state STOPPING).
#
# Его нельзя отключать (`None`). При `None` проверка в `_try_increment_error_count`
# становится всегда-ложной, `_terminate()` недостижим, и `_listen` бесконечно
# перечитывает мёртвый StreamReader: `readexactly` мгновенно перевыбрасывает
# сохранённый `_exception`, дописывая фрейм в его traceback, а библиотека на
# каждой итерации печатает его целиком через `_logger.exception`. Петля живёт в
# общем event loop, поэтому HA подвисает, а стоимость форматирования растёт
# квадратично (production-инцидент 2026-08-12).
#
# Счётчик CONNECTION обнуляется только реальным сообщением от сервера
# (`_handle_message`, после раннего `return` для LoginResponse), поэтому на
# здоровом сокете heartbeat'ы каждые 10-20 с держат его на нуле, а петля
# «connect → login → разрыв» упирается в лимит и честно гасит receiver.
# Дальше подхватывает watchdog ниже: мёртвый клиент = `is_started() == False`.
FCM_ABORT_AFTER_ERRORS = 3

# Watchdog: интервал контроля живости FCM-сокета. Ловит остановленный
# библиотекой receiver и провал первичного checkin (`client is None`) —
# иначе пуши о вызове молча отвалятся (инцидент 2026-06-24). Восстановление
# ограничено: см. `_async_watchdog` и backoff ниже.
FCM_WATCHDOG_INTERVAL = timedelta(minutes=2)

# Пауза между пробами после того, как circuit разомкнут, и её подпись для
# лога. Последняя пара повторяется бесконечно.
#
# Подпись лежит рядом со значением, а не считается форматтером: `str(timedelta)`
# даёт нечитаемое `0:15:00`, а склонять произвольную длительность незачем —
# значений ровно четыре, и забыть подпись при добавлении новой паузы нельзя.
# Винительный падеж, чтобы строка вставала после «через».
FCM_RETRY_BACKOFFS = (
    (timedelta(minutes=15), "15 минут"),
    (timedelta(hours=1), "1 час"),
    (timedelta(hours=6), "6 часов"),
    (timedelta(hours=24), "24 часа"),
)

_FCM_REPAIR_ISSUE_PREFIX = "fcm_receiver_unavailable"


def _b64_pad(value: str) -> str:
    """Дополнить base64url-строку `=` до длины, кратной 4."""
    return value + "=" * (-len(value) % 4)


def _normalize_push_header(header: str, label: str) -> str:
    """Свести Web Push заголовок к одному сегменту с корректным padding.

    `Crypto-Key` и `Encryption` — списки параметров через `;` (RFC 8188 §2.1,
    RFC 8291 §4), а не одиночные значения, поэтому нужный сегмент выбираем по
    метке независимо от его позиции.
    """
    for segment in header.split(";"):
        name, sep, payload = segment.strip().partition("=")
        if sep and name == label:
            return f"{label}={_b64_pad(payload.strip())}"
    # Метки нет. Библиотека всё равно срежет 3/5 символов, то есть съест
    # реальные байты ключа, поэтому метку восстанавливаем — но только если
    # строка вообще может быть голым значением: `=` в base64url встречается
    # лишь как хвостовой padding. Незнакомую форму отдаём нетронутой.
    bare = header.strip()
    if not bare or "=" in bare.rstrip("="):
        return header
    return f"{label}={_b64_pad(bare)}"


def _patch_push_headers(client: Any) -> None:
    """Нормализовать crypto-key/encryption до формы, которую ждёт библиотека.

    firebase-messaging 0.4.5 читает оба заголовка как одиночное значение и
    срезает префикс вслепую — `[3:]` для `dh=`, `[5:]` для `salt=`
    (`fcmpushclient.py:425-426`), после чего декодирует остаток без padding
    (`:378-379`). На реальном пуше оператора это ломается дважды:

    * `crypto-key` пришёл в VAPID-форме `dh=<87>; p256ecdsa=<87>` — после
      среза остаётся `<dh>; p256ecdsa=<...>`, и base64-декодер молча
      выбрасывает `;`, пробел и буквы метки, собирая 137 байт вместо 65;
    * `dh` передан без `=`-padding (87 символов), тогда как `salt` — с ним
      (24 символа), так что одного лишь padding'а недостаточно.

    Итог до фикса — `Invalid EC key.` (а без padding'а `Incorrect padding`)
    на каждом зашифрованном пуше, то есть на каждом звонке в домофон.
    Падение происходит до `self.callback(...)`: событие не доезжает до
    интеграции, ACK не отправляется, и Google переигрывает то же сообщение
    при каждом переподключении, роняя клиент по кругу.

    Правим заголовки в `app_data` до того, как их прочитает библиотека —
    достаём нужный сегмент по метке независимо от его позиции и дополняем
    padding. Криптографию и порядок вызовов не трогаем; когда апстрим
    научится разбирать список параметров, патч станет no-op. Обновиться
    некуда: 0.4.5 — последняя версия на PyPI.

    Патчим **экземпляр**, а не класс: `firebase-messaging` тянет за собой не
    только нас (её же использует `ring_doorbell[listen]`, то есть core-
    интеграция `ring` в том же процессе). Классовый патч чинил бы и чужие
    клиенты, и переживал бы выгрузку нашего entry — радиус шире, чем нужно.

    Форма заголовков снята с прода 2026-08-13 (DIAG-проба);
    в июне 2026 сегмента `p256ecdsa` ещё не было — см. `research/
    intercom-call-probe/logs/fcm.log` с 16 расшифрованными `CALL_INCOMING`.
    """
    original = client._handle_data_message

    def _handle_with_normalized_headers(msg: Any) -> Any:
        for item in msg.app_data:
            if item.key == "crypto-key":
                item.value = _normalize_push_header(item.value, "dh")
            elif item.key == "encryption":
                item.value = _normalize_push_header(item.value, "salt")
        return original(msg)

    client._handle_data_message = _handle_with_normalized_headers


def fcm_repair_issue_id(entry_id: str) -> str:
    """Вернуть стабильный Repairs issue ID для config entry."""
    return f"{_FCM_REPAIR_ISSUE_PREFIX}_{entry_id}"


@callback
def async_create_fcm_repair_issue(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    """Show one persistent degraded-FCM issue for a config entry."""
    ir.async_create_issue(
        hass,
        DOMAIN,
        fcm_repair_issue_id(entry.entry_id),
        is_fixable=False,
        is_persistent=True,
        severity=ir.IssueSeverity.ERROR,
        translation_key="fcm_receiver_unavailable",
        translation_placeholders={"entry_title": entry.title},
    )


@callback
def async_delete_fcm_repair_issue(
    hass: HomeAssistant, entry_id: str
) -> None:
    """Удалить persistent FCM issue одного config entry."""
    ir.async_delete_issue(hass, DOMAIN, fcm_repair_issue_id(entry_id))


class _FcmRecoveryPhase(StrEnum):
    """Per-entry FCM recovery phase."""

    HEALTHY = "healthy"
    SUSPECT = "suspect"
    VERIFYING = "verifying"
    OPEN = "open"


class DoorbellFcmListener:
    """Держит FCM-соединение и рассылает событие вызова через dispatcher."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: MyDomRuAPI,
        coordinator: Any = None,
    ) -> None:
        self._hass = hass
        self._entry = entry
        self._api = api
        # Needed to learn which place the access keys belong to. Optional so the
        # listener can be built in isolation; without it the name index stays
        # empty and key events degrade to anonymous rather than failing.
        self._coordinator = coordinator
        self._client: Any = None
        # Name index for access keys, kept warm by a timer. A door opening
        # must be named the moment the push lands, and the push callback is
        # synchronous, so the keys are fetched ahead of time.
        self._key_index: dict[str, str] = {}
        self._key_index_unsub: Any = None
        # Watchdog: unsub периодического контроля живости + guard от
        # перекрытия повторных переподнятий.
        self._watchdog_unsub: Any = None
        self._transition_lock = asyncio.Lock()
        self._stopping = False
        self._recovery_phase = _FcmRecoveryPhase.HEALTHY
        self._next_probe_at: datetime | None = None
        self._backoff_index = 0
        # FCM push-токен (после checkin_or_register). Нужен SIP-ответу для
        # push-params REGISTER (pn-tok=...) — см. sip/call_controller.py.
        self.fcm_token: str | None = None

    async def async_start(self) -> None:
        """Первичный коннект + запуск watchdog'а (контроль живости сокета)."""
        async with self._transition_lock:
            if self._stopping or self._watchdog_unsub is not None:
                return
            await self._async_connect()
            if self._stopping:
                # Выгрузка успела начаться уже после успешного start() —
                # здесь клиент реальный и его надо закрыть.
                await self._async_disconnect()
                return
            self._watchdog_unsub = async_track_time_interval(
                self._hass, self._async_watchdog, FCM_WATCHDOG_INTERVAL
            )
            # Prime once, then keep it warm.
            await self.async_refresh_key_index()
            self._key_index_unsub = async_track_time_interval(
                self._hass, self.async_refresh_key_index, KEY_INDEX_INTERVAL
            )

    async def _async_connect(self) -> None:
        """checkin/register → привязка токена у оператора → start MTalk-сокет.

        Полностью contained: любая ошибка здесь — warning, `self._client`
        остаётся `None`, и watchdog разбирается дальше по своей state machine.
        Клиент публикуется в `self._client` только после успешного `start()`.
        """
        try:
            from firebase_messaging import (
                FcmPushClient,
                FcmPushClientConfig,
                FcmRegisterConfig,
            )
        except Exception as err:  # noqa: BLE001
            LOGGER.warning(
                "FCM: firebase-messaging недоступна (%s) — событие вызова отключено",
                type(err).__name__,
            )
            return

        try:
            register_config = FcmRegisterConfig(
                project_id=FCM_PROJECT_ID,
                app_id=FCM_APP_ID,
                api_key=FCM_API_KEY,
                messaging_sender_id=FCM_SENDER_ID,
                bundle_id=FCM_BUNDLE_ID,
            )
            credentials = self._entry.data.get(CONF_FCM_CREDENTIALS)
            # Keep the candidate local until start(): firebase-messaging 0.4.5
            # creates stopping_lock in start(), so stop() is unsafe beforehand.
            client = FcmPushClient(
                self._on_notification,
                register_config,
                credentials,
                self._on_credentials_updated,
                config=FcmPushClientConfig(
                    abort_on_sequential_error_count=FCM_ABORT_AFTER_ERRORS
                ),
                http_client_session=async_get_clientsession(self._hass),
            )
            # Внутри `try`: патч читает приватный метод зависимости, а верхней
            # границы версии в manifest нет. Если апстрим его переименует,
            # ошибка должна уйти в graceful degradation, а не оборвать
            # `_async_connect` до постановки watchdog'а.
            _patch_push_headers(client)
            fcm_token = await client.checkin_or_register()
            self.fcm_token = fcm_token
            # Начатую выгрузку видно только здесь: `async_stop()` выставляет
            # флаг до захвата lock'а и ждёт нас. Нестартовавший клиент просто
            # отбрасываем — `stop()` до `start()` упадёт на `stopping_lock`.
            if self._stopping:
                return
            if not await self._api.register_push_device(fcm_token):
                LOGGER.warning(
                    "FCM: привязка push-токена у оператора не удалась — пуши могут не прийти"
                )
            if self._stopping:
                return
            await client.start()
            self._client = client
            LOGGER.info("FCM doorbell listener запущен")
        except Exception as err:  # noqa: BLE001
            # Текст исключения зависимости может нести credentials/payload —
            # логируем только класс (ADR-0004).
            LOGGER.warning(
                "FCM: не удалось запустить listener (%s) — событие вызова отключено",
                type(err).__name__,
            )

    @callback
    def _async_mark_healthy(self) -> None:
        """Сбросить recovery-state после подтверждённого healthy-тика."""
        recovered = self._recovery_phase in {
            _FcmRecoveryPhase.VERIFYING,
            _FcmRecoveryPhase.OPEN,
        }
        self._recovery_phase = _FcmRecoveryPhase.HEALTHY
        self._next_probe_at = None
        self._backoff_index = 0
        async_delete_fcm_repair_issue(self._hass, self._entry.entry_id)
        if recovered:
            LOGGER.info("FCM: push-receiver восстановлен")

    @callback
    def _async_open_circuit(self, now: datetime) -> None:
        """Назначить следующую пробу и показать persistent Repairs issue."""
        if self._stopping:
            return
        delay, delay_text = FCM_RETRY_BACKOFFS[self._backoff_index]
        self._backoff_index = min(
            self._backoff_index + 1, len(FCM_RETRY_BACKOFFS) - 1
        )
        self._next_probe_at = now + delay
        self._recovery_phase = _FcmRecoveryPhase.OPEN
        async_create_fcm_repair_issue(self._hass, self._entry)
        LOGGER.warning(
            "FCM: частые попытки восстановления приостановлены; "
            "следующая проверка через %s",
            delay_text,
        )

    async def _async_reconnect(self) -> bool:
        """Выполнить один защищённый disconnect/connect цикл."""
        if not await self._async_disconnect():
            return False
        if self._stopping:
            return False
        await self._async_connect()
        if not self._stopping:
            self._recovery_phase = _FcmRecoveryPhase.VERIFYING
        return True

    async def _async_watchdog(self, _now: datetime | None = None) -> None:
        """Наблюдать receiver и выполнять bounded automatic recovery.

        Один тик = один переход. Живой клиент всегда возвращает в HEALTHY;
        мёртвый идёт HEALTHY → SUSPECT → VERIFYING → OPEN, где OPEN пробует
        восстановиться по backoff-расписанию.
        """
        if self._stopping or self._transition_lock.locked():
            return
        async with self._transition_lock:
            if self._stopping:
                return
            client = self._client
            if client is not None and client.is_started():
                self._async_mark_healthy()
                return

            now = _now or dt_util.utcnow()

            match self._recovery_phase:
                case _FcmRecoveryPhase.HEALTHY:
                    # Первая неактивность — только наблюдаем: даём библиотеке
                    # тик на самостоятельное переподключение.
                    self._recovery_phase = _FcmRecoveryPhase.SUSPECT

                case _FcmRecoveryPhase.SUSPECT:
                    LOGGER.warning(
                        "FCM: push-receiver неактивен — выполняю одну попытку восстановления"
                    )
                    if not await self._async_reconnect():
                        self._async_open_circuit(now)

                case _FcmRecoveryPhase.VERIFYING:
                    # Замена не ожила к следующему тику — размыкаем circuit.
                    await self._async_disconnect()
                    self._async_open_circuit(now)

                case _FcmRecoveryPhase.OPEN:
                    if self._next_probe_at is not None and now < self._next_probe_at:
                        return
                    LOGGER.info("FCM: выполняю пробную попытку восстановления")
                    if not await self._async_reconnect():
                        self._async_open_circuit(now)

    async def _async_disconnect(self) -> bool:
        """Остановить текущий MTalk-сокет (watchdog НЕ трогаем)."""
        client = self._client
        if client is None:
            return True
        try:
            await client.stop()
        except Exception as err:  # noqa: BLE001
            LOGGER.warning(
                "FCM: не удалось остановить listener (%s)",
                type(err).__name__,
            )
            return False
        if self._client is client:
            self._client = None
        return True

    async def async_stop(self) -> bool:
        """Полная остановка на unload entry: отменить watchdog + закрыть сокет."""
        self._stopping = True
        if self._watchdog_unsub is not None:
            self._watchdog_unsub()
            self._watchdog_unsub = None
        if self._key_index_unsub is not None:
            self._key_index_unsub()
            self._key_index_unsub = None
        async with self._transition_lock:
            stopped = await self._async_disconnect()
        if stopped and self._entry.disabled_by is not None:
            async_delete_fcm_repair_issue(self._hass, self._entry.entry_id)
        return stopped

    @callback
    def _on_credentials_updated(self, credentials: dict, *_: Any) -> None:
        """Персист FCM-creds в entry.data — стабильный токен между рестартами.

        Тот же guard, что и в `_on_notification`: при неподтверждённой
        остановке клиент остаётся живым и после удаления entry, а запись в
        чужой/удалённый entry бросит `UnknownEntry` внутри чужой таски.
        """
        if self._stopping:
            return
        self._hass.config_entries.async_update_entry(
            self._entry,
            data={**self._entry.data, CONF_FCM_CREDENTIALS: credentials},
        )

    @callback
    def _on_notification(self, notification: dict, persistent_id: str, *_: Any) -> None:
        """Callback firebase-messaging: парсит push → SIGNAL_DOORBELL / SIGNAL_ACCESS_KEY."""
        if self._stopping:
            return
        data = (notification or {}).get("data") or {}
        if self._async_handle_place_event(data):
            return
        push_type = data.get("PushType") or data.get("google.c.a.m_l")
        event_type = _PUSH_TYPE_EVENT.get(str(push_type)) if push_type else None
        if not event_type:
            # Не дропаем молча: если оператор шлёт end-пуш на сброс/таймаут
            # неизвестным типом — увидим его здесь и замаппим в следующем слайсе.
            LOGGER.debug("FCM: PushType %s не обрабатывается — пропуск", push_type)
            return
        attributes: dict[str, Any] = {
            "gate_name": data.get("GateName"),
            "apartment": data.get("Apartment"),
            "call_id": data.get("Call-ID"),
            "allow_open": data.get("AllowOpen"),
            "call_started": data.get("CallStarted"),
            "call_invalidated": data.get("CallInvalidated"),
        }
        if event_type == "ended":
            attributes["reason"] = "answered_elsewhere"
        async_dispatcher_send(
            self._hass,
            SIGNAL_DOORBELL,
            {
                "event_type": event_type,
                "place_id": str(data.get("PlaceId") or ""),
                "access_control_id": str(data.get("AccessControlId") or ""),
                "attributes": attributes,
            },
        )

    async def async_refresh_key_index(self) -> None:
        """Reload the key name index from the operator.

        Kept warm on a timer rather than fetched inside the push callback,
        which is synchronous: a door opening must be named immediately, so
        there is no time for a request first.
        """
        if self._coordinator is None:
            return
        for place in (self._coordinator.data or {}).get("places") or []:
            place_id = (place.get("place") or {}).get("id")
            if place_id is None:
                continue
            keys = await self._api.query_access_keys(place_id)
            self._key_index = build_key_index(keys)
            LOGGER.debug(
                "FCM: индекс ключей обновлён: ответ=%s, форм=%d, place_id=%s",
                describe_key_payload(keys),
                len(self._key_index),
                place_id,
            )
            return

    def _resolve_key_name(self, message: Any) -> str | None:
        """Resolve a key name from a message.

        Names come from the operator: they are the same ones the phone app
        shows, so a key renamed in the app is renamed here too, and there is
        nothing to configure.
        """
        return resolve_key_identity(message, self._key_index)

    def _async_handle_place_event(self, data: dict[str, Any]) -> bool:
        """Dispatch an `accessKeyActivated` push, if this is one.

        Returns:
            True when the push was a `placeEvent` and was consumed here, so the
            caller does not also try the call-channel mapping.
        """
        raw = data.get(_EVENT_PUSH_KEY)
        if not isinstance(raw, str) or not raw:
            return False
        event = parse_place_event(raw)
        if event is None:
            # `u` present but unparseable: log the type, never the body — the
            # body is operator text and may embed a key code.
            LOGGER.debug("FCM: placeEvent не разобран (%s) — пропуск", type(raw).__name__)
            return True
        by_type = event["event_type"] == _PUSH_ACCESS_KEY_EVENT
        key_name = self._resolve_key_name(event["message"])
        if not by_type and key_name is None:
            # Neither the type we expect nor a known key in the text: not ours.
            # Still worth logging, because it proves the push channel is alive
            # even when we ignore the event. Body is never logged.
            LOGGER.debug(
                "FCM: placeEvent %s получен и не обрабатывается: %s",
                event["event_type"],
                mask_secrets(event["message"]),
            )
            return True
        # Set before either branch: the content path is the common one on a
        # verified account, and leaving it to the `by_type` branch raised
        # UnboundLocalError exactly there — the event was recognised and then
        # dropped on the way to the entity.
        by_content = not by_type
        if by_type:
            LOGGER.debug(
                "FCM: key activation по типу accessKeyActivated id=%s "
                "source=%s:%s resolved=%s",
                event["event_id"],
                event["event_type"],
                event["source_id"],
                key_name or "NO_LABEL_MATCH",
            )
        else:
            # A door opening identified by its text, under a type the operator
            # did not name accessKeyActivated. Observed on a verified account:
            # the API never returns accessKeyActivated at all, but a plain
            # infoNotification arrives within a second of a key being applied,
            # reading e.g. "... открыта ключом Денис.".
            LOGGER.debug(
                "FCM: placeEvent %s распознан как проход ключом id=%s "
                "source=%s:%s resolved=%s",
                event["event_type"],
                event["event_id"],
                event["source_type"],
                event["source_id"],
                key_name,
            )
        payload: dict[str, Any] = {
            "event_type": EVENT_KEY_ACTIVATED,
            "event_id": event["event_id"],
            "occurred_at": event["timestamp"],
            "place_id": event["place_id"],
            "source_type": event["source_type"],
            "source_id": event["source_id"],
            # The operator's source for these is `billingSystem`, not the
            # intercom, so nothing downstream can match on it. `by_content`
            # tells the entities the identity came from the message text and
            # that the place — not a door — is all we can honestly claim.
            "by_content": by_content,
        }
        if key_name:
            payload["key_name"] = key_name
        async_dispatcher_send(self._hass, SIGNAL_ACCESS_KEY, payload)
        return True
