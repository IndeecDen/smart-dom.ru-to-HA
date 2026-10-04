"""Key caches survive failures without mixing names between addresses."""
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from custom_components.my_dom_ru.access_keys import refresh_place_key_indexes
from custom_components.my_dom_ru.fcm import DoorbellFcmListener
from custom_components.my_dom_ru.api import MyDomRuAPI


@pytest.mark.asyncio
async def test_refreshes_all_places_and_isolates_failures():
    api = SimpleNamespace(query_access_keys=AsyncMock(side_effect=[
        RuntimeError("offline"), [],
        [{"accessKey": {"accessKeyCode": "ABCD1234", "name": "Гость"}}],
    ]))
    previous = {"1": {"Денис": "Денис"}, "2": {"Удалён": "Удалён"}, "9": {}}
    result = await refresh_place_key_indexes(
        api, {"places": [{"place": {"id": i}} for i in (1, 2, 3)]}, previous,
    )
    assert result["1"] == previous["1"]
    assert result["2"] == {}
    assert result["3"]["ABCD1234"] == "Гость"
    assert "9" not in result
    assert api.query_access_keys.await_args_list == [call(1), call(2), call(3)]


@pytest.mark.asyncio
async def test_fcm_timer_accepts_time_and_keeps_place_scoped_names():
    api = SimpleNamespace(query_access_keys=AsyncMock(side_effect=[
        [{"accessKey": {"accessKeyCode": "ABCD1234", "name": "Первый"}}],
        [{"accessKey": {"accessKeyCode": "ABCD1234", "name": "Второй"}}],
    ]))
    coordinator = SimpleNamespace(data={"places": [{"place": {"id": i}} for i in (1, 2)]})
    listener = DoorbellFcmListener(MagicMock(), MagicMock(), api, coordinator)
    await listener.async_refresh_key_index(datetime.now(UTC))
    assert listener._resolve_key_name("ключом ABCD1234", "1") == "Первый"
    assert listener._resolve_key_name("ключом ABCD1234", "2") == "Второй"
    assert listener._resolve_key_name("ключом Первый", "2") is None
    api.query_access_keys.side_effect = [None, []]
    await listener.async_refresh_key_index(datetime.now(UTC))
    assert listener._resolve_key_name("ключом ABCD1234", "1") == "Первый"
    assert listener._resolve_key_name("ключом ABCD1234", "2") is None


@pytest.mark.asyncio
async def test_api_distinguishes_empty_keys_from_unavailable_lookup():
    api = MyDomRuAPI.__new__(MyDomRuAPI)
    api.http = MagicMock()
    with patch("custom_components.my_dom_ru.app_api.AppApi.execute", new_callable=AsyncMock) as execute:
        execute.return_value = []
        assert await api.query_access_keys(55) == []
        execute.side_effect = TimeoutError()
        assert await api.query_access_keys(55) is None
