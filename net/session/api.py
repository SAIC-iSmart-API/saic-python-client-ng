from datetime import datetime

import httpx
from httpx._client import USER_AGENT
from requests import Session, PreparedRequest

from crypto_utils import md5_hex_digest, encrypt_aes_cbc_pkcs5_padding
from net.security import get_app_verification_string, decrypt_response, httpx_decrypt_response
from net.utils import update_request_with_content


class SaicApiClient(Session):
    def __init__(self, user_token):
        super().__init__()
        self.__user_token = user_token
        self.__base_url = "https://gateway-mg-eu.soimt.com/api.app/v1/"
        self.__tenant_id = "459771"
        self.__class_name = ""
        self.__client = httpx.AsyncClient(
            event_hooks={
                "request": [self.__encrypt_request],
                "response": [httpx_decrypt_response]
            }
        )

    def client(self):
        return self.__client

    def get_user_token(self):
        return self.__user_token

    def set_user_token(self, user_token):
        self.__user_token = user_token

    async def __encrypt_request(self, modified_request: httpx.Request):
        original_request_url = modified_request.url
        original_content_type = modified_request.headers.get("Content-Type")
        if not original_content_type:
            modified_content_type = "application/json"
        else:
            modified_content_type = original_content_type
        request_content = ""
        current_ts = str(int(datetime.now().timestamp() * 1000))
        tenant_id = self.__tenant_id
        user_token = self.get_user_token()
        request_path = str(original_request_url).replace(self.__base_url, "/")
        request_body = modified_request.content.decode("utf-8")
        if request_body:
            modified_content_type = "multipart/form-data" if "multipart" in original_content_type else "application/json"
            request_content = request_body.strip()
            if request_content and not "multipart" in original_content_type:
                key_hex = md5_hex_digest(
                    md5_hex_digest(
                        request_path + tenant_id + user_token + "app",
                        False
                    ) + current_ts + "1" + modified_content_type,
                    False
                )
                iv_hex = md5_hex_digest(current_ts, False)
                if key_hex and iv_hex:
                    new_content = encrypt_aes_cbc_pkcs5_padding(request_content, key_hex, iv_hex).encode("utf-8")
                    update_request_with_content(modified_request, new_content)

        modified_request.headers["User-Agent"] = "okhttp/3.14.9"
        modified_request.headers["Content-Type"] = "application/json;charset=UTF-8"
        modified_request.headers["Accept"] = "application/json"
        modified_request.headers["Accept-Encoding"] = "gzip"

        modified_request.headers["REGION"] = "eu"
        modified_request.headers["APP-SEND-DATE"] = current_ts
        modified_request.headers["APP-CONTENT-ENCRYPTED"] = "1"
        modified_request.headers["tenant-id"] = tenant_id
        modified_request.headers["User-Type"] = "app"
        modified_request.headers["APP-LANGUAGE-TYPE"] = "en"
        if user_token:
            modified_request.headers["blade-auth"] = user_token
        app_verification_string = get_app_verification_string(
            self.__class_name,
            request_path,
            current_ts,
            tenant_id,
            modified_content_type,
            request_content,
            user_token
        )
        modified_request.headers["ORIGINAL-CONTENT-TYPE"] = modified_content_type
        modified_request.headers["APP-VERIFICATION-STRING"] = app_verification_string
