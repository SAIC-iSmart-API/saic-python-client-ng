import hashlib
import hmac

from requests import Response

from crypto_utils import md5_hex_digest, encrypt_aes_cbc_pkcs5_padding, decrypt_aes_cbc_pkcs5_padding


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
    originKeyPartOne = request_path + tenant_id + user_token + "app"
    encryptKeyPartOne = md5_hex_digest(originKeyPartOne, False)
    originKeyPartTwo = current_ts + "1" + content_type
    encryptKey = md5_hex_digest(encryptKeyPartOne + originKeyPartTwo, False)
    encryptIV = md5_hex_digest(current_ts, False)
    encryptReq = encrypt_aes_cbc_pkcs5_padding(request_content, encryptKey,
                                               encryptIV) if len(request_content) > 0 else ""
    hmacSha256Value = request_path + tenant_id + user_token + "app" + current_ts + "1" + content_type + encryptReq
    hmacSha256Key = md5_hex_digest(encryptKey + current_ts, False)

    if len(hmacSha256Key) > 0 and len(hmacSha256Value) > 0:
        app_verification_string = hmac.new(
            hmacSha256Key.encode(),
            msg=hmacSha256Value.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        print(
            f"{clazz_simple_name}  headerInterceptor apiName--->>>  {api_name}  \n encryptURI --->>>  {request_path}  \n originKeyPartOne --->>>  {originKeyPartOne}  \n encryptKeyPartOne --->>>  {encryptKeyPartOne}  \n originKeyPartTwo --->>>  {originKeyPartTwo}  \n 完整的加密Key  encryptKey --->>>  {encryptKey}  \n 加密IV  encryptIV --->>>  {encryptIV}  \n 原始params  paramsStr --->>>  {request_content}  \n 加密params  encryptReq --->>>  {encryptReq}  \n hmacSha256Value --->>>  {hmacSha256Value}  \n origin hmacKey --->>>  {encryptKey + current_ts}  \n hmacSha256Key --->>>  {hmacSha256Key}  \n APP-VERIFICATION-STRING --->>>  {app_verification_string}"
        )
        return app_verification_string

    print(
        f"{clazz_simple_name}  headerInterceptor apiName--->>>  {api_name}  \n encryptURI --->>>  {request_path}  \n originKeyPartOne --->>>  {originKeyPartOne}  \n encryptKeyPartOne --->>>  {encryptKeyPartOne}  \n originKeyPartTwo --->>>  {originKeyPartTwo}  \n 完整的加密Key  encryptKey --->>>  {encryptKey}  \n 加密IV  encryptIV --->>>  {encryptIV}  \n 原始params  paramsStr --->>>  {request_content}  \n 加密params  encryptReq --->>>  {encryptReq}  \n hmacSha256Value --->>>  {hmacSha256Value}  \n origin hmacKey --->>>  {encryptKey + current_ts}  \n hmacSha256Key --->>>  {hmacSha256Key}")
    return ""


def decrypt_response(resp: Response):
    app_send_date = resp.headers.get("APP-SEND-DATE")
    original_content_type = resp.headers.get("ORIGINAL-CONTENT-TYPE")
    charset = "UTF-8"  # FIXME: Check it from the content type
    resp_content = resp.content.strip()
    if resp_content:
        original_response_key = app_send_date + "1" + original_content_type
        key = md5_hex_digest(original_response_key, False) if len(original_response_key) > 0 else ""
        iv = md5_hex_digest(app_send_date, False)
        decrypted = decrypt_aes_cbc_pkcs5_padding(resp_content, key, iv)
        if decrypted:
            resp._content = decrypted.encode(charset)
            resp.headers["Content-Length"] = str(len(resp._content))
            resp.headers["Content-Type"] = original_content_type
            return resp
    return resp
