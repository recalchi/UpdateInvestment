from update_portfolio import PortfolioUpdater
import argparse
import os
import json

def main():
    parser = argparse.ArgumentParser(description="Run the PortfolioPulse investment portfolio update automation.")
    parser.add_argument(
        "--config", 
        type=str, 
        default="config/config.json", 
        help="Path to the configuration JSON file."
    )
    args = parser.parse_args()

    # Resolve the absolute path for the config file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path_abs = os.path.join(script_dir, "..", args.config)
    config_path_abs = os.path.normpath(config_path_abs)

    # Ensure the config directory exists
    config_dir = os.path.dirname(config_path_abs)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    # Check if config.json exists, if not, create a dummy one
    if not os.path.exists(config_path_abs):
        print(f"Configuration file not found at {config_path_abs}. Creating a dummy one.")
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
        with open(config_path_abs, 'w') as f:
            json.dump(dummy_config, f, indent=4)
        print(f"A dummy config.json has been created at {config_path_abs}. Please update it with your actual details.")
        return # Exit after creating dummy config, user needs to fill it

    try:
        updater = PortfolioUpdater(config_path=config_path_abs)
        updater.run_update()
    except FileNotFoundError as e:
        print(f"Configuration error: {e}. Please ensure config.json and credentials.json are correctly set up.")
    except Exception as e:
        print(f"An unexpected error occurred during the update process: {e}")

if __name__ == "__main__":
    main()

