from __future__ import annotations

from enum import IntEnum


class SaicReturnCode(IntEnum):
    """SAIC return codes with a known meaning.

    SAIC replies with a numeric ``code`` and a ``message``. Codes not listed
    here still come through unchanged in ``SaicApiException.return_code``.
    """

    SUCCESS = 0
    # "The remote control instruction failed, please try again later." Seen
    # when the car can't be reached (e.g. asleep), and briefly while it wakes.
    VEHICLE_UNREACHABLE = 4
    SERVICE_UNAVAILABLE = 6
    # The request was refused. SAIC uses this for several different reasons
    # (vehicle not locked, too many remote commands, ...): read the message.
    REQUEST_REJECTED = 8
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    # Not from SAIC: the library's own code for a request that failed in an
    # unexpected way (no usable reply, connection error, ...).
    UNEXPECTED_FAILURE = 500


class SaicApiException(Exception):
    """An error from the SAIC API (or from talking to it).

    ``str(e)`` is unchanged: ``"return code: <code>, message: <message>"``, or
    just the message when there is no code. The two parts are also available
    on their own, so callers don't have to parse that text:

    - ``return_code``: the numeric code, or ``None``
    - ``saic_message``: the message on its own (SAIC's words when the error
      came from a SAIC reply)
    """

    def __init__(self, msg: str, return_code: int | None = None) -> None:
        self.return_code: int | None = return_code
        self.saic_message: str = msg
        if return_code is not None:
            self.message = f"return code: {return_code}, message: {msg}"
        else:
            self.message = msg
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message

    @property
    def is_vehicle_unreachable(self) -> bool:
        """SAIC couldn't reach the car (return code 4)."""
        return self.return_code == SaicReturnCode.VEHICLE_UNREACHABLE

    @property
    def is_request_rejected(self) -> bool:
        """SAIC refused the request (return code 8), for any reason."""
        return self.return_code == SaicReturnCode.REQUEST_REJECTED

    @property
    def is_vehicle_not_locked(self) -> bool:
        """Refused because the vehicle isn't locked (code 8, "not locked")."""
        return self.is_request_rejected and "not locked" in self.saic_message.lower()

    @property
    def is_logged_out(self) -> bool:
        """The session is no longer valid; log in again."""
        return self.return_code in (
            SaicReturnCode.UNAUTHORIZED,
            SaicReturnCode.FORBIDDEN,
        )

    @property
    def is_unexpected_failure(self) -> bool:
        """The library's own code for a request that failed unexpectedly."""
        return self.return_code == SaicReturnCode.UNEXPECTED_FAILURE


class SaicLogoutException(SaicApiException):
    @property
    def is_logged_out(self) -> bool:
        return True


class SaicApiClosedException(SaicApiException):
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
