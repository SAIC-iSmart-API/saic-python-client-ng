import asyncio
import logging

import httpx

from _net.client.api import SaicApiClient
from crypto_utils import sha256_hex_digest
from model import SaicApiConfiguration
from saic_api import SaicApi
from schema import LoginResp, AlarmType, AlarmSwitchReq, AlarmSwitchDTO


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
    config = SaicApiConfiguration(username="***REMOVED***", password="***REMOVED***", )
    saic_api = SaicApi(
        config
    )
    login_resp = await saic_api.login()
    vehicle_list_rest = await saic_api.vehicle_list()
    cars = vehicle_list_rest.vinList
    for car in cars:
        vin_num = car.vin
        alarm_config = await saic_api.get_alarm_switch(vin_num)
        for alarm in alarm_config.alarmSwitchList:
            alarm_type = alarm.alarmType
            try:
                out = AlarmType(alarm_type)
                alarm_desc = f"{out.name} ({out.value})"
            except ValueError:
                alarm_desc = f"Generic Alarm ({alarm_type})"
            print(f"{alarm_desc} -> {alarm.alarmSwitch}")
        # fota_list_resp = await fota_list(login_resp, vin_num, config)
        req = AlarmSwitchReq(
            vin=vin_num,
            alarmSwitchList=[AlarmSwitchDTO(
                alarmType=AlarmType.ALARM_TYPE_VEHICLE_FAULT.value,
                functionSwitch=1,
                alarmSwitch=1
            )]
        )
        await saic_api.set_alarm_switch(req, vin_num)
        print(vin_num)
    print(login_resp)


logging.basicConfig(
    format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG
)

asyncio.run(main())
