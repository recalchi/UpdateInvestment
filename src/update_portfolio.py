import pandas as pd
from data_coordinator import DataCoordinator
from excel_processor import ExcelProcessor
from yfinance_connector import YFinanceConnector
from nord_connector import NordConnector
from levante_connector import LevanteConnector
from investment_analyzer import InvestmentAnalyzer
from portfolio_manager import PortfolioManager
from google_sheets_updater import GoogleSheetsUpdater
from telegram_connector import TelegramConnector
import os
import json

class PortfolioUpdater:
    def __init__(self, config_path: str = 'config.json'):
        self.config = self._load_config(config_path)

        self.excel_processor = ExcelProcessor(self.config['excel_file_path'])
        self.data_coordinator = DataCoordinator(excel_processor=self.excel_processor) # Pass ExcelProcessor here
        self.investment_analyzer = InvestmentAnalyzer()
        self.portfolio_manager = PortfolioManager()

        # Initialize connectors
        self.yfinance_connector = YFinanceConnector()
        self.nord_connector = NordConnector()
        self.levante_connector = LevanteConnector()
        self.google_sheets_updater = GoogleSheetsUpdater(self.config['google_sheets_credentials_path'])
        self.telegram_connector = TelegramConnector(self.config['telegram_bot_token'], self.config['telegram_chat_id'])

        # Register data sources with the coordinator
        self.data_coordinator.register_source('yfinance', self.yfinance_connector)
        self.data_coordinator.register_source('nord', self.nord_connector)
        self.data_coordinator.register_source('levante', self.levante_connector)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found at {config_path}")
        with open(config_path, 'r') as f:
            return json.load(f)

    def run_update(self):
        print("Starting portfolio update process...")

        # 1. Load portfolio positions from Excel
        print("Loading portfolio positions from Excel...")
        positions_df = self.data_coordinator.get_portfolio_positions(self.config['excel_positions_sheet_name'])
        if positions_df.empty:
            print("No positions found in Excel. Aborting update.")
            return
        self.portfolio_manager.load_positions(positions_df)
        print(f"Loaded {len(positions_df)} positions.")

        # 2. Collect latest prices from Yahoo Finance
        print("Collecting latest prices from Yahoo Finance...")
        tickers = positions_df['Ativo'].tolist()
        latest_prices = self.data_coordinator.collect_data('yfinance', tickers=tickers)
        
        if latest_prices.empty:
            print("Warning: Could not fetch any latest prices from Yahoo Finance. Using existing prices if available.")
        else:
            self.portfolio_manager.update_prices(latest_prices)
            print("Latest prices updated.")

        # 3. Calculate current portfolio values and summary
        print("Calculating portfolio values and summary...")
        self.portfolio_manager.calculate_current_value()
        portfolio_data_with_values = self.portfolio_manager.get_portfolio_data()
        portfolio_summary = self.investment_analyzer.get_portfolio_summary(portfolio_data_with_values)
        print("Portfolio values and summary calculated.")

        # 4. Update Google Sheets
        print("Updating Google Sheets...")
        spreadsheet_name = self.config['google_sheets_spreadsheet_name']
        summary_sheet = self.config['google_sheets_summary_sheet_name']
        details_sheet = self.config['google_sheets_details_sheet_name']

        # Prepare summary for Google Sheets
        summary_df = pd.DataFrame([portfolio_summary])
        self.google_sheets_updater.write_data(summary_df, spreadsheet_name, summary_sheet, clear_existing=True)
        self.google_sheets_updater.write_data(portfolio_data_with_values, spreadsheet_name, details_sheet, clear_existing=True)
        print("Google Sheets updated.")

        # 5. Send Telegram Notification
        print("Sending Telegram notification...")
        message = (
            f"*Atualização da Carteira de Investimentos*\n\n"
            f"*Valor Total Atual:* R$ {portfolio_summary.get('TotalValorAtual', 0.0):.2f}\n"
            f"*Total Investido:* R$ {portfolio_summary.get('TotalValorInvestido', 0.0):.2f}\n"
            f"*Lucro/Prejuízo:* R$ {portfolio_summary.get('LucroPrejuizo_Total', 0.0):.2f}\n"
            f"*ROI Percentual:* {portfolio_summary.get('ROI_Percentual_Total', 0.0):.2f}%\n\n"
            f"_Verifique a planilha para detalhes: {self.config['google_sheets_spreadsheet_url']}_"
        )
        self.telegram_connector.send_message(message)
        print("Telegram notification sent.")

        print("Portfolio update process completed successfully.")


if __name__ == '__main__':
    # Example config.json structure:
    # {
    #   "excel_file_path": "portfolio.xlsx",
    #   "excel_positions_sheet_name": "Posicoes",
    #   "google_sheets_credentials_path": "path/to/your/credentials.json",
    #   "google_sheets_spreadsheet_name": "MyInvestmentPortfolio",
    #   "google_sheets_summary_sheet_name": "Resumo",
    #   "google_sheets_details_sheet_name": "Detalhes",
    #   "google_sheets_spreadsheet_url": "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit",
    #   "telegram_bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
    #   "telegram_chat_id": "YOUR_TELEGRAM_CHAT_ID"
    # }

    # Create a dummy config.json for demonstration if it doesn't exist
    if not os.path.exists('config.json'):
        dummy_config = {
            "excel_file_path": "portfolio.xlsx",
            "excel_positions_sheet_name": "Posicoes",
            "google_sheets_credentials_path": "./credentials.json", # Placeholder
            "google_sheets_spreadsheet_name": "MyInvestmentPortfolio", # Placeholder
            "google_sheets_summary_sheet_name": "Resumo",
            "google_sheets_details_sheet_name": "Detalhes",
            "google_sheets_spreadsheet_url": "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit", # Placeholder
            "telegram_bot_token": "YOUR_TELEGRAM_BOT_TOKEN", # Placeholder
            "telegram_chat_id": "YOUR_TELEGRAM_CHAT_ID" # Placeholder
        }
        with open('config.json', 'w') as f:
            json.dump(dummy_config, f, indent=4)
        print("Created a dummy config.json. Please update it with your actual details.")

    try:
        updater = PortfolioUpdater()
        updater.run_update()
    except FileNotFoundError as e:
        print(f"Configuration error: {e}. Please ensure config.json and credentials.json are correctly set up.")
    except Exception as e:
        print(f"An unexpected error occurred during the update process: {e}")

