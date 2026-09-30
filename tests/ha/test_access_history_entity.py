"""The access-history entity: source matching and push/poll dedup."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "custom_components"))

from homeassistant.core import HomeAssistant  # noqa: E402
from homeassistant.helpers.entity_platform import AddEntitiesCallback  # noqa: E402

from my_dom_ru.const import EVENT_KEY_ACTIVATED  # noqa: E402
from my_dom_ru.coordinator import (  # noqa: E402
    MyDomRuConfigEntry,
    MyDomRuUpdateCoordinator,
)
from my_dom_ru.event import (  # noqa: E402
    EVENT_CALL_ACCEPTED,
    MyDomRuAccessHistoryEvent,
    MyDomRuPlaceHistoryEvent,
)

LOCK = {
    "place_id": 55,
    "access_control_id": 101,
    "name": "Домофон",
    "entrance_id": None,
}


def make_entity() -> MyDomRuAccessHistoryEvent:
    entity = MyDomRuAccessHistoryEvent(
        MagicMock(spec=MyDomRuUpdateCoordinator),
        LOCK,
        "my_dom_ru_history_event_entry",
    )
    entity.hass = MagicMock(spec=HomeAssistant)
    entity.entity_id = "event.moy_dom_doorofon_access"
    fired: list[tuple[str, dict]] = []
    entity._fired = fired
    entity._trigger_event = lambda event_type, attrs: fired.append(
        (event_type, attrs)
    )
    entity.async_write_ha_state = lambda: None
    return entity


def payload(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "event_type": EVENT_KEY_ACTIVATED,
        "event_id": "e1",
        "occurred_at": 1777213000,
        "place_id": "55",
        "source_type": "accessControl",
        "source_id": "101",
        "key_name": "Сын",
        "by_content": False,
    }
    base.update(overrides)
    return base


class TestSourceMatching:
    def test_key_event_on_access_control_matches(self) -> None:
        entity = make_entity()
        entity._emit(payload())
        assert len(entity._fired) == 1

    def test_key_event_from_subscriber_place_matches(self) -> None:
        # We have no live sample, so a place-scoped source is also accepted
        # when its id is the place this entity belongs to.
        entity = make_entity()
        entity._emit(
            payload(source_type="subscriberPlace", source_id="55")
        )
        assert len(entity._fired) == 1

    def test_key_event_from_other_place_is_ignored(self) -> None:
        entity = make_entity()
        entity._emit(
            payload(source_type="subscriberPlace", source_id="999")
        )
        assert entity._fired == []

    def test_other_intercom_is_ignored(self) -> None:
        entity = make_entity()
        entity._emit(payload(source_id="202"))
        assert entity._fired == []

    def test_other_place_is_ignored(self) -> None:
        entity = make_entity()
        entity._emit(payload(place_id="999"))
        assert entity._fired == []

    def test_call_event_still_matches(self) -> None:
        entity = make_entity()
        entity._emit(
            payload(event_type=EVENT_CALL_ACCEPTED, key_name=None)
        )
        assert entity._fired == [(EVENT_CALL_ACCEPTED, entity._fired[0][1])]

    def test_call_event_from_subscriber_place_is_ignored(self) -> None:
        # The lenient place-source rule applies to key events only; a call
        # must not be attributed to an intercom it did not come from.
        entity = make_entity()
        entity._emit(
            payload(
                event_type=EVENT_CALL_ACCEPTED,
                source_type="subscriberPlace",
                source_id="55",
            )
        )
        assert entity._fired == []

    def test_unrelated_event_type_is_ignored(self) -> None:
        entity = make_entity()
        entity._emit(payload(event_type="motion"))
        assert entity._fired == []


class TestDeduplication:
    def test_same_event_id_from_push_and_poll_fires_once(self) -> None:
        # This is the whole point: the same activation legitimately arrives
        # twice, and a Telegram automation must not notify twice.
        entity = make_entity()
        entity._emit(payload())
        entity._emit(payload())
        assert len(entity._fired) == 1

    def test_different_event_ids_both_fire(self) -> None:
        entity = make_entity()
        entity._emit(payload(event_id="e1"))
        entity._emit(payload(event_id="e2"))
        assert len(entity._fired) == 2

    def test_attributes_expose_key_name(self) -> None:
        entity = make_entity()
        entity._emit(payload())
        _, attributes = entity._fired[0]
        assert attributes["key_name"] == "Сын"
        assert attributes["event_id"] == "e1"
        assert attributes["occurred_at"] == 1777213000

    def test_missing_key_name_is_omitted_not_none(self) -> None:
        # A None attribute would render as "None" in a notification template.
        entity = make_entity()
        entity._emit(payload(key_name=None))
        _, attributes = entity._fired[0]
        assert "key_name" not in attributes

    def test_event_without_id_is_not_deduped(self) -> None:
        # Without a backend id there is nothing stable to compare on, so the
        # event is reported rather than silently swallowed.
        entity = make_entity()
        entity._emit(payload(event_id=""))
        entity._emit(payload(event_id=""))
        assert len(entity._fired) == 2

    def test_recent_id_set_stays_bounded(self) -> None:
        entity = make_entity()
        for index in range(500):
            entity._emit(payload(event_id=f"e{index}"))
        assert len(entity._recent_event_ids) <= 128
        # The newest must survive so a push/poll pair is still deduped.
        assert "e499" in entity._recent_event_ids


class TestPlaceHistorySharesTheBase:
    """The place-level entity must get key events and the same dedup."""
    def make_place_entity(self):
        coordinator = MagicMock(spec=MyDomRuUpdateCoordinator)
        # place_display_name reads coordinator.data when building DeviceInfo.
        coordinator.data = {}
        entity = MyDomRuPlaceHistoryEvent(
            coordinator,
            "account-1",
            "sub-1",
            # Int, exactly as the API delivers it: coordinator reads
            # `place["id"]` straight out of the JSON response.
            55,
            "my_dom_ru_history_event_entry",
            [
                {
                    "place_id": 55,
                    "access_control_id": 101,
                    "name": "Домофон",
                }
            ],
        )
        entity.hass = MagicMock(spec=HomeAssistant)
        entity.entity_id = "event.moy_dom_istoriya"
        fired: list[tuple[str, dict]] = []
        entity._fired = fired
        entity._trigger_event = lambda event_type, attrs: fired.append(
            (event_type, attrs)
        )
        entity.async_write_ha_state = lambda: None
        return entity

    def test_declares_key_activated(self) -> None:
        # Read through an instance: HA's ABCCachedProperties metaclass turns
        # `_attr_*` class attributes into properties on the class itself.
        entity = self.make_place_entity()
        assert EVENT_KEY_ACTIVATED in entity._attr_event_types

    def test_key_event_carries_label_and_intercom_name(self) -> None:
        entity = self.make_place_entity()
        entity._emit(payload())
        _, attributes = entity._fired[0]
        assert attributes["key_name"] == "Сын"
        assert attributes["source_name"] == "Домофон"
        assert attributes["source_id"] == "101"

    def test_dedup_applies_here_too(self) -> None:
        entity = self.make_place_entity()
        entity._emit(payload())
        entity._emit(payload())
        assert len(entity._fired) == 1

    def test_unknown_intercom_is_ignored(self) -> None:
        entity = self.make_place_entity()
        entity._emit(payload(source_id="999"))
        assert entity._fired == []

    def test_int_place_id_from_api_is_normalized(self) -> None:
        # Regression: with the raw int 55 kept, `source_key[0] != _place_id`
        # compared "55" to 55 and the entity silently never fired.
        entity = self.make_place_entity()
        assert entity._place_id == "55"
        entity._emit(
            payload(
                event_type=EVENT_CALL_ACCEPTED,
                source_id="101",
            )
        )
        assert len(entity._fired) == 1

    def test_content_key_event_from_billing_source_is_owned(self) -> None:
        # Verified on a real account: the operator files key openings under
        # source=billingSystem and names the address, so nothing matches an
        # intercom. The place-level stream is where it can be reported.
        entity = self.make_place_entity()
        entity._emit(
            payload(source_type="billingSystem", source_id="18", by_content=True)
        )
        assert len(entity._fired) == 1

    def test_content_key_event_omits_intercom_name(self) -> None:
        # There is no intercom to name, so the attribute must be absent rather
        # than a wrong one.
        entity = self.make_place_entity()
        entity._emit(
            payload(source_type="billingSystem", source_id="18", by_content=True)
        )
        _, attributes = entity._fired[0]
        assert "source_name" not in attributes
        assert attributes["key_name"] == "Сын"

    def test_content_key_event_of_another_place_is_ignored(self) -> None:
        entity = self.make_place_entity()
        entity._emit(
            payload(
                place_id="999",
                source_type="billingSystem",
                source_id="18",
                by_content=True,
            )
        )
        assert entity._fired == []


class TestIntercomClaimsContentKeyEvent:
    """An intercom may claim a key event only when the door is unambiguous."""

    def make_sole(self):
        entity = MyDomRuAccessHistoryEvent(
            MagicMock(spec=MyDomRuUpdateCoordinator),
            LOCK,
            "sig",
            sole_intercom=True,
        )
        entity.hass = MagicMock(spec=HomeAssistant)
        fired: list[tuple[str, dict]] = []
        entity._fired = fired
        entity._trigger_event = lambda event_type, attrs: fired.append(
            (event_type, attrs)
        )
        entity.async_write_ha_state = lambda: None
        return entity

    def test_sole_intercom_claims_it(self) -> None:
        entity = self.make_sole()
        entity._emit(
            payload(source_type="billingSystem", source_id="18", by_content=True)
        )
        assert len(entity._fired) == 1

    def test_one_of_several_intercoms_does_not(self) -> None:
        # With more than one door, claiming it on one of them would be a guess.
        entity = MyDomRuAccessHistoryEvent(
            MagicMock(spec=MyDomRuUpdateCoordinator),
            LOCK,
            "sig",
            sole_intercom=False,
        )
        entity.hass = MagicMock(spec=HomeAssistant)
        fired: list[tuple[str, dict]] = []
        entity._fired = fired
        entity._trigger_event = lambda event_type, attrs: fired.append(
            (event_type, attrs)
        )
        entity.async_write_ha_state = lambda: None
        entity._emit(
            payload(source_type="billingSystem", source_id="18", by_content=True)
        )
        assert fired == []


@pytest.mark.asyncio
class TestSoleIntercomIsComputedFromApiTypes:
    """The wiring that decides whether a door may claim a key event.

    `async_setup_entry` counts distinct access controls per place to derive
    `sole_intercom`. Both ids arrive from the JSON API as *numbers*, and the
    counting map used to keep them raw while the lookup went through `str()`,
    so the lookup never matched and `sole_intercom` was silently `False` on
    every install. The intercom entity then stayed mute for key openings even
    on an account with exactly one door — while its own tests, which pass
    `sole_intercom` directly, were all green.
    """

    LOCKS_ONE = [
        {
            "place_id": 55,
            "access_control_id": 101,
            "name": "Домофон",
            "entrance_id": None,
        }
    ]
    LOCKS_TWO = [
        {
            "place_id": 55,
            "access_control_id": 101,
            "name": "Первый",
            "entrance_id": 1,
        },
        {
            "place_id": 55,
            "access_control_id": 202,
            "name": "Второй",
            "entrance_id": 2,
        },
    ]

    async def collect(self, locks: list[dict]) -> list:
        from unittest.mock import patch

        from my_dom_ru.const import CONF_ACCOUNT_ID, CONF_SUBSCRIBER_ID
        from my_dom_ru.event import async_setup_entry

        coordinator = MagicMock(spec=MyDomRuUpdateCoordinator)
        coordinator.data = {"locks": locks, "cameras": []}
        entry = MagicMock()
        entry.entry_id = "entry-1"
        entry.runtime_data = coordinator
        entry.data = {
            CONF_ACCOUNT_ID: "482631118701",
            CONF_SUBSCRIBER_ID: "6095505",
        }

        added: list = []
        with (
            patch("my_dom_ru.event.place_device_id", return_value=None),
            patch("my_dom_ru.event._migrate_single_place_account_history_entity"),
        ):
            await async_setup_entry(
                MagicMock(spec=HomeAssistant), entry, added.extend
            )
        return added

    async def test_single_intercom_with_numeric_ids_may_claim(self) -> None:
        added = await self.collect(self.LOCKS_ONE)
        access = [
            entity
            for entity in added
            if isinstance(entity, MyDomRuAccessHistoryEvent)
        ]
        assert len(access) == 1
        assert access[0]._sole_intercom is True

    async def test_two_intercoms_may_not_claim(self) -> None:
        added = await self.collect(self.LOCKS_TWO)
        access = [
            entity
            for entity in added
            if isinstance(entity, MyDomRuAccessHistoryEvent)
        ]
        assert len(access) == 2
        assert all(entity._sole_intercom is False for entity in access)

    async def test_the_wired_entity_reports_the_opening(self) -> None:
        # End of the chain: the entity built by setup, fed the payload the push
        # actually delivers, must fire rather than drop it.
        added = await self.collect(self.LOCKS_ONE)
        entity = next(
            entity
            for entity in added
            if isinstance(entity, MyDomRuAccessHistoryEvent)
        )
        entity.hass = MagicMock(spec=HomeAssistant)
        fired: list[tuple[str, dict]] = []
        entity._trigger_event = lambda event_type, attrs: fired.append(
            (event_type, attrs)
        )
        entity.async_write_ha_state = lambda: None
        entity._emit(
            payload(source_type="billingSystem", source_id="18", by_content=True)
        )
        assert len(fired) == 1
        assert fired[0][0] == EVENT_KEY_ACTIVATED
