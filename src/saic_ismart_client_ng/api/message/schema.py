from __future__ import annotations

from dataclasses import dataclass, field
import datetime
import logging
from typing import Any

LOGGER = logging.getLogger(__name__)

# The API returns date-times inconsistently. This is terrible a workaround.
MESSAGE_DATE_TIME_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%d-%m-%Y %H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
]


@dataclass
class MessageEntity:
    content: str | None = None
    contentId: str | None = None
    contentIdList: list[Any] = field(default_factory=list)
    createTime: int | None = None
    messageId: str | int | None = None
    messageTime: str | None = None
    messageType: str | None = None
    readStatus: int | None = None
    sender: str | None = None
    showCheckButton: bool | None = None
    title: str | None = None
    vin: str | None = None

    @property
    def message_time(self) -> datetime.datetime:
        if self.messageTime:
            for date_format in MESSAGE_DATE_TIME_FORMATS:
                try:
                    return datetime.datetime.strptime(self.messageTime, date_format)
                except ValueError:
                    pass
            LOGGER.error(
                "Could not parse messageTime '%s'. This is a bug. Please file a ticket",
                self.messageTime,
            )
        return datetime.datetime.now()

    @property
    def read_status(self) -> str:
        if self.readStatus is None:
            return "unknown"
        if self.readStatus == 0:
            return "unread"
        return "read"

    @property
    def details(self) -> str:
        return (
            f"ID: {self.messageId}, Time: {self.message_time}, Type: {self.messageType}, Title: {self.title}, "
            f"Content: {self.content}, Status: {self.read_status}, Sender: {self.sender}, VIN: {self.vin}"
        )


@dataclass
class MessageResp:
    alarmNumber: int | None = None
    commandNumber: int | None = None
    messages: list[MessageEntity] = field(default_factory=list)
    newsNumber: int | None = None
    # notifications: List[Any] = None
    recordsNumber: int | None = None
    totalNumber: int | None = None


@dataclass
class UpateMessageRequest:
    actionType: str | None = None
    deviceId: str | None = None
    messageGroup: str | None = None
    messageId: str | int | None = None
    notificationCount: int | None = None
    pageNum: int | None = None
    pageSize: int | None = None
