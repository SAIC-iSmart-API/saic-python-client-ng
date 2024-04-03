import asyncio
import logging
import sys

from saic_ismart_client_ng import SaicApi
from saic_ismart_client_ng.model import SaicApiConfiguration


async def main():
    config = SaicApiConfiguration(username="XXXXX@xxxx.com", password="XXXXX", )
    saic_api = SaicApi(
        config
    )
    await saic_api.login()
    while True:
        logging.info("Auth token expires at %s", saic_api.token_expiration)
        vehicle_list_rest = await saic_api.vehicle_list()
        cars = vehicle_list_rest.vinList
        for car in cars:
            vin_num = car.vin
            # vehicle_status = await saic_api.get_vehicle_status(vin_num)
            # logging.info("Battery voltage is %d", vehicle_status.basicVehicleStatus.batteryVoltage)
            # charging_status = await saic_api.get_vehicle_charging_management_data(vin_num)
            # logging.info("Current power is %d", charging_status.rvsChargeStatus.realtimePower)
            logging.info("My VIN is %s", vin_num)
        await asyncio.sleep(10)


logging.basicConfig(
    stream=sys.stdout,
    format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

asyncio.run(main())
