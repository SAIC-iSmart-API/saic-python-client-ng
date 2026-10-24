from __future__ import annotations

import asyncio
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
