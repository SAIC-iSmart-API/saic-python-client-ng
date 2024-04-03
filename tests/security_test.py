import unittest
from saic_ismart_client_ng.net import security


class TestGetAppVerificationString(unittest.TestCase):

    def test_get_app_verification_string_valid(self):
        clazz_simple_name = 'SampleClass'
        request_path = '/api/v1/data'
        current_ts = '20230514123000'
        tenant_id = '1234'
        content_type = 'application/json'
        request_content = '{"key": "value"}'
        user_token = 'dummy_token'

        result = security.get_app_verification_string(clazz_simple_name, request_path, current_ts, tenant_id,
                                                      content_type, request_content, user_token)
        self.assertIsInstance(result, str)

    def test_with_empty_request_path(self):
        clazz_simple_name = 'SampleClass'
        request_path = ''
        current_ts = '20230514123000'
        tenant_id = '1234'
        content_type = 'application/json'
        request_content = '{"key": "value"}'
        user_token = 'dummy_token'

        result = security.get_app_verification_string(clazz_simple_name, request_path, current_ts, tenant_id,
                                                      content_type, request_content, user_token)
        self.assertIsInstance(result, str)

    def test_with_no_request_content(self):
        clazz_simple_name = 'SampleClass'
        request_path = '/api/v1/data'
        current_ts = '20230514123000'
        tenant_id = '1234'
        content_type = 'application/json'
        request_content = ''
        user_token = 'dummy_token'

        result = security.get_app_verification_string(clazz_simple_name, request_path, current_ts, tenant_id,
                                                      content_type, request_content, user_token)
        self.assertIsInstance(result, str)


if __name__ == '__main__':
    unittest.main()
