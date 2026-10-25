from __future__ import annotations

import datetime

from saic_ismart_client_ng.api.message.schema import MessageEntity

UTC = datetime.UTC


def test_create_time_utc_from_milliseconds() -> None:
    created = datetime.datetime(2026, 9, 25, 17, 57, 38, tzinfo=UTC)
    msg = MessageEntity(createTime=int(created.timestamp() * 1000))
    assert msg.create_time_utc == created
    assert msg.create_time_utc is not None
    assert msg.create_time_utc.tzinfo is not None


def test_create_time_utc_missing_is_none() -> None:
    assert MessageEntity().create_time_utc is None


def test_create_time_utc_unreadable_is_none() -> None:
    assert MessageEntity(createTime="soon").create_time_utc is None  # type: ignore[arg-type]
    assert MessageEntity(createTime=10**20).create_time_utc is None


def test_message_time_or_none_parses_every_known_format() -> None:
    expected = datetime.datetime(2026, 9, 25, 18, 57, 38)
    for text in ("2026-09-25 18:57:38", "25-09-2026 18:57:38", "25/09/2026 18:57:38"):
        assert MessageEntity(messageTime=text).message_time_or_none == expected


def test_message_time_or_none_is_naive() -> None:
    parsed = MessageEntity(messageTime="2026-09-25 18:57:38").message_time_or_none
    assert parsed is not None
    assert parsed.tzinfo is None


def test_message_time_or_none_missing_or_unreadable_is_none() -> None:
    assert MessageEntity().message_time_or_none is None
    assert MessageEntity(messageTime="").message_time_or_none is None
    assert MessageEntity(messageTime="yesterday").message_time_or_none is None


def test_message_time_still_falls_back_to_now() -> None:
    # Unchanged behaviour for existing callers.
    before = datetime.datetime.now()
    fallback = MessageEntity().message_time
    assert before <= fallback <= datetime.datetime.now()
    parsed = MessageEntity(messageTime="2026-09-25 18:57:38").message_time
    assert parsed == datetime.datetime(2026, 9, 25, 18, 57, 38)
