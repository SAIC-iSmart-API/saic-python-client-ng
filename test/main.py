import asyncio
import logging

from saic_ismart_client_ng import SaicApi
from saic_ismart_client_ng.model import SaicApiConfiguration


async def main():
    config = SaicApiConfiguration(username="XXXXX@xxxx.com", password="XXXXX", )
    saic_api = SaicApi(
        config
    )
    await saic_api.login()
    vehicle_list_rest = await saic_api.vehicle_list()
    cars = vehicle_list_rest.vinList
    for car in cars:
        vin_num = car.vin
        status = await saic_api.get_vehicle_charging_management_data(vin_num)
        print(str(status))


logging.basicConfig(
    format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG
)

asyncio.run(main())
