from __future__ import annotations

from unittest.mock import patch

import pytest

from saic_ismart_client_ng.listener import SaicApiListener


@pytest.fixture
def api_listener() -> SaicApiListener:
    return SaicApiListener()


@pytest.mark.asyncio
async def test_on_request(api_listener: SaicApiListener) -> None:
    with patch.object(api_listener, "on_request") as mocked_api_listener:
        path = "/test/path"
        body = "test body"
        headers = {"Content-Type": "application/json"}

        await mocked_api_listener.on_request(path, body, headers)
        mocked_api_listener.on_request.assert_called_once_with(path, body, headers)


@pytest.mark.asyncio
async def test_on_response(api_listener: SaicApiListener) -> None:
    with patch.object(api_listener, "on_response") as mocked_api_listener:
        path = "/test/path"
        body = "test body"
        headers = {"Content-Type": "application/json"}

        await mocked_api_listener.on_response(path, body, headers)
        mocked_api_listener.on_response.assert_called_once_with(path, body, headers)
