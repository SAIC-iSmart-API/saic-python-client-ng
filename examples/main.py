from __future__ import annotations

import asyncio
from dataclasses import asdict
import logging
import os
from pathlib import Path
import sys

from saic_ismart_client_ng import SaicApi
from saic_ismart_client_ng.model import SaicApiConfiguration

if __package__:
    from .example_env import load_env
else:
    from example_env import load_env


async def main() -> None:
    load_env(Path(__file__).parent / ".env")
    config = SaicApiConfiguration(
        username=os.environ.get("SAIC_USER"),
        username_is_email=os.environ.get("SAIC_USERNAME_IS_EMAIL", "false").lower()
        in ("1", "true", "yes"),
        password=os.environ.get("SAIC_PASS"),
        base_uri=os.environ.get(
            "SAIC_BASE_URI", "https://gateway-mg-th.soimt.com/api.app/v1/"
        ),
        region=os.environ.get("SAIC_REGION", "th"),
        phone_country_code=os.environ.get("SAIC_PHONE_COUNTRY_CODE", "66"),
        device_app_id=os.environ.get("SAIC_DEVICE_APP_ID", "com.saicmotor.ismartthai"),
        login_authorization=os.environ.get("SAIC_LOGIN_AUTHORIZATION"),
    )
    saic_api = SaicApi(config)
    await saic_api.login()
    while True:
        logging.info("Auth token expires at %s", saic_api.token_expiration)
        vehicle_list_rest = await saic_api.vehicle_list()
        cars = vehicle_list_rest.vinList
        for car in cars:
            vin_num = car.vin
            if not vin_num:
                logging.warning("Vehicle list entry has no VIN; skipping status requests")
                continue
            logging.info("My VIN is %s", vin_num)
            vehicle_status = await saic_api.get_vehicle_status(vin_num)
            if vehicle_status.basicVehicleStatus is None:
                logging.info("No basicVehicleStatus")
            else:
                for name, value in asdict(vehicle_status.basicVehicleStatus).items():
                    logging.info("basicVehicleStatus.%s = %s", name, value)
            charging_status = await saic_api.get_vehicle_charging_management_data(vin_num)

            chrg_mgmt_data = charging_status.chrgMgmtData
            if chrg_mgmt_data is None:
                logging.info("No chrgMgmtData")
                continue
            for name, value in asdict(chrg_mgmt_data).items():
                logging.info("chrgMgmtData.%s = %s", name, value)
            logging.info("decoded_current = %s A", chrg_mgmt_data.decoded_current)
            logging.info("decoded_voltage = %s V", chrg_mgmt_data.decoded_voltage)
            logging.info("decoded_power = %s kW", chrg_mgmt_data.decoded_power)
        await asyncio.sleep(10)


if __name__ == "__main__":
    logging.basicConfig(
        stream=sys.stdout,
        format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
    )

    asyncio.run(main())
