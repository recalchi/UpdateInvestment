import requests
from typing import Dict, Any

class TelegramConnector:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_message(self, message: str, parse_mode: str = "Markdown") -> Dict[str, Any]:
        """Sends a message to the configured Telegram chat.
        :param message: The text message to send.
        :param parse_mode: Parse mode for the message (e.g., "Markdown", "HTML").
        :return: Dictionary with the API response.
        """
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            print("Message sent to Telegram successfully.")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error sending message to Telegram: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Telegram API response: {e.response.text}")
            return {"error": str(e)}

    def get_updates(self) -> Dict[str, Any]:
        """Fetches updates from the Telegram bot (e.g., new messages).
        Useful for debugging or interactive bots.
        """
        url = f"{self.base_url}/getUpdates"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting updates from Telegram: {e}")
            return {"error": str(e)}


if __name__ == '__main__':
    # IMPORTANT: Replace with your actual bot token and chat ID for testing.
    # You can get your chat_id by sending a message to your bot and then
    # accessing https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
    BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

    if BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN" or CHAT_ID == "YOUR_TELEGRAM_CHAT_ID":
        print("Please replace YOUR_TELEGRAM_BOT_TOKEN and YOUR_TELEGRAM_CHAT_ID with actual values to run this example.")
    else:
        connector = TelegramConnector(BOT_TOKEN, CHAT_ID)

        # Test sending a simple message
        print("\nSending a test message...")
        test_message = "*Hello from PortfolioPulse!*\nThis is a test message from your investment automation bot."
        send_response = connector.send_message(test_message)
        print(f"Send message response: {send_response}")

        # Test getting updates (might not show the message just sent, depends on offset)
        print("\nGetting updates...")
        updates_response = connector.get_updates()
        print(f"Get updates response: {updates_response}")

        # Example of sending a message with HTML parse mode
        # html_message = "<b>Hello from PortfolioPulse!</b><br>This is an <i>HTML</i> test message."
        # html_send_response = connector.send_message(html_message, parse_mode="HTML")
        # print(f"HTML message response: {html_send_response}")

