from enum import Enum

from saic_ismart_client_ng.api.vehicle import RvcParamsId


class VehicleWindowId(Enum):
    SUNROOF = RvcParamsId.WINDOW_SUNROOF
    DRIVER = RvcParamsId.WINDOW_DRIVER
    WINDOW_2 = RvcParamsId.WINDOW_2
    WINDOW_3 = RvcParamsId.WINDOW_3
    WINDOW_4 = RvcParamsId.WINDOW_4
