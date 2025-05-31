from __future__ import annotations

from saic_ismart_client_ng.api.base import AbstractSaicApi
from saic_ismart_client_ng.api.message.schema import (
    MessageEntity,
    MessageResp,
    UpateMessageRequest,
)

__all__ = [
    "MessageEntity",
    "MessageResp",
    "UpateMessageRequest",
]


class SaicMessageApi(AbstractSaicApi):
    async def get_alarm_list(
        self, *, page_num: int, page_size: int
    ) -> MessageResp | None:
        return await self.get_message_list(
            page_num=page_num, page_size=page_size, message_group="ALARM"
        )

    async def get_command_list(
        self, *, page_num: int, page_size: int
    ) -> MessageResp | None:
        return await self.get_message_list(
            page_num=page_num, page_size=page_size, message_group="COMMAND"
        )

    async def get_news_list(
        self, *, page_num: int, page_size: int
    ) -> MessageResp | None:
        return await self.get_message_list(
            page_num=page_num, page_size=page_size, message_group="NEWS"
        )

    async def get_message_list(
        self, *, page_num: int, page_size: int, message_group: str
    ) -> MessageResp | None:
        return await self.execute_api_call_with_optional_result(
            "GET",
            "/message/list",
            params={
                "pageNum": page_num,
                "pageSize": page_size,
                "messageGroup": message_group,
            },
            out_type=MessageResp,
        )

    async def delete_all_alarms(self) -> None:
        await self.__change_message_status(action="DELETE_ALARM")

    async def delete_all_commands(self) -> None:
        await self.__change_message_status(action="DELETE_COMMAND")

    async def delete_all_news(self) -> None:
        await self.__change_message_status(action="DELETE_NEWS")

    async def read_message(self, *, message_id: str | int) -> None:
        await self.__change_message_status(message_id=message_id, action="READ")

    async def delete_message(self, *, message_id: str | int) -> None:
        await self.__change_message_status(message_id=message_id, action="DELETE")

    async def __change_message_status(
        self, *, action: str, message_id: str | int | None = None
    ) -> None:
        request = UpateMessageRequest(
            actionType=action,
            messageId=message_id,
        )
        await self.update_message_status(request)

    async def update_message_status(self, data: UpateMessageRequest) -> None:
        await self.execute_api_call_no_result(
            "PUT",
            "/message/status",
            body=data,
        )

    async def get_unread_messages_count(self) -> MessageResp | None:
        return await self.execute_api_call_with_optional_result(
            "GET", "/message/unreadCount", out_type=MessageResp
        )
