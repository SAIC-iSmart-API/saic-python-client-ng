import logging

import httpx

from saic_ismart_client_ng.listener import SaicApiListener
from saic_ismart_client_ng.model import SaicApiConfiguration
from saic_ismart_client_ng.net.client import AbstractSaicClient

LOG = logging.getLogger(__name__)


class SaicLoginClient(AbstractSaicClient):
    def __init__(
            self,
            configuration: SaicApiConfiguration,
            listener: SaicApiListener = None,
    ):
        super().__init__(configuration, listener, LOG)
        self.__listener = listener

    async def encrypt_request(self, modified_request: httpx.Request):
        await super().encrypt_request(modified_request)
        modified_request.headers["Authorization"] = "Basic c3dvcmQ6c3dvcmRfc2VjcmV0"
