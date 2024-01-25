import hashlib
import hmac
import logging

from httpx import Response

from saic_ismart_client_ng.crypto_utils import md5_hex_digest, encrypt_aes_cbc_pkcs5_padding, \
    decrypt_aes_cbc_pkcs5_padding

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


async def decrypt_response(resp: Response):
    if resp.is_success:
        charset = "UTF-8"  # FIXME: Check it from the content type
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
