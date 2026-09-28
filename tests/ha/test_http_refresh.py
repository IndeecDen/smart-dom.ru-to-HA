"""Exercise token rotation with an offline HA transport, including no replay."""
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio
from aiohttp import ClientError
from homeassistant.core import HomeAssistant

from custom_components.my_dom_ru.http import HTTP


@pytest_asyncio.fixture
async def transport(tmp_path):
    hass = HomeAssistant(str(tmp_path))
    user_agent = SimpleNamespace(__str__=lambda self: "my_dom_ru test")
    http = HTTP(hass, user_agent, "old-access", "old-refresh", "2")
    return hass, http


@pytest.mark.asyncio
async def test_refresh_rotates_both_tokens_and_releases(transport):
    hass, http = transport
    response = Mock(status=200, json=AsyncMock(return_value={"accessToken": "new-access", "refreshToken": "new-refresh"}))
    session = Mock(get=AsyncMock(return_value=response))
    saved = Mock()
    http.on_tokens_refreshed = saved
    with patch("custom_components.my_dom_ru.http.async_get_clientsession", return_value=session):
        assert await http._async_refresh("old-access")
    assert http.access_token == "new-access"
    saved.assert_called_once_with("new-access", "new-refresh")
    assert session.get.await_args.kwargs["headers"]["Bearer"] == "old-refresh"
    assert "authorization" not in session.get.await_args.kwargs["headers"]
    assert session.get.await_args.kwargs["allow_redirects"] is False
    response.release.assert_called_once()
    await hass.async_stop()


@pytest.mark.asyncio
async def test_get_is_retried_once_after_401(transport):
    hass, http = transport
    denied = Mock(status=401, ok=False, method="GET", url="https://myhome.proptech.ru/rest/v3/subscriber-places", headers={})
    okay = Mock(status=200, ok=True, method="GET", url="https://myhome.proptech.ru/rest/v3/subscriber-places", headers={})
    refreshed = Mock(status=200, json=AsyncMock(return_value={"accessToken": "new", "refreshToken": "new-refresh"}))
    session = Mock(get=AsyncMock(side_effect=[denied, refreshed, okay]))
    with patch("custom_components.my_dom_ru.http.async_get_clientsession", return_value=session):
        assert await http.get("/rest/v3/subscriber-places") is okay
    assert session.get.await_count == 3
    assert session.get.await_args.kwargs["headers"]["authorization"] == "Bearer new"
    denied.release.assert_called_once()
    refreshed.release.assert_called_once()
    await hass.async_stop()


@pytest.mark.asyncio
async def test_failed_refresh_does_not_loop(transport):
    hass, http = transport
    denied = Mock(status=401, ok=False, method="GET", url="https://myhome.proptech.ru/rest/v3/subscriber-places", headers={})
    refresh_denied = Mock(status=401)
    session = Mock(get=AsyncMock(side_effect=[denied, refresh_denied]))
    with patch("custom_components.my_dom_ru.http.async_get_clientsession", return_value=session):
        with pytest.raises(ClientError):
            await http.get("/rest/v3/subscriber-places")
    assert session.get.await_count == 2
    await hass.async_stop()


@pytest.mark.asyncio
async def test_mutation_is_never_replayed_after_401(transport):
    hass, http = transport
    denied = Mock(status=401, ok=False, method="PUT", url="https://myhome.proptech.ru/rest/v1/example", headers={})
    session = Mock(put=AsyncMock(return_value=denied), get=AsyncMock())
    with patch("custom_components.my_dom_ru.http.async_get_clientsession", return_value=session):
        with pytest.raises(ClientError):
            await http.put("/rest/v1/example", "{}")
    session.put.assert_awaited_once()
    session.get.assert_not_awaited()
    await hass.async_stop()
