import unittest
from unittest.mock import patch

from saic_ismart_client_ng.listener import SaicApiListener


class TestSaicApiListener(unittest.TestCase):
    def setUp(self):
        self.listener = SaicApiListener()

    @patch('listener.SaicApiListener.on_request')
    async def test_on_request(self, mock_on_request):
        path = "/test/path"
        body = "test body"
        headers = {"Content-Type": "application/json"}

        await self.listener.on_request(path, body, headers)
        mock_on_request.assert_called_once_with(path, body, headers)

    @patch('listener.SaicApiListener.on_response')
    async def test_on_response(self, mock_on_response):
        path = "/test/path"
        body = "test body"
        headers = {"Content-Type": "application/json"}

        await self.listener.on_response(path, body, headers)
        mock_on_response.assert_called_once_with(path, body, headers)


if __name__ == '__main__':
    unittest.main()
