from __future__ import annotations

import hashlib
import hmac
import logging
from typing import TYPE_CHECKING

from saic_ismart_client_ng.crypto_utils import (
    decrypt_aes_cbc_pkcs5_padding,
    encrypt_aes_cbc_pkcs5_padding,
    md5_hex_digest,
)
from saic_ismart_client_ng.net.utils import normalize_content_type

if TYPE_CHECKING:
    from collections.abc import MutableMapping
    from datetime import datetime

    Headers = MutableMapping[str, str]

logger = logging.getLogger(__name__)


def get_app_verification_string(
    *,
    request_path: str,
    current_ts: str,
    tenant_id: str,
    content_type: str,
    request_content: str,
    user_token: str,
) -> str:
    # api_name = (
    #    request_path
    #    if (len(request_path) == 0 or "?" not in request_path)
    #    else request_path.split("?")[0]
    # )
    origin_key_part_one = request_path + tenant_id + user_token + "app"
    encrypt_key_part_one = md5_hex_digest(origin_key_part_one, False)
    origin_key_part_two = current_ts + "1" + content_type
    encrypt_key = md5_hex_digest(encrypt_key_part_one + origin_key_part_two, False)
    encrypt_iv = md5_hex_digest(current_ts, False)
    encrypt_req = (
        encrypt_aes_cbc_pkcs5_padding(request_content, encrypt_key, encrypt_iv)
        if len(request_content) > 0
        else ""
    )
    hmac_sha256_value = (
        request_path
        + tenant_id
        + user_token
        + "app"
        + current_ts
        + "1"
        + content_type
        + encrypt_req
    )
    hmac_sha256_key = md5_hex_digest(encrypt_key + current_ts, False)

    if len(hmac_sha256_key) > 0:
        return hmac.new(
            hmac_sha256_key.encode(),
            msg=hmac_sha256_value.encode(),
            digestmod=hashlib.sha256,
        ).hexdigest()

    return ""


def encrypt_request(
    *,
    original_request_url: str,
    original_request_headers: Headers,
    original_request_content: str,
    request_timestamp: datetime,
    base_uri: str,
    region: str,
    tenant_id: str,
    user_token: str = "",
) -> tuple[str | bytes, Headers]:
    original_content_type = original_request_headers.get(
        "Content-Type"
    )  # 'application/x-www-form-urlencoded'
    if not original_content_type:
        modified_content_type = "application/json"
    else:
        modified_content_type = (
            original_content_type  # 'application/x-www-form-urlencoded'
        )
    request_content = ""
    current_ts = str(int(request_timestamp.timestamp() * 1000))
    request_path = str(original_request_url).replace(base_uri, "/")
    request_body = original_request_content
    new_content: str | bytes = original_request_content
    if request_body and (
        not original_content_type or "multipart" not in original_content_type
    ):
        modified_content_type = normalize_content_type(original_content_type)
        request_content = request_body.strip()
        if request_content:
            key_hex = md5_hex_digest(
                md5_hex_digest(request_path + tenant_id + user_token + "app", False)
                + current_ts
                + "1"
                + modified_content_type,
                False,
            )
            iv_hex = md5_hex_digest(current_ts, False)
            if key_hex and iv_hex:
                new_content = encrypt_aes_cbc_pkcs5_padding(
                    request_content, key_hex, iv_hex
                ).encode("utf-8")

    original_request_headers["User-Agent"] = "Europe/2.1.0 (iPad; iOS 18.5; Scale/2.00)"
    original_request_headers["Content-Type"] = f"{modified_content_type};charset=utf-8"
    original_request_headers["Accept"] = "application/json"
    original_request_headers["Accept-Encoding"] = "gzip"

    original_request_headers["REGION"] = region

    original_request_headers["APP-SEND-DATE"] = current_ts
    original_request_headers["APP-CONTENT-ENCRYPTED"] = "1"
    original_request_headers["tenant-id"] = tenant_id
    original_request_headers["User-Type"] = "app"
    original_request_headers["APP-LANGUAGE-TYPE"] = "en"
    if user_token:
        original_request_headers["blade-auth"] = user_token
    app_verification_string = get_app_verification_string(
        request_path=request_path,
        current_ts=current_ts,
        tenant_id=tenant_id,
        content_type=modified_content_type,
        request_content=request_content,
        user_token=user_token,
    )
    original_request_headers["APP-VERIFICATION-STRING"] = app_verification_string
    original_request_headers["ORIGINAL-CONTENT-TYPE"] = modified_content_type
    return new_content, original_request_headers


def decrypt_request(
    *,
    original_request_url: str,
    original_request_headers: Headers,
    original_request_content: str,
    base_uri: str,
) -> bytes:
    charset = "utf-8"
    req_content = original_request_content.strip()
    if req_content:
        app_send_date = original_request_headers.get("APP-SEND-DATE")
        original_content_type = original_request_headers.get("ORIGINAL-CONTENT-TYPE")
        if app_send_date and original_content_type:
            tenant_id = original_request_headers["tenant-id"]
            user_token = original_request_headers.get("blade-auth", "")
            request_path = original_request_url.replace(base_uri, "/")
            key = md5_hex_digest(
                md5_hex_digest(request_path + tenant_id + user_token + "app", False)
                + app_send_date
                + "1"
                + original_content_type,
                False,
            )
            iv = md5_hex_digest(app_send_date, False)
            decrypted = decrypt_aes_cbc_pkcs5_padding(req_content, key, iv)
            if decrypted:
                return decrypted.encode(charset)
    return original_request_content.encode(charset)


def encrypt_response(
    *,
    original_request_url: str,
    original_response_headers: Headers,
    original_response_content: str,
    response_timestamp_ms: int,
    base_uri: str,
    tenant_id: str,
    user_token: str = "",
) -> tuple[str | bytes, Headers]:
    request_content = ""
    request_path = str(original_request_url).replace(base_uri, "/")
    original_content_type = original_response_headers.get(
        "Content-Type", "application/json"
    )  # 'application/x-www-form-urlencoded'
    modified_content_type = original_content_type  # 'application/x-www-form-urlencoded'
    current_ts = str(response_timestamp_ms)
    request_body = original_response_content
    new_content: str | bytes = original_response_content
    if request_body and "multipart" not in original_content_type:
        modified_content_type = normalize_content_type(original_content_type)
        request_content = request_body.strip()
        if request_content:
            key_hex = md5_hex_digest(current_ts + "1" + modified_content_type, False)
            iv_hex = md5_hex_digest(current_ts, False)
            if key_hex and iv_hex:
                new_content = encrypt_aes_cbc_pkcs5_padding(
                    request_content, key_hex, iv_hex
                ).encode("utf-8")

    original_response_headers["Content-Type"] = f"{modified_content_type};charset=utf-8"
    original_response_headers["APP-CONTENT-ENCRYPTED"] = "1"
    original_response_headers["APP-SEND-DATE"] = current_ts
    original_response_headers["ORIGINAL-CONTENT-TYPE"] = modified_content_type
    app_verification_string = get_app_verification_string(
        request_path=request_path,
        current_ts=current_ts,
        tenant_id=tenant_id,
        content_type=modified_content_type,
        request_content=request_content,
        user_token=user_token,
    )
    original_response_headers["APP-VERIFICATION-STRING"] = app_verification_string
    return new_content, original_response_headers


def decrypt_response(
    *,
    original_response_content: str,
    original_response_headers: Headers,
    original_response_charset: str,
) -> tuple[bytes, Headers]:
    resp_content = original_response_content.strip()
    if resp_content:
        app_send_date = original_response_headers.get("APP-SEND-DATE")
        original_content_type = original_response_headers.get("ORIGINAL-CONTENT-TYPE")
        if app_send_date and original_content_type:
            original_response_key = app_send_date + "1" + original_content_type
            key = (
                md5_hex_digest(original_response_key, False)
                if len(original_response_key) > 0
                else ""
            )
            iv = md5_hex_digest(app_send_date, False)
            decrypted = decrypt_aes_cbc_pkcs5_padding(resp_content, key, iv)
            if decrypted:
                resp_content = decrypted
                original_response_headers["Content-Type"] = original_content_type

    return resp_content.encode(original_response_charset), original_response_headers
