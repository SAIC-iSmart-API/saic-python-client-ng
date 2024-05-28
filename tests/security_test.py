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

        self.assertEqual('afd4eaf98af2d964f8ea840fc144ee7bae95dbeeeb251d5e3a01371442f92eeb', result)

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
        self.assertEqual('ff8cb13ebcce5958e7fbfe602716c653fd72ce78842be87b6d50dccede198735', result)

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
        self.assertEqual('332c85836aa9afc864282436a740eb2cc778fafd1fea74dd887c1f8de5056de0', result)

if __name__ == '__main__':
    unittest.main()
