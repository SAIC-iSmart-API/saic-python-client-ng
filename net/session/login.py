from datetime import datetime

import httpx

from crypto_utils import md5_hex_digest, encrypt_aes_cbc_pkcs5_padding
from net.security import get_app_verification_string, httpx_decrypt_response
from net.utils import update_request_with_content


class SaicLoginClient():
    def __init__(self):
        super().__init__()
        self.__user_token = ""
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

    async def __encrypt_request(self, modified_request: httpx.Request):
        original_request_url = modified_request.url
        original_content_type = modified_request.headers.get("Content-Type")
        request_content = ""
        current_ts = str(int(datetime.now().timestamp() * 1000))
        tenant_id = self.__tenant_id
        user_token = self.__user_token
        request_path = str(original_request_url).replace(self.__base_url, "/")
        request_body = modified_request.content.decode("utf-8")
        if request_body:
            request_content = request_body.strip()
            if request_content:
                key_hex = md5_hex_digest(
                    md5_hex_digest(
                        request_path + tenant_id + user_token + "app",
                        False
                    ) + current_ts + "1" + "application/x-www-form-urlencoded",
                    False
                )
                iv_hex = md5_hex_digest(current_ts, False)
                if key_hex and iv_hex:
                    new_content = encrypt_aes_cbc_pkcs5_padding(request_content, key_hex, iv_hex).encode('utf-8')
                    # Update the request content
                    update_request_with_content(modified_request, new_content)

        modified_request.headers["Authorization"] = "Basic c3dvcmQ6c3dvcmRfc2VjcmV0"
        modified_request.headers["User-Type"] = "app"
        modified_request.headers["tenant-id"] = tenant_id
        modified_request.headers["Content-Type"] = "application/x-www-form-urlencoded; charset=utf-8"
        modified_request.headers["APP-SEND-DATE"] = current_ts
        modified_request.headers["APP-CONTENT-ENCRYPTED"] = "1"
        modified_request.headers["APP-LANGUAGE-TYPE"] = "en"
        app_verification_string = get_app_verification_string(
            self.__class_name,
            request_path,
            current_ts,
            tenant_id,
            "application/x-www-form-urlencoded",
            request_content,
            user_token
        )
        modified_request.headers["ORIGINAL-CONTENT-TYPE"] = original_content_type
        modified_request.headers["APP-VERIFICATION-STRING"] = app_verification_string
