from __future__ import annotations

from enum import Enum


class VehicleLockId(Enum):
    TAILGATE = 2
    DOORS = 3


class TailgateAction(Enum):
    """Open or close a power tailgate.

    The values are what the iSmart app sends (decrypted MG S6 EV traffic, UK).
    """

    OPEN = 1
    CLOSE = 2
