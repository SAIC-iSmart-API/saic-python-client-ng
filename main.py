import asyncio
import logging

import httpx

from crypto_utils import sha1_hex_digest, sha256_hex_digest
from net.session.api import SaicApiClient
from net.session.login import SaicLoginClient


async def login(username, password):
    # Example usage
    url = "https://gateway-mg-eu.soimt.com/api.app/v1/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    firebase_device_id = "cqSHOMG1SmK4k-fzAeK6hr:APA91bGtGihOG5SEQ9hPx3Dtr9o9mQguNiKZrQzboa-1C_UBlRZYdFcMmdfLvh9Q_xA8A0dGFIjkMhZbdIXOYnKfHCeWafAfLXOrxBS3N18T4Slr-x9qpV6FHLMhE9s7I6s89k9lU7DD"
    form_body = {
        "grant_type": "password",
        "username": username,
        "password": sha1_hex_digest(password),
        "scope": "all",
        "deviceId": f"{firebase_device_id}###europecar",
        "deviceType": "1",  # 2 for huawei
        "loginType": "2",  # 1 for phone number
        "countryCode": "",  # e.g 39 for italy if we have a phone number
    }
    # Create an instance of your custom session
    async with SaicLoginClient().client() as s:
        req = httpx.Request("POST", url, data=form_body, headers=headers)
        response = await s.send(req)
        return response.json()


async def get_user_info(login_resp):
    # Example usage
    url = "https://gateway-mg-eu.soimt.com/api.app/v1/user/account/userInfo"
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
    }
    # Create an instance of your custom session
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
    # Create an instance of your custom session
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
    # Create an instance of your custom session
    s = SaicApiClient(login_resp.get("access_token"))
    async with s.client() as client:
        req = httpx.Request("GET", url, headers=headers, params={"vin": sha256_hex_digest(vin)})
        resp = await client.send(req)
        return resp.json()


async def main():
    login_resp = await login('xxxxx@gmail.com', 'XXXXXX')
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
