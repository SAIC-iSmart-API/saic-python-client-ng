from dataclasses import dataclass, field
from enum import Enum
from typing import List


class AlarmType(Enum):
    ALARM_TYPE_VEHICLE_FAULT = 0
    ALARM_TYPE_GEOFENCE = 2
    ALARM_TYPE_VEHICLE_START = 3


@dataclass
class AlarmSwitch:
    alarmType: int = None
    functionSwitch: int = None
    alarmSwitch: int = None


@dataclass
class AlarmSwitchResp:
    alarmSwitchList: List[AlarmSwitch] = field(default_factory=list)


@dataclass
class AlarmSwitchReq:
    vin: str
    alarmSwitchList: List[AlarmSwitch] = field(default_factory=list)
