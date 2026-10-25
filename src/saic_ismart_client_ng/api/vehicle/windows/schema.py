from __future__ import annotations

from enum import Enum

from saic_ismart_client_ng.api.vehicle import RvcParamsId


class VehicleWindowId(Enum):
    SUNROOF = RvcParamsId.WINDOW_SUNROOF
    DRIVER = RvcParamsId.WINDOW_DRIVER
    WINDOW_2 = RvcParamsId.WINDOW_2
    WINDOW_3 = RvcParamsId.WINDOW_3
    WINDOW_4 = RvcParamsId.WINDOW_4


class DoorWindowsAction(Enum):
    """What to do with all four door windows at once.

    The values are what the iSmart app sends (decrypted MG S6 EV traffic).
    The car reports ventilated and fully open windows the same way in its
    status, so the two can't be told apart afterwards.
    """

    CLOSE = 0
    VENTILATE = 1  # open a few centimetres
    OPEN = 2  # fully open
