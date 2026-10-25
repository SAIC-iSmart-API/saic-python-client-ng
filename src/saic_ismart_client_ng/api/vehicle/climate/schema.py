from __future__ import annotations

from enum import Enum

from saic_ismart_client_ng.api.vehicle.schema import RvcParamsId


class HeatedSeat(Enum):
    """A single heated seat, by the parameter the iSmart app uses for it.

    Left and right are the physical sides of the car, the same on left- and
    right-hand drive cars. They match ``frontLeftSeatHeatLevel`` /
    ``frontRightSeatHeatLevel`` in the vehicle status.
    """

    FRONT_LEFT = RvcParamsId.HEATED_SEAT_FRONT_LEFT
    FRONT_RIGHT = RvcParamsId.HEATED_SEAT_FRONT_RIGHT
    REAR_LEFT = RvcParamsId.HEATED_SEAT_REAR_LEFT
    REAR_RIGHT = RvcParamsId.HEATED_SEAT_REAR_RIGHT


# Rear seats are on/off only; the iSmart app sends this level for "on".
REAR_HEATED_SEAT_ON_LEVEL = 3


class VentilatedSeat(Enum):
    """A single ventilated seat, by the parameter the iSmart app uses for it.

    Left and right are the physical sides of the car. They match
    ``frontLeftSeatVentLevel`` / ``frontRightSeatVentLevel`` and
    ``secondRowLeftSeatVentLevel`` / ``secondRowRightSeatVentLevel`` in the
    vehicle status.
    """

    FRONT_LEFT = RvcParamsId.SEAT_VENTILATION_FRONT_LEFT
    FRONT_RIGHT = RvcParamsId.SEAT_VENTILATION_FRONT_RIGHT
    REAR_LEFT = RvcParamsId.SEAT_VENTILATION_REAR_LEFT
    REAR_RIGHT = RvcParamsId.SEAT_VENTILATION_REAR_RIGHT


# Seats with a single ventilation level (on/off only) take this level for "on".
ONE_LEVEL_VENTILATED_SEAT_ON_LEVEL = 3
