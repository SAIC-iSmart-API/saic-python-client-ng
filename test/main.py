import asyncio
import logging

import httpx

from _net.client.api import SaicApiClient
from crypto_utils import sha256_hex_digest
from model import SaicApiConfiguration
from saic_api import SaicApi


async def get_user_info(login_resp):
    # Example usage
    url = "https://gateway-mg-eu.soimt.com/api.app/v1/user/account/userInfo"
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
    }
    # Create an instance of your custom client
    s = SaicApiClient(login_resp.get("access_token"))

    async with s.client() as client:
        req = httpx.Request("GET", url, headers=headers)
        resp = await client.send(req)
        return resp.json()


async def vehicle_list(login_resp):
    # Example usage
    url = "https://gateway-mg-eu.soimt.com/api.app/v1/vehicle/list"
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
    }
    # Create an instance of your custom client
    s = SaicApiClient(login_resp.get("access_token"))

    async with s.client() as client:
        req = httpx.Request("GET", url, headers=headers)
        resp = await client.send(req)
        return resp.json()


async def fota_list(login_resp, vin):
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
    s = SaicApiClient(login_resp.get("access_token"))
    async with s.client() as client:
        req = httpx.Request("GET", url, headers=headers, params={"vin": sha256_hex_digest(vin)})
        resp = await client.send(req)
        return resp.json()


async def main():
    saic_api = SaicApi(
        SaicApiConfiguration(
            username="xxxx@gmail.com",
            password="XXXXXX",
        )
    )
    login_resp = await saic_api.login()
    vehicle_list_rest = await vehicle_list(login_resp['data'])
    cars = vehicle_list_rest['data']['vinList']
    for car in cars:
        vin_num = car['vin']
        fota_list_resp = await fota_list(login_resp['data'], vin_num)
        print(fota_list_resp)
    print(login_resp)


logging.basicConfig(
    format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG
)

asyncio.run(main())
