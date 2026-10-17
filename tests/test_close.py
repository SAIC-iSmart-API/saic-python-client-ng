import unittest

from saic_ismart_client_ng import SaicApi
from saic_ismart_client_ng.model import SaicApiConfiguration


class TestClose(unittest.IsolatedAsyncioTestCase):
    async def test_close_is_idempotent(self) -> None:
        api = SaicApi(
            SaicApiConfiguration(username="user", password="pass"),
        )
        await api.close()
        await api.close()
