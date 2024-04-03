import unittest
from saic_ismart_client_ng.model import SaicApiConfiguration


class TestSaicApiConfiguration(unittest.TestCase):
    def setUp(self):
        self.config = SaicApiConfiguration(
            "test_username",
            "test_password",
            True,
            "GB",
            "https://test-uri.com",
            "123456",
            "test_region",
            10.0,
            5.0
        )

    def test_username(self):
        self.assertEqual(self.config.username, "test_username")

    def test_password(self):
        self.assertEqual(self.config.password, "test_password")

    def test_username_is_email(self):
        self.assertEqual(self.config.username_is_email, True)

    def test_phone_country_code(self):
        self.assertEqual(self.config.phone_country_code, "GB")

    def test_base_uri(self):
        self.assertEqual(self.config.base_uri, "https://test-uri.com")

    def test_tenant_id(self):
        self.assertEqual(self.config.tenant_id, "123456")

    def test_region(self):
        self.assertEqual(self.config.region, "test_region")

    def test_relogin_delay(self):
        self.assertEqual(self.config.relogin_delay, 10.0)

    def test_sms_delivery_delay(self):
        self.assertEqual(self.config.sms_delivery_delay, 5.0)


if __name__ == '__main__':
    unittest.main()

