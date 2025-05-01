from __future__ import annotations

from dataclasses import dataclass, field
import datetime
import logging
from typing import List, Optional, Union

LOGGER = logging.getLogger(__name__)

# FIXME: The API returns date-times inconsistently. This is terrible a workaround.
MESSAGE_DATE_TIME_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%d-%m-%Y %H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
]


@dataclass
class MessageEntity:
    content: Optional[str] = None
    contentId: Optional[str] = None
    contentIdList: list = field(default_factory=list)
    createTime: Optional[int] = None
    messageId: Union[str, int, None] = None
    messageTime: Optional[str] = None
    messageType: Optional[str] = None
    readStatus: Optional[int] = None
    sender: Optional[str] = None
    showCheckButton: Optional[bool] = None
    title: Optional[str] = None
    vin: Optional[str] = None

    @property
    def message_time(self) -> datetime.datetime:
        if self.messageTime:
            for date_format in MESSAGE_DATE_TIME_FORMATS:
                try:
                    parsed_date = datetime.datetime.strptime(
                        self.messageTime, date_format
                    )
                    return parsed_date
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
            + f"Content: {self.content}, Status: {self.read_status}, Sender: {self.sender}, VIN: {self.vin}"
        )


@dataclass
class MessageResp:
    alarmNumber: Optional[int] = None
    commandNumber: Optional[int] = None
    messages: List[MessageEntity] = field(default_factory=list)
    newsNumber: Optional[int] = None
    # notifications: List[Any] = None
    recordsNumber: Optional[int] = None
    totalNumber: Optional[int] = None


@dataclass
class UpateMessageRequest:
    actionType: Optional[str] = None
    deviceId: Optional[str] = None
    messageGroup: Optional[str] = None
    messageId: Optional[Union[str, int]] = None
    notificationCount: Optional[int] = None
    pageNum: Optional[int] = None
    pageSize: Optional[int] = None
