from __future__ import annotations


class SaicApiException(Exception):
    def __init__(self, msg: str, return_code: int | None = None) -> None:
        if return_code is not None:
            self.message = f"return code: {return_code}, message: {msg}"
        else:
            self.message = msg

    def __str__(self) -> str:
        return self.message


class SaicLogoutException(SaicApiException):
    pass


class SaicApiRetryException(SaicApiException):
    def __init__(
        self, msg: str, *, event_id: str, return_code: int | None = None
    ) -> None:
        super().__init__(msg, return_code)
        self.__event_id = event_id

    @property
    def event_id(self) -> str:
        return self.__event_id

    def __str__(self) -> str:
        return f"{self.message}, event_id: {self.event_id}"
