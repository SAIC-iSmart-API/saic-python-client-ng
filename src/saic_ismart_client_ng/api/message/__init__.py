from typing import Optional, Union

from saic_ismart_client_ng.api.base import AbstractSaicApi
from saic_ismart_client_ng.api.message.schema import MessageResp, UpateMessageRequest


class SaicMessageApi(AbstractSaicApi):
    async def get_alarm_list(self, *, page_num: int, page_size: int) -> MessageResp:
        return await self.get_message_list(page_num=page_num, page_size=page_size, message_group='ALARM')

    async def get_command_list(self, *, page_num: int, page_size: int) -> MessageResp:
        return await self.get_message_list(page_num=page_num, page_size=page_size, message_group='COMMAND')

    async def get_news_list(self, *, page_num: int, page_size: int) -> MessageResp:
        return await self.get_message_list(page_num=page_num, page_size=page_size, message_group='NEWS')

    async def get_message_list(self, *, page_num: int, page_size: int, message_group: str) -> MessageResp:
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

    async def delete_all_alarms(self):
        return await self.__change_message_status(action='DELETE_ALARM')

    async def delete_all_commands(self):
        return await self.__change_message_status(action='DELETE_COMMAND')

    async def delete_all_news(self):
        return await self.__change_message_status(action='DELETE_NEWS')

    async def read_message(self, *, message_id: Union[str, int]):
        return await self.__change_message_status(message_id=message_id, action='READ')

    async def delete_message(self, *, message_id: Union[str, int]):
        return await self.__change_message_status(message_id=message_id, action='DELETE')

    async def __change_message_status(self, *, action: str, message_id: Optional[Union[str, int]] = None):
        request = UpateMessageRequest(
            actionType=action,
            messageId=message_id,
        )
        return await self.update_message_status(request)

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
