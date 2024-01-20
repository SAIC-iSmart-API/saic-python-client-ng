from dataclasses import dataclass


@dataclass
class GpsPosition:
    @dataclass
    class WayPoint:
        @dataclass
        class Position:
            altitude: int = None
            latitude: int = None
            longitude: int = None

        hdop: int = None
        heading: int = None
        position: Position = None
        satellites: int = None
        speed: int = None

    gpsStatus: int = None
    timeStamp: int = None
    wayPoint: WayPoint = None