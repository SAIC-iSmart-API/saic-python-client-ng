import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Union


@dataclass
class MessageEntity:
    content: str = None
    contentId: str = None
    contentIdList: list = field(default_factory=list)
    createTime: int = None
    messageId: Union[str, int] = None
    messageTime: str = None
    messageType: str = None
    readStatus: int = None
    sender: str = None
    showCheckButton: bool = None
    title: str = None
    vin: str = None

    @property
    def message_time(self) -> datetime.datetime:
        return datetime.datetime.strptime(self.messageTime, '%Y-%m-%d %H:%M:%S')  # FIXME

    @property
    def read_status(self) -> str:
        if self.readStatus is None:
            return 'unknown'
        elif self.readStatus == 0:
            return 'unread'
        else:
            return 'read'

    @property
    def details(self) -> str:
        return f'ID: {self.messageId}, Time: {self.message_time}, Type: {self.messageType}, Title: {self.title}, ' \
            + f'Content: {self.content}, Status: {self.read_status}, Sender: {self.sender}, VIN: {self.vin}'


@dataclass
class MessageResp:
    alarmNumber: int = None
    commandNumber: int = None
    messages: List[MessageEntity] = field(default_factory=list)
    newsNumber: int = None
    # notifications: List[Any] = None
    recordsNumber: int = None
    totalNumber: int = None


@dataclass
class UpateMessageRequest:
    actionType: Optional[str] = None
    deviceId: Optional[str] = None
    messageGroup: Optional[str] = None
    messageId: Optional[Union[str, int]] = None
    notificationCount: Optional[int] = None
    pageNum: Optional[int] = None
    pageSize: Optional[int] = None
