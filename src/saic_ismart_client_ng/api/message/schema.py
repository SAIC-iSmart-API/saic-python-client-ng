from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MessageEntity:
    content: str = None
    contentId: str = None
    contentIdList: list = field(default_factory=list)
    createTime: int = None
    messageId: str = None
    messageTime: str = None
    messageType: str = None
    readStatus: int = None
    sender: str = None
    showCheckButton: bool = None
    title: str = None
    vin: str = None


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
    messageId: Optional[str] = None
    notificationCount: Optional[int] = None
    pageNum: Optional[int] = None
    pageSize: Optional[int] = None