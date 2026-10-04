"""Exercise the WebSocket browse path independently from live entity triggers."""
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.my_dom_ru.api import HistoryEvent, HistoryPage
from custom_components.my_dom_ru.history_ws import HistoryBrowseTarget, async_handle_history
from homeassistant.exceptions import Unauthorized


@pytest.mark.asyncio
@pytest.mark.parametrize(("aggregate", "doors", "expected"), [
    (True, 1, True), (False, 1, True), (True, 2, True), (False, 2, False),
])
async def test_browse_content_key_event(aggregate, doors, expected):
    locks = [{"place_id": 55, "access_control_id": i, "name": f"Дверь {i}"}
             for i in range(1, doors + 1)]
    event = HistoryEvent(id="key-1", place_id="55", event_type="infoNotification",
                         timestamp=1770000000, source_type="billingSystem", source_id="18",
                         message="Адрес открыт ключом Денис")
    coordinator = SimpleNamespace(
        data={"locks": locks},
        api=SimpleNamespace(
            query_events=AsyncMock(return_value=HistoryPage(events=(event,), number=0, last=True)),
            query_access_keys=AsyncMock(return_value=[
                {"accessKey": {"accessKeyCode": "ABCD1234", "name": "Денис"}},
            ]),
        ),
    )
    target = HistoryBrowseTarget(coordinator, ("55",), {("55", "1"): "Дверь 1"}, "Адрес", aggregate)
    connection = MagicMock()
    with patch("custom_components.my_dom_ru.history_ws._resolve_target", return_value=target):
        await async_handle_history(MagicMock(), connection, {"id": 1, "entity_id": "event.test", "page": 0})
    rows = connection.send_result.call_args.args[1]["events"]
    assert bool(rows) is expected
    if expected:
        assert rows[0]["event_type"] == "key_activated"
        assert rows[0]["key_name"] == "Денис"
        assert "message" not in rows[0]
        assert "ABCD1234" not in str(rows)
        if aggregate:
            assert rows[0]["source_id"] == ("1" if doors == 1 else "")


@pytest.mark.asyncio
async def test_browse_keeps_calls_on_key_lookup_failure_and_drops_foreign_rows():
    def event(event_id, place, kind, message=""):
        return HistoryEvent(id=event_id, place_id=place, event_type=kind,
                            timestamp=1770000000, source_type="accessControl",
                            source_id="1", message=message)

    coordinator = SimpleNamespace(
        data={"locks": [{"place_id": 55, "access_control_id": 1}]},
        api=SimpleNamespace(
            query_events=AsyncMock(return_value=HistoryPage(events=(
                event("call", "55", "accessControlCallMissed"),
                event("typed", "55", "accessKeyActivated"),
                event("unmatched", "55", "infoNotification", "ключом Денис"),
                event("foreign", "99", "accessKeyActivated"),
            ), number=0, last=True)),
            query_access_keys=AsyncMock(side_effect=TimeoutError()),
        ),
    )
    target = HistoryBrowseTarget(coordinator, ("55",), {("55", "1"): "Дверь"}, "Адрес", True)
    connection = MagicMock()
    with patch("custom_components.my_dom_ru.history_ws._resolve_target", return_value=target):
        await async_handle_history(MagicMock(), connection, {"id": 1, "entity_id": "event.test", "page": 0})
    rows = connection.send_result.call_args.args[1]["events"]
    assert [row["event_id"] for row in rows] == ["call", "typed"]
    assert all("key_name" not in row for row in rows)


@pytest.mark.asyncio
async def test_browse_requires_entity_read_access_before_resolving_target():
    connection = MagicMock()
    connection.user.is_admin = False
    connection.user.permissions.check_entity.return_value = False
    with patch("custom_components.my_dom_ru.history_ws._resolve_target") as resolve:
        with pytest.raises(Unauthorized):
            await async_handle_history(MagicMock(), connection, {"id": 1, "entity_id": "event.test", "page": 0})
    resolve.assert_not_called()
