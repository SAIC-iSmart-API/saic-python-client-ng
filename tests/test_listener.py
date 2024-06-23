import pytest

from saic_ismart_client_ng.listener import SaicApiListener


@pytest.fixture()
def api_listener():
    return SaicApiListener()


@pytest.mark.asyncio
async def test_on_request(api_listener, mocker):
    mocker.patch.object(api_listener, 'on_request')
    path = "/test/path"
    body = "test body"
    headers = {"Content-Type": "application/json"}

    await api_listener.on_request(path, body, headers)
    api_listener.on_request.assert_called_once_with(path, body, headers)


@pytest.mark.asyncio
async def test_on_response(api_listener, mocker):
    mocker.patch.object(api_listener, 'on_response')
    path = "/test/path"
    body = "test body"
    headers = {"Content-Type": "application/json"}

    await api_listener.on_response(path, body, headers)
    api_listener.on_response.assert_called_once_with(path, body, headers)
