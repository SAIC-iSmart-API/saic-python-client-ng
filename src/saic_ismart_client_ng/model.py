class SaicApiConfiguration:
    def __init__(
            self,
            username: str,
            password: str,
            username_is_email: bool = True,
            phone_country_code: str = None,
            base_uri: str = "https://gateway-mg-eu.soimt.com/api.app/v1/",
            tenant_id: str = "459771",
            region: str = "eu",
            sms_delivery_delay: float = 3.0,
    ):
        self.__username = username
        self.__password = password
        self.__username_is_email = username_is_email
        self.__phone_country_code = phone_country_code
        self.__base_uri = base_uri
        self.__tenant_id = tenant_id
        self.__region = region
        self.__sms_delivery_delay = sms_delivery_delay

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password

    @property
    def username_is_email(self):
        return self.__username_is_email

    @property
    def phone_country_code(self):
        return self.__phone_country_code

    @property
    def base_uri(self):
        return self.__base_uri

    @property
    def tenant_id(self):
        return self.__tenant_id

    @property
    def region(self):
        return self.__region

    @property
    def sms_delivery_delay(self):
        return self.__sms_delivery_delay
