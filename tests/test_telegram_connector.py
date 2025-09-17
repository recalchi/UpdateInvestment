import unittest
from unittest.mock import patch, MagicMock
from telegram_connector import TelegramConnector
import requests

class TestTelegramConnector(unittest.TestCase):
    def setUp(self):
        self.bot_token = "mock_token"
        self.chat_id = "mock_chat_id"
        self.connector = TelegramConnector(self.bot_token, self.chat_id)

    @patch("requests.post")
    def test_send_message_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"ok": True, "result": {"message_id": 123}}
        mock_post.return_value = mock_response

        message = "Test message"
        response = self.connector.send_message(message)

        mock_post.assert_called_once_with(
            f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
            json={
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
        )
        self.assertTrue(response["ok"])

    @patch("requests.post")
    def test_send_message_failure(self, mock_post):
        mock_post.side_effect = requests.exceptions.RequestException("Network error")
        message = "Test message"
        response = self.connector.send_message(message)

        self.assertIn("error", response)
        self.assertIn("Network error", response["error"])

    @patch("requests.get")
    def test_get_updates_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"ok": True, "result": []}
        mock_get.return_value = mock_response

        response = self.connector.get_updates()

        mock_get.assert_called_once_with(
            f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        )
        self.assertTrue(response["ok"])

    @patch("requests.get")
    def test_get_updates_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("API error")
        response = self.connector.get_updates()

        self.assertIn("error", response)
        self.assertIn("API error", response["error"])

if __name__ == "__main__":
    unittest.main()
