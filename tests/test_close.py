from __future__ import annotations

import unittest

import pytest

from saic_ismart_client_ng import SaicApi
from saic_ismart_client_ng.exceptions import SaicApiClosedException
from saic_ismart_client_ng.model import SaicApiConfiguration


def _build_api() -> SaicApi:
    return SaicApi(
        SaicApiConfiguration(username="user", password="pass"),  # noqa: S106
    )


class TestClose(unittest.IsolatedAsyncioTestCase):
    async def test_close_is_idempotent(self) -> None:
        api = _build_api()
        await api.close()
        await api.close()

    async def test_login_after_close_raises(self) -> None:
        api = _build_api()
        await api.close()
        with pytest.raises(SaicApiClosedException):
            await api.login()
