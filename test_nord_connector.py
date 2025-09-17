import unittest
import pandas as pd
import requests
from unittest.mock import patch, MagicMock
from nord_connector import NordConnector

class TestNordConnector(unittest.TestCase):
    def setUp(self):
        self.connector = NordConnector(base_url="http://mock-nord.com")

    @patch("requests.Session.get")
    def test_fetch_latest_reports_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = """
            <html><body>
                <a class="report-link" href="/report1">Report Title 1</a>
                <a class="report-link" href="/report2">Report Title 2</a>
                <a class="report-link" href="/report3">Report Title 3</a>
            </body></html>
        """
        mock_get.return_value = mock_response

        df = self.connector.fetch_latest_reports(num_reports=2)
        self.assertFalse(df.empty)
        self.assertEqual(len(df), 2)
        self.assertIn("Source", df.columns)
        self.assertIn("Title", df.columns)
        self.assertIn("Link", df.columns)
        self.assertEqual(df.loc[0, "Title"], "Report Title 1")
        self.assertEqual(df.loc[0, "Link"], "http://mock-nord.com/report1")

    @patch("requests.Session.get")
    def test_fetch_latest_reports_no_reports_found(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = "<html><body><p>No reports here</p></body></html>"
        mock_get.return_value = mock_response

        df = self.connector.fetch_latest_reports()
        self.assertTrue(df.empty)

    @patch("requests.Session.get")
    def test_fetch_latest_reports_with_search_term(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = """
            <html><body>
                <a class="report-link" href="/report1">Report PETR4 Analysis</a>
                <a class="report-link" href="/report2">Market Overview</a>
                <a class="report-link" href="/report3">PETR4 Update</a>
            </body></html>
        """
        mock_get.return_value = mock_response

        df = self.connector.fetch_latest_reports(search_term="PETR4")
        self.assertFalse(df.empty)
        self.assertEqual(len(df), 2)
        self.assertTrue(all("PETR4" in title for title in df["Title"].tolist()))

    @patch("requests.Session.get")
    def test_fetch_latest_reports_request_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Test error")
        df = self.connector.fetch_latest_reports()
        self.assertTrue(df.empty)

    def test_fetch_data_alias(self):
        with patch.object(self.connector, "fetch_latest_reports") as mock_fetch:
            mock_fetch.return_value = pd.DataFrame({"Title": ["Test"]})
            df = self.connector.fetch_data(query="TestQuery", num_results=1)
            mock_fetch.assert_called_once_with(search_term="TestQuery", num_reports=1)
            self.assertFalse(df.empty)

if __name__ == "__main__":
    unittest.main()
