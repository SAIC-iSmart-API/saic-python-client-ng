import httpx

from crypto_utils import sha1_hex_digest
from saic_ismart_client.api.base import AbstractSaicApi
from saic_ismart_client.api.login.schema import LoginResp


class SaicLoginApi(AbstractSaicApi):
    async def login(self) -> LoginResp:
        url = f"{self.configuration.base_uri}oauth/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        firebase_device_id = "cqSHOMG1SmK4k-fzAeK6hr:APA91bGtGihOG5SEQ9hPx3Dtr9o9mQguNiKZrQzboa-1C_UBlRZYdFcMmdfLvh9Q_xA8A0dGFIjkMhZbdIXOYnKfHCeWafAfLXOrxBS3N18T4Slr-x9qpV6FHLMhE9s7I6s89k9lU7DD"
        form_body = {
            "grant_type": "password",
            "username": self.configuration.username,
            "password": sha1_hex_digest(self.configuration.password),
            "scope": "all",
            "deviceId": f"{firebase_device_id}###europecar",
            "deviceType": "1",  # 2 for huawei
            "loginType": "2" if self.configuration.username_is_email else "1",
            "countryCode": "" if self.configuration.username_is_email else self.configuration.phone_country_code,
        }

        req = httpx.Request("POST", url, data=form_body, headers=headers)
        response = await self.login_client.client.send(req)
        result = self.deserialize(response, LoginResp)
        # Update the user token
        self.api_client.user_token = result.access_token
        return result
