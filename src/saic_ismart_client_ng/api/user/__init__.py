from saic_ismart_client_ng.api.base import AbstractSaicApi
from saic_ismart_client_ng.api.user.schema import UserTimezoneResp


class SaicUserApi(AbstractSaicApi):

    async def get_user_timezone(self) -> UserTimezoneResp:
        return await self.execute_api_call(
            "GET",
            "/user/timezone",
            out_type=UserTimezoneResp
        )
