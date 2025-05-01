from __future__ import annotations

import datetime
import json
import unittest

import httpx
import pytest

from saic_ismart_client_ng.net.crypto import get_app_verification_string
from saic_ismart_client_ng.net.httpx import decrypt_httpx_request, encrypt_httpx_request


def test_get_app_verification_string_valid():
    clazz_simple_name = "SampleClass"
    request_path = "/api/v1/data"
    current_ts = "20230514123000"
    tenant_id = "1234"
    content_type = "application/json"
    request_content = '{"key": "value"}'
    user_token = "dummy_token"

    result = get_app_verification_string(
        clazz_simple_name,
        request_path,
        current_ts,
        tenant_id,
        content_type,
        request_content,
        user_token,
    )

    assert result == "afd4eaf98af2d964f8ea840fc144ee7bae95dbeeeb251d5e3a01371442f92eeb"


@pytest.mark.asyncio
async def test_a_request_should_encrypt_properly():
    ts = datetime.datetime.now()
    expected_json = {"change": "me"}
    base_uri = "http://fake.server/"
    original_request = httpx.Request(
        url=f"{base_uri}with/path",
        method="GET",
        params={"vin": "zevin"},
        headers={"Content-Type": "application/json"},
        json=expected_json,
    )
    original_request_content = original_request.content.decode("utf-8").strip()
    region = "EU"
    tenant_id = "2559"
    computed_verification_string = get_app_verification_string(
        "",
        "/with/path?vin=zevin",
        str(int(ts.timestamp() * 1000)),
        tenant_id,
        "application/json",
        original_request_content,
        "",
    )

    await encrypt_httpx_request(
        modified_request=original_request,
        request_timestamp=ts,
        base_uri=base_uri,
        region=region,
        tenant_id=tenant_id,
    )
    assert original_request is not None
    assert region == original_request.headers["REGION"]
    assert tenant_id == original_request.headers["tenant-id"]
    assert original_request.headers["User-Type"] == "app"
    assert str(int(ts.timestamp() * 1000)) == original_request.headers["APP-SEND-DATE"]
    assert original_request.headers["APP-CONTENT-ENCRYPTED"] == "1"
    assert (
        computed_verification_string
        == original_request.headers["APP-VERIFICATION-STRING"]
    )


@pytest.mark.asyncio
async def test_a_request_should_decrypt_properly():
    ts = datetime.datetime.now()
    expected_json = {"change": "me"}
    base_uri = "http://fake.server/"
    original_request = httpx.Request(
        url=f"{base_uri}with/path",
        method="GET",
        params={"vin": "zevin"},
        headers={"Content-Type": "application/json"},
        json=expected_json,
    )
    region = "EU"
    tenant_id = "2559"

    await encrypt_httpx_request(
        modified_request=original_request,
        request_timestamp=ts,
        base_uri=base_uri,
        region=region,
        tenant_id=tenant_id,
    )
    decrypted = await decrypt_httpx_request(original_request, base_uri=base_uri)

    assert decrypted is not None
    decrypted_json = json.loads(decrypted)
    assert expected_json == decrypted_json


def test_with_empty_request_path():
    clazz_simple_name = "SampleClass"
    request_path = ""
    current_ts = "20230514123000"
    tenant_id = "1234"
    content_type = "application/json"
    request_content = '{"key": "value"}'
    user_token = "dummy_token"

    result = get_app_verification_string(
        clazz_simple_name,
        request_path,
        current_ts,
        tenant_id,
        content_type,
        request_content,
        user_token,
    )
    assert result == "ff8cb13ebcce5958e7fbfe602716c653fd72ce78842be87b6d50dccede198735"


def test_with_no_request_content():
    clazz_simple_name = "SampleClass"
    request_path = "/api/v1/data"
    current_ts = "20230514123000"
    tenant_id = "1234"
    content_type = "application/json"
    request_content = ""
    user_token = "dummy_token"

    result = get_app_verification_string(
        clazz_simple_name,
        request_path,
        current_ts,
        tenant_id,
        content_type,
        request_content,
        user_token,
    )
    assert result == "332c85836aa9afc864282436a740eb2cc778fafd1fea74dd887c1f8de5056de0"


if __name__ == "__main__":
    unittest.main()
