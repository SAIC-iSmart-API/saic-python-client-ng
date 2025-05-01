from __future__ import annotations

import unittest

from saic_ismart_client_ng.model import SaicApiConfiguration


class TestSaicApiConfiguration(unittest.TestCase):
    def setUp(self) -> None:
        self.config = SaicApiConfiguration(
            "test_username",
            "test_password",
            True,
            "GB",
            "https://test-uri.com",
            "123456",
            "test_region",
            5.0,
        )

    def test_username(self) -> None:
        assert self.config.username == "test_username"

    def test_password(self) -> None:
        assert self.config.password == "test_password"  # noqa: S105

    def test_username_is_email(self) -> None:
        assert self.config.username_is_email

    def test_phone_country_code(self) -> None:
        assert self.config.phone_country_code == "GB"

    def test_base_uri(self) -> None:
        assert self.config.base_uri == "https://test-uri.com"

    def test_tenant_id(self) -> None:
        assert self.config.tenant_id == "123456"

    def test_region(self) -> None:
        assert self.config.region == "test_region"

    def test_sms_delivery_delay(self) -> None:
        assert self.config.sms_delivery_delay == 5.0


if __name__ == "__main__":
    unittest.main()
