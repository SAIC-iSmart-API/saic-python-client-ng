from saic_ismart_client_ng.api.base import AbstractSaicApi
from saic_ismart_client_ng.api.message.schema import MessageResp, UpateMessageRequest


class SaicMessageApi(AbstractSaicApi):

    async def get_message_list(self, page_num: int, page_size: int, message_group: str) -> MessageResp:
        return await self.execute_api_call(
            "GET",
            "/message/list",
            params={
                "pageNum": page_num,
                "pageSize": page_size,
                "messageGroup": message_group,
            },
            out_type=MessageResp
        )

    async def update_message_status(self, data: UpateMessageRequest):
        return await self.execute_api_call(
            "PUT",
            "/message/status",
            body=data,
        )

    async def get_unread_messages_count(self) -> MessageResp:
        return await self.execute_api_call(
            "GET",
            "/message/unreadCount",
            out_type=MessageResp
        )
