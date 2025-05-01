from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


@dataclass
class LoginResp:
    @dataclass
    class LoginRespDetail:
        languageType: str | None = None

    access_token: str | None = None
    account: str | None = None
    avatar: str | None = None
    client_id: str | None = None
    dept_id: str | None = None
    detail: LoginRespDetail | None = None
    expires_in: int | None = None
    jti: str | None = None
    languageType: str | None = None
    license: str | None = None
    oauth_id: str | None = None
    post_id: str | None = None
    refresh_token: str | None = None
    role_id: str | None = None
    role_name: str | None = None
    scope: str | None = None
    tenant_id: str | None = None
    token_type: str | None = None
    user_id: str | None = None
    user_name: str | None = None


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
            altitude: int | None = None
            latitude: int | None = None
            longitude: int | None = None

        hdop: int | None = None
        heading: int | None = None
        position: Position | None = None
        satellites: int | None = None
        speed: int | None = None

    gpsStatus: int | None = None
    timeStamp: int | None = None
    wayPoint: WayPoint | None = None

    @property
    def gps_status_decoded(self) -> GpsStatus | None:
        value = self.gpsStatus
        if value is None:
            return None
        try:
            return GpsStatus(value)
        except ValueError:
            logger.error("Could not decode %s as GpsStatus", value)
            return None
