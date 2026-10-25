from __future__ import annotations

import asyncio
import json
import pickle

import httpx
import pytest

from saic_ismart_client_ng import SaicApi
from saic_ismart_client_ng.exceptions import (
    SaicApiException,
    SaicApiRetryException,
    SaicLogoutException,
    SaicReturnCode,
)
from saic_ismart_client_ng.model import SaicApiConfiguration


def test_text_is_unchanged() -> None:
    e = SaicApiException("Vehicle not locked.", return_code=8)
    assert str(e) == "return code: 8, message: Vehicle not locked."
    assert e.message == "return code: 8, message: Vehicle not locked."
    assert str(SaicApiException("plain")) == "plain"


def test_retry_exception_text_is_unchanged() -> None:
    e = SaicApiRetryException("try again", event_id="123", return_code=4)
    assert str(e) == "return code: 4, message: try again, event_id: 123"
    assert e.event_id == "123"


def test_code_and_message_kept_separately() -> None:
    e = SaicApiException("Vehicle not locked.", return_code=8)
    assert e.return_code == SaicReturnCode.REQUEST_REJECTED
    assert e.saic_message == "Vehicle not locked."
    plain = SaicApiException("plain")
    assert plain.return_code is None
    assert plain.saic_message == "plain"


def test_args_are_set() -> None:
    assert SaicApiException("x", return_code=6).args == ("return code: 6, message: x",)


@pytest.mark.parametrize(
    ("code", "message", "unreachable", "rejected", "not_locked", "logged_out"),
    [
        (4, "The remote control instruction failed", True, False, False, False),
        (8, "Vehicle not locked.", False, True, True, False),
        (
            8,
            "Too many commands, start the vehicle with the key",
            False,
            True,
            False,
            False,
        ),
        (6, "Service not available", False, False, False, False),
        (401, "token expired", False, False, False, True),
        (403, "forbidden", False, False, False, True),
        (None, "no code", False, False, False, False),
    ],
)
def test_checks(
    code: int | None,
    message: str,
    unreachable: bool,
    rejected: bool,
    not_locked: bool,
    logged_out: bool,
) -> None:
    e = SaicApiException(message, return_code=code)
    assert e.is_vehicle_unreachable is unreachable
    assert e.is_request_rejected is rejected
    assert e.is_vehicle_not_locked is not_locked
    assert e.is_logged_out is logged_out


def test_retry_exception_has_the_checks_too() -> None:
    e = SaicApiRetryException("failed", event_id="9", return_code=4)
    assert e.is_vehicle_unreachable
    assert isinstance(e, SaicApiException)


def test_logout_exception_is_always_logged_out() -> None:
    assert SaicLogoutException("bye").is_logged_out
    assert SaicLogoutException('{"code":401}', 401).is_logged_out


def test_unexpected_failure() -> None:
    e = SaicApiException("API call POST /vehicle/control failed unexpectedly", 500)
    assert e.is_unexpected_failure
    assert not SaicApiException("x", 8).is_unexpected_failure


def test_picklable() -> None:
    e = pickle.loads(pickle.dumps(SaicApiException("x", return_code=8)))  # noqa: S301
    assert str(e) == "return code: 8, message: x"


# -- Through the real response handling --------------------------------------


def _deserialize(payload: dict[str, object], *, event_id: str | None = None) -> None:
    api = SaicApi(SaicApiConfiguration(username="offline@example.com", password="x"))  # noqa: S106
    headers = {"event-id": event_id} if event_id else {}
    request = httpx.Request("POST", "https://example.invalid/x", headers=headers)
    response = httpx.Response(
        200, content=json.dumps(payload).encode(), request=request
    )
    deserialize = getattr(api, "_AbstractSaicApi__deserialize")  # noqa: B009
    asyncio.run(deserialize(request, response, None, allow_null_body=True))


def test_rejection_from_a_real_reply_keeps_saics_words() -> None:
    with pytest.raises(SaicApiException) as info:
        _deserialize({"code": 8, "message": "Vehicle not locked."})
    e = info.value
    assert e.return_code == 8
    assert e.saic_message == "Vehicle not locked."
    assert e.is_vehicle_not_locked
    assert str(e) == "return code: 8, message: Vehicle not locked."


def test_unreachable_from_a_real_reply_during_event_polling() -> None:
    with pytest.raises(SaicApiRetryException) as info:
        _deserialize(
            {"code": 4, "message": "The remote control instruction failed"},
            event_id="1118530795",
        )
    assert info.value.is_vehicle_unreachable
    assert info.value.saic_message == "The remote control instruction failed"
