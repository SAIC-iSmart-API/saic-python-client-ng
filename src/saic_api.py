import httpx

from _net.client.login import SaicLoginClient
from crypto_utils import sha1_hex_digest
from model import SaicApiConfiguration


class SaicApi:
    def __init__(
            self,
            configuration: SaicApiConfiguration,
    ):
        self.__configuration = configuration
        self.__login_client = SaicLoginClient(configuration)

    async def login(self):
        # Example usage
        url = f"{self.__configuration.base_uri}/oauth/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        firebase_device_id = "cqSHOMG1SmK4k-fzAeK6hr:APA91bGtGihOG5SEQ9hPx3Dtr9o9mQguNiKZrQzboa-1C_UBlRZYdFcMmdfLvh9Q_xA8A0dGFIjkMhZbdIXOYnKfHCeWafAfLXOrxBS3N18T4Slr-x9qpV6FHLMhE9s7I6s89k9lU7DD"
        form_body = {
            "grant_type": "password",
            "username": self.__configuration.username,
            "password": sha1_hex_digest(self.__configuration.password),
            "scope": "all",
            "deviceId": f"{firebase_device_id}###europecar",
            "deviceType": "1",  # 2 for huawei
            "loginType": "2" if self.__configuration.username_is_email else "1",
            "countryCode": "" if self.__configuration.username_is_email else self.__configuration.phone_country_code,
        }
        # Create an instance of your custom client
        async with self.__login_client.client as s:
            req = httpx.Request("POST", url, data=form_body, headers=headers)
            response = await s.send(req)
            return response.json()
