import unittest
from unittest.mock import patch, MagicMock
from utils.currencies_api import get_currencies


class TestCurrenciesAPI(unittest.TestCase):

    @patch('utils.currencies_api.requests.get')
    def test_get_currencies_success(self, mock_get):
        xml = """
        <ValCurs Date="02.12.2025" name="Foreign Currency Market">
            <Valute ID="R01235">
                <NumCode>840</NumCode>
                <CharCode>USD</CharCode>
                <Nominal>1</Nominal>
                <Name>Доллар США</Name>
                <Value>90,1234</Value>
            </Valute>
        </ValCurs>
        """.encode('utf-8')
        mock_resp = MagicMock()
        mock_resp.content = xml
        mock_resp.raise_for_status = lambda: None
        mock_get.return_value = mock_resp

        res = get_currencies(url="http://example.com/test")
        self.assertTrue(isinstance(res, list))
        self.assertEqual(res[0]['char_code'], 'USD')

    @patch('utils.currencies_api.requests.get')
    def test_get_currencies_network_error(self, mock_get):
        mock_get.side_effect = Exception("network")
        with self.assertRaises(Exception):
            get_currencies(url="http://example.com/test")


if __name__ == '__main__':
    unittest.main()
