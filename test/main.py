import asyncio
import logging

import httpx

from crypto_utils import sha256_hex_digest
from saic_ismart_client import SaicApi
from saic_ismart_client.net.client.api import SaicApiClient
from saic_ismart_client.model import SaicApiConfiguration
from saic_ismart_client.api.login.schema import LoginResp


async def fota_list(login_resp: LoginResp, vin: str, config: SaicApiConfiguration):
    # Example usage
    url = "https://gateway-mg-eu.soimt.com/api.app/v1/vehicle/charging/mgmtData"
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/3.14.9",
        "event-id": '0',
    }
    # Create an instance of your custom client
    s = SaicApiClient(configuration=config)
    async with s.client as client:
        req = httpx.Request("GET", url, headers=headers, params={"vin": sha256_hex_digest(vin)})
        resp = await client.send(req)
        return resp.json()


async def main():
    config = SaicApiConfiguration(username="XXXX@gmail.com", password="XXXXXX", )
    saic_api = SaicApi(
        config
    )
    login_resp = await saic_api.login()
    vehicle_list_rest = await saic_api.vehicle_list()
    cars = vehicle_list_rest.vinList
    for car in cars:
        vin_num = car.vin
        status = await saic_api.get_vehicle_status(vin_num)
        print(str(status))
    print(login_resp)


logging.basicConfig(
    format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG
)

asyncio.run(main())
