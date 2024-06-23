import hashlib
import hmac
import logging
from datetime import datetime
from typing import Optional

from httpx import Response, Request

from saic_ismart_client_ng.crypto_utils import md5_hex_digest, encrypt_aes_cbc_pkcs5_padding, \
    decrypt_aes_cbc_pkcs5_padding
from saic_ismart_client_ng.net.utils import update_request_with_content, normalize_content_type

logger = logging.getLogger(__name__)


def get_app_verification_string(
        clazz_simple_name,
        request_path,
        current_ts,
        tenant_id,
        content_type,
        request_content,
        user_token
):
    api_name = request_path if (len(request_path) > 0 or "?" not in request_path) else request_path.split("?")[0]
    origin_key_part_one = request_path + tenant_id + user_token + "app"
    encrypt_key_part_one = md5_hex_digest(origin_key_part_one, False)
    origin_key_part_two = current_ts + "1" + content_type
    encrypt_key = md5_hex_digest(encrypt_key_part_one + origin_key_part_two, False)
    encrypt_iv = md5_hex_digest(current_ts, False)
    encrypt_req = encrypt_aes_cbc_pkcs5_padding(request_content, encrypt_key,
                                                encrypt_iv) if len(request_content) > 0 else ""
    hmac_sha256_value = request_path + tenant_id + user_token + "app" + current_ts + "1" + content_type + encrypt_req
    hmac_sha256_key = md5_hex_digest(encrypt_key + current_ts, False)

    if len(hmac_sha256_key) > 0 and len(hmac_sha256_value) > 0:
        app_verification_string = hmac.new(
            hmac_sha256_key.encode(),
            msg=hmac_sha256_value.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        logger.debug(
            f"{clazz_simple_name}  headerInterceptor apiName--->>>  {api_name}  \n encryptURI --->>>  {request_path}  \n origin_key_part_one --->>>  {origin_key_part_one}  \n encrypt_key_part_one --->>>  {encrypt_key_part_one}  \n origin_key_part_two --->>>  {origin_key_part_two}  \n 完整的加密Key  encrypt_key --->>>  {encrypt_key}  \n 加密IV  encrypt_iv --->>>  {encrypt_iv}  \n 原始params  paramsStr --->>>  {request_content}  \n 加密params  encrypt_req --->>>  {encrypt_req}  \n hmac_sha256_value --->>>  {hmac_sha256_value}  \n origin hmacKey --->>>  {encrypt_key + current_ts}  \n hmacSha256Key --->>>  {hmac_sha256_key}  \n APP-VERIFICATION-STRING --->>>  {app_verification_string}"
        )
        return app_verification_string

    logger.debug(
        f"{clazz_simple_name}  headerInterceptor apiName--->>>  {api_name}  \n encryptURI --->>>  {request_path}  \n origin_key_part_one --->>>  {origin_key_part_one}  \n encrypt_key_part_one --->>>  {encrypt_key_part_one}  \n origin_key_part_two --->>>  {origin_key_part_two}  \n 完整的加密Key  encrypt_key --->>>  {encrypt_key}  \n 加密IV  encrypt_iv --->>>  {encrypt_iv}  \n 原始params  paramsStr --->>>  {request_content}  \n 加密params  encrypt_req --->>>  {encrypt_req}  \n hmac_sha256_value --->>>  {hmac_sha256_value}  \n origin hmacKey --->>>  {encrypt_key + current_ts}  \n hmacSha256Key --->>>  {hmac_sha256_key}")
    return ""


async def encrypt_request(
        *,
        modified_request: Request,
        request_timestamp: datetime,
        base_uri: str,
        region: str,
        tenant_id: str,
        user_token: str = "",
        class_name: str = "",
):
    original_request_url = modified_request.url
    original_content_type = modified_request.headers.get("Content-Type")  # 'application/x-www-form-urlencoded'
    if not original_content_type:
        modified_content_type = "application/json"
    else:
        modified_content_type = original_content_type  # 'application/x-www-form-urlencoded'
    request_content = ""
    current_ts = str(int(request_timestamp.timestamp() * 1000))
    request_path = str(original_request_url).replace(base_uri, "/")
    request_body = modified_request.content.decode("utf-8")
    if request_body and "multipart" not in original_content_type:
        modified_content_type = normalize_content_type(original_content_type)
        request_content = request_body.strip()
        if request_content:
            key_hex = md5_hex_digest(
                md5_hex_digest(
                    request_path + tenant_id + user_token + "app",
                    False
                ) + current_ts + "1" + modified_content_type,
                False
            )
            iv_hex = md5_hex_digest(current_ts, False)
            if key_hex and iv_hex:
                new_content = encrypt_aes_cbc_pkcs5_padding(request_content, key_hex, iv_hex).encode('utf-8')
                # Update the request content
                update_request_with_content(modified_request, new_content)

    modified_request.headers["User-Agent"] = "okhttp/3.14.9"
    modified_request.headers["Content-Type"] = f"{modified_content_type};charset=utf-8"
    modified_request.headers["Accept"] = "application/json"
    modified_request.headers["Accept-Encoding"] = "gzip"

    modified_request.headers["REGION"] = region

    modified_request.headers["APP-SEND-DATE"] = current_ts
    modified_request.headers["APP-CONTENT-ENCRYPTED"] = "1"
    modified_request.headers["tenant-id"] = tenant_id
    modified_request.headers["User-Type"] = "app"
    modified_request.headers["APP-LANGUAGE-TYPE"] = "en"
    if user_token:
        modified_request.headers["blade-auth"] = user_token
    app_verification_string = get_app_verification_string(
        class_name,
        request_path,
        current_ts,
        tenant_id,
        modified_content_type,
        request_content,
        user_token
    )
    modified_request.headers["ORIGINAL-CONTENT-TYPE"] = modified_content_type
    modified_request.headers["APP-VERIFICATION-STRING"] = app_verification_string


async def decrypt_request(req: Request, base_uri: str):
    charset = 'utf-8'
    req_content = (await req.aread()).decode(charset).strip()
    if req_content:
        app_send_date = req.headers.get("APP-SEND-DATE")
        original_content_type = req.headers.get("ORIGINAL-CONTENT-TYPE")
        if app_send_date and original_content_type:
            tenant_id = req.headers['tenant-id']
            user_token = req.headers.get('blade-auth', '')
            request_path = str(req.url).replace(base_uri, "/")
            key = md5_hex_digest(
                md5_hex_digest(
                    request_path + tenant_id + user_token + "app",
                    False
                ) + app_send_date + "1" + original_content_type,
                False
            )
            iv = md5_hex_digest(app_send_date, False)
            decrypted = decrypt_aes_cbc_pkcs5_padding(req_content, key, iv)
            if decrypted:
                return decrypted.encode(charset)
    return req_content


async def decrypt_response(resp: Response):
    if resp.is_success:
        charset = resp.encoding
        resp_content = (await resp.aread()).decode(charset).strip()
        if resp_content:
            app_send_date = resp.headers.get("APP-SEND-DATE")
            original_content_type = resp.headers.get("ORIGINAL-CONTENT-TYPE")
            if app_send_date and original_content_type:
                original_response_key = app_send_date + "1" + original_content_type
                key = md5_hex_digest(original_response_key, False) if len(original_response_key) > 0 else ""
                iv = md5_hex_digest(app_send_date, False)
                decrypted = decrypt_aes_cbc_pkcs5_padding(resp_content, key, iv)
                if decrypted:
                    resp._content = decrypted.encode(charset)
                    resp.headers["Content-Length"] = str(len(resp._content))
                    resp.headers["Content-Type"] = original_content_type
    return resp
