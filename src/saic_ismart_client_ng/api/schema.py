import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class LoginResp:
    @dataclass
    class LoginRespDetail:
        languageType: Optional[str] = None

    access_token: Optional[str] = None
    account: Optional[str] = None
    avatar: Optional[str] = None
    client_id: Optional[str] = None
    dept_id: Optional[str] = None
    detail: Optional[LoginRespDetail] = None
    expires_in: Optional[int] = None
    jti: Optional[str] = None
    languageType: Optional[str] = None
    license: Optional[str] = None
    oauth_id: Optional[str] = None
    post_id: Optional[str] = None
    refresh_token: Optional[str] = None
    role_id: Optional[str] = None
    role_name: Optional[str] = None
    scope: Optional[str] = None
    tenant_id: Optional[str] = None
    token_type: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None


class GpsStatus(Enum):
    NO_SIGNAL = 0
    TIME_FIX = 1
    FIX_2D = 2
    FIX_3d = 3


@dataclass
class GpsPosition:
    @dataclass
    class WayPoint:
        @dataclass
        class Position:
            altitude: Optional[int] = None
            latitude: Optional[int] = None
            longitude: Optional[int] = None

        hdop: Optional[int] = None
        heading: Optional[int] = None
        position: Optional[Position] = None
        satellites: Optional[int] = None
        speed: Optional[int] = None

    gpsStatus: Optional[int] = None
    timeStamp: Optional[int] = None
    wayPoint: Optional[WayPoint] = None

    @property
    def gps_status_decoded(self) -> Optional[GpsStatus]:
        value = self.gpsStatus
        if value is None:
            return None
        try:
            return GpsStatus(value)
        except ValueError:
            logger.error(f"Could not decode {value} as GpsStatus")
            return None
