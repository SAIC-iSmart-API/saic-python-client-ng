from __future__ import annotations

from enum import Enum

from saic_ismart_client_ng.api.vehicle.schema import RvcParamsId


class HeatedSeat(Enum):
    """A single heated seat, by the parameter the iSmart app uses for it."""

    FRONT_LEFT = RvcParamsId.HEATED_SEAT_DRIVER
    FRONT_RIGHT = RvcParamsId.HEATED_SEAT_PASSENGER
    REAR_LEFT = RvcParamsId.HEATED_SEAT_REAR_LEFT
    REAR_RIGHT = RvcParamsId.HEATED_SEAT_REAR_RIGHT


# Rear seats are on/off only; the iSmart app sends this level for "on".
REAR_HEATED_SEAT_ON_LEVEL = 3
