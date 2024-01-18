from tenacity import RetryError


class SaicApiException(Exception):
    def __init__(self, msg: str, return_code: int = None):
        if return_code is not None:
            self.message = f'return code: {return_code}, message: {msg}'
        else:
            self.message = msg

    def __str__(self):
        return self.message


class SaicApiRetryException(RetryError, SaicApiException):
    def __init__(self, event_id: str):
        self.__event_id = event_id

    @property
    def event_id(self) -> str:
        return self.__event_id
