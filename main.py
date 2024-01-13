from requests import Request

from crypto_utils import sha1_hex_digest, sha256_hex_digest
from net.debug import debug_requests_on, debug_requests_off
from net.session.api import SaicApiSecuritySession
from net.session.login import SaicLoginSecuritySession


def login(username, password):
    # Example usage
    url = "https://gateway-mg-eu.soimt.com/api.app/v1/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/3.14.9",
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
    s = SaicLoginSecuritySession()

    req = Request("POST", url, data=form_body, headers=headers)
    prepared_request = s.prepare_request(req)
    # Make a request using your custom session
    response = s.send(prepared_request)
    if response.ok:
        return response.json()


def get_user_info(login_resp):
    # Example usage
    url = "https://gateway-mg-eu.soimt.com/api.app/v1/user/account/userInfo"
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/3.14.9",
    }
    # Create an instance of your custom session
    s = SaicApiSecuritySession(login_resp.get("access_token"))

    req = Request("GET", url, headers=headers)
    prepared_request = s.prepare_request(req)
    # Make a request using your custom session
    response = s.send(prepared_request)
    if response.ok:
        return response.json()


def vehicle_list(login_resp):
    # Example usage
    url = "https://gateway-mg-eu.soimt.com/api.app/v1/vehicle/list"
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/3.14.9",
    }
    # Create an instance of your custom session
    s = SaicApiSecuritySession(login_resp.get("access_token"))

    req = Request("GET", url, headers=headers)
    prepared_request = s.prepare_request(req)
    # Make a request using your custom session
    response = s.send(prepared_request)
    if response.ok:
        return response.json()


def fota_list(login_resp, vin):
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
    s = SaicApiSecuritySession(login_resp.get("access_token"))

    req = Request("GET", url, headers=headers, params={"vin": sha256_hex_digest(vin)})
    prepared_request = s.prepare_request(req)
    # Make a request using your custom session
    response = s.send(prepared_request)
    if response.ok:
        return response.json()


debug_requests_on()
login_resp = login('', '')['data']

access_token = login_resp.get("access_token")
refresh_token = login_resp.get("refresh_token")

cars = vehicle_list(login_resp)['data']['vinList']
for car in cars:
    vin_num = car['vin']
    fota_list_resp = fota_list(login_resp, vin_num)
    print(fota_list_resp)

debug_requests_off()
