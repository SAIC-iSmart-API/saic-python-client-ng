from datetime import datetime

from requests import Session, PreparedRequest

from crypto_utils import md5_hex_digest, encrypt_aes_cbc_pkcs5_padding
from net.security import get_app_verification_string, decrypt_response


class SaicLoginSecuritySession(Session):
    def __init__(self):
        super().__init__()
        self.__user_token = ""
        self.__base_url = "https://gateway-mg-eu.soimt.com/api.app/v1/"
        self.__tenant_id = "459771"
        self.__class_name = ""

    def get_user_token(self):
        return self.__user_token

    def get_class_name(self):
        return self.__class_name

    def get_base_url(self):
        return self.__base_url

    def get_tenand_id(self):
        return self.__tenant_id

    def set_user_token(self, user_token):
        self.__user_token = user_token

    def send(self, modified_request: PreparedRequest, **kwargs):
        self.__encrypt_request(modified_request)
        resp = super().send(modified_request, **kwargs)
        if resp.ok and resp.content:
            decrypted_resp = decrypt_response(resp)
            return decrypted_resp
        else:
            return resp

    def __encrypt_request(self, modified_request):
        original_request_url = modified_request.url
        original_content_type = modified_request.headers.get("Content-Type")
        request_content = ""
        current_ts = str(int(datetime.now().timestamp() * 1000))
        tenant_id = self.get_tenand_id()
        user_token = self.get_user_token()
        request_path = original_request_url.replace(self.get_base_url(), "/")
        request_body = modified_request.body
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
                    modified_request.body = encrypt_aes_cbc_pkcs5_padding(request_content, key_hex, iv_hex)
        modified_request.headers["Authorization"] = "Basic c3dvcmQ6c3dvcmRfc2VjcmV0"
        modified_request.headers["User-Type"] = "app"
        modified_request.headers["tenant-id"] = tenant_id
        modified_request.headers["Content-Type"] = "application/x-www-form-urlencoded; charset=utf-8"
        modified_request.headers["APP-SEND-DATE"] = current_ts
        modified_request.headers["APP-CONTENT-ENCRYPTED"] = "1"
        modified_request.headers["APP-LANGUAGE-TYPE"] = "en"
        app_verification_string = get_app_verification_string(
            self.get_class_name(),
            request_path,
            current_ts,
            tenant_id,
            "application/x-www-form-urlencoded",
            request_content,
            user_token
        )
        modified_request.headers["ORIGINAL-CONTENT-TYPE"] = original_content_type
        modified_request.headers["APP-VERIFICATION-STRING"] = app_verification_string
        # Recompute the content length because we have modified the request body
        modified_request.prepare_content_length(modified_request.body)
