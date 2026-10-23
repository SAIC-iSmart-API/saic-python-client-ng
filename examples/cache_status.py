from __future__ import annotations

import asyncio
import dataclasses
import datetime as dt
import os
from pathlib import Path

from saic_ismart_client_ng import SaicApi
from saic_ismart_client_ng.model import SaicApiConfiguration


def load_env(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"Missing {path}; copy .env.example to .env and fill it in")
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


async def main() -> None:
    load_env(Path(__file__).parent / ".env")
    api = SaicApi(
        SaicApiConfiguration(
            username=os.environ["SAIC_USER"],
            password=os.environ["SAIC_PASS"],
            region=os.environ.get("SAIC_REGION", "eu"),
        )
    )
    await api.login()
    vin = os.environ.get("SAIC_VIN") or (await api.vehicle_list()).vinList[0].vin
    resp = await api.get_vehicle_status_cached(vin)
    now = dt.datetime.now(dt.timezone.utc)
    if resp.statusTime:
        ts = dt.datetime.fromtimestamp(resp.statusTime, dt.timezone.utc)
        print(f"statusTime: {resp.statusTime} -> {ts.isoformat()} ({now - ts} ago)")
    else:
        print("statusTime: None")
    print("basicVehicleStatus:")
    if resp.basicVehicleStatus:
        for k, v in dataclasses.asdict(resp.basicVehicleStatus).items():
            if v is not None:
                print(f"  {k}: {v}")
    print("onlineStatus:", resp.onlineStatus)
    print("gpsPosition: <omitted>")


asyncio.run(main())
