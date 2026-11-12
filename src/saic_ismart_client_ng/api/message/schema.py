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
        """The message time, or the current local time if there isn't one.

        Falling back to now() means a message with no time looks brand new.
        Prefer ``message_time_or_none`` or ``create_time_utc`` when that
        matters (e.g. deciding whether a message is old).
        """
        parsed = self.message_time_or_none
        if parsed is not None:
            return parsed
        return datetime.datetime.now()

    @property
    def message_time_or_none(self) -> datetime.datetime | None:
        """``messageTime`` parsed, or None if it is missing or unreadable.

        The result is naive: SAIC sends it in the server's local time with no
        timezone (the EU servers use CET/CEST), so it can't safely be compared
        with UTC. Use ``create_time_utc`` for that.
        """
        if not self.messageTime:
            return None
        for date_format in MESSAGE_DATE_TIME_FORMATS:
            try:
                return datetime.datetime.strptime(self.messageTime, date_format)
            except ValueError:
                pass
        LOGGER.error(
            "Could not parse messageTime '%s'. This is a bug. Please file a ticket",
            self.messageTime,
        )
        return None

    @property
    def create_time_utc(self) -> datetime.datetime | None:
        """``createTime`` (Unix milliseconds) as a UTC datetime, or None.

        None when the message has no createTime (common on EU accounts) or
        it can't be read. Unlike ``messageTime`` this has no timezone doubt.
        """
        if self.createTime is None:
            return None
        try:
            return datetime.datetime.fromtimestamp(
                self.createTime / 1000.0, tz=datetime.UTC
            )
        except (TypeError, OSError, OverflowError, ValueError):
            return None

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
