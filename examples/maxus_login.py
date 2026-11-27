from __future__ import annotations

import asyncio
import os
from pathlib import Path

from saic_ismart_client_ng import SaicApi
from saic_ismart_client_ng.model import SaicApiConfiguration

if __package__:
    from .example_env import load_env
else:
    from example_env import load_env


async def main() -> None:
    load_env(Path(__file__).parent / ".env")
    api = SaicApi(
        SaicApiConfiguration.maxus_eu(
            os.environ["MAXUS_USER"], os.environ["MAXUS_PASS"]
        )
    )
    try:
        await api.login()
        print("login: OK")
        vehicles = await api.vehicle_list()
        print("vehicles:", len(vehicles.vinList or []))
    finally:
        await api.close()


asyncio.run(main())
