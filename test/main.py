import asyncio
import logging

from model import SaicApiConfiguration
from saic_api import SaicApi


async def main():
    config = SaicApiConfiguration(username="xxxx@gmail.com", password="XXXXXX", )
    saic_api = SaicApi(
        config
    )
    login_resp = await saic_api.login()
    vehicle_list_rest = await saic_api.vehicle_list()
    cars = vehicle_list_rest.vinList
    for car in cars:
        vin_num = car.vin
        # fota_list_resp = await fota_list(login_resp, vin_num, config)
        print(vin_num)
    print(login_resp)


logging.basicConfig(
    format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG
)

asyncio.run(main())
