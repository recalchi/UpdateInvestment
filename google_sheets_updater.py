import gspread
import pandas as pd
from typing import List, Dict, Any
from gspread_dataframe import set_with_dataframe # Import gspread_dataframe

class GoogleSheetsUpdater:
    def __init__(self, credentials_path: str = 'credentials.json'):
        """Initializes the GoogleSheetsUpdater with service account credentials.
        :param credentials_path: Path to the Google service account JSON key file.
        """
        try:
            self.gc = gspread.service_account(filename=credentials_path)
            print("Google Sheets API client initialized successfully.")
        except Exception as e:
            print(f"Error initializing Google Sheets API client: {e}")
            self.gc = None

    def open_spreadsheet(self, spreadsheet_name: str):
        """Opens a Google Spreadsheet by its name.
        :param spreadsheet_name: The name of the spreadsheet.
        :return: A gspread.Spreadsheet object or None if an error occurs.
        """
        if not self.gc:
            print("Google Sheets client not initialized. Cannot open spreadsheet.")
            return None
        try:
            spreadsheet = self.gc.open(spreadsheet_name)
            print(f"Spreadsheet \'{spreadsheet_name}\' opened successfully.")
            return spreadsheet
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"Error: Spreadsheet \'{spreadsheet_name}\' not found.")
            return None
        except Exception as e:
            print(f"Error opening spreadsheet \'{spreadsheet_name}\' : {e}")
            return None

    def get_worksheet(self, spreadsheet, worksheet_name: str):
        """Gets a specific worksheet from a spreadsheet.
        :param spreadsheet: A gspread.Spreadsheet object.
        :param worksheet_name: The name of the worksheet.
        :return: A gspread.Worksheet object or None if an error occurs.
        """
        if not spreadsheet:
            return None
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
            print(f"Worksheet \'{worksheet_name}\' retrieved successfully.")
            return worksheet
        except gspread.exceptions.WorksheetNotFound:
            print(f"Error: Worksheet \'{worksheet_name}\' not found in the spreadsheet.")
            return None
        except Exception as e:
            print(f"Error getting worksheet \'{worksheet_name}\' : {e}")
            return None

    def read_data(self, spreadsheet_name: str, worksheet_name: str) -> pd.DataFrame:
        """Reads data from a specified worksheet into a Pandas DataFrame.
        :param spreadsheet_name: The name of the spreadsheet.
        :param worksheet_name: The name of the worksheet.
        :return: A Pandas DataFrame containing the worksheet data.
        """
        spreadsheet = self.open_spreadsheet(spreadsheet_name)
        worksheet = self.get_worksheet(spreadsheet, worksheet_name)
        if worksheet:
            try:
                data = worksheet.get_all_records()
                df = pd.DataFrame(data)
                print(f"Data read from \'{worksheet_name}\' successfully.")
                return df
            except Exception as e:
                print(f"Error reading data from worksheet \'{worksheet_name}\' : {e}")
        return pd.DataFrame()

    def write_data(self, df: pd.DataFrame, spreadsheet_name: str, worksheet_name: str, clear_existing: bool = True):
        """Writes a Pandas DataFrame to a specified worksheet.
           If clear_existing is True, clears the worksheet before writing.
           If the worksheet does not exist, it will be created.
        :param df: The Pandas DataFrame to write.
        :param spreadsheet_name: The name of the spreadsheet.
        :param worksheet_name: The name of the worksheet.
        :param clear_existing: If True, clears existing data in the worksheet before writing.
        """
        spreadsheet = self.open_spreadsheet(spreadsheet_name)
        if not spreadsheet:
            return

        try:
            # Try to get the worksheet, if not found, create it
            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
            except gspread.exceptions.WorksheetNotFound:
                print(f"Worksheet \'{worksheet_name}\' not found, creating a new one.")
                # gspread_dataframe handles worksheet sizing automatically when writing
                worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1, cols=1) # Minimal initial size

            if clear_existing:
                worksheet.clear()
                print(f"Worksheet \'{worksheet_name}\' cleared.")

            # Use set_with_dataframe for efficient writing
            set_with_dataframe(worksheet, df)
            print(f"Data successfully written to worksheet \'{worksheet_name}\' in spreadsheet \'{spreadsheet_name}\' .")
        except Exception as e:
            print(f"Error writing data to Google Sheet: {e}")


if __name__ == '__main__':
    # IMPORTANT: Replace 'path/to/your/credentials.json' with the actual path to your service account key file.
    # Ensure the service account has edit access to the target Google Sheet.
    # For testing, you might need to create a dummy credentials.json and a dummy Google Sheet.
    
    # Example usage (requires a valid credentials.json and a Google Sheet)
    # updater = GoogleSheetsUpdater(credentials_path='path/to/your/credentials.json')
    # spreadsheet_name = 'MyInvestmentPortfolio'
    # worksheet_name = 'PortfolioSummary'

    # Create a dummy DataFrame for testing
    # test_df = pd.DataFrame({
    #     'Asset': ['AAPL', 'GOOGL', 'MSFT'],
    #     'Quantity': [10, 5, 15],
    #     'CurrentPrice': [170.0, 1500.0, 280.0],
    #     'Value': [1700.0, 7500.0, 4200.0]
    # })

    # Write data to Google Sheet
    # updater.write_data(test_df, spreadsheet_name, worksheet_name)

    # Read data from Google Sheet
    # read_df = updater.read_data(spreadsheet_name, worksheet_name)
    # print("\nData read from Google Sheet:")
    # print(read_df)

    print("GoogleSheetsUpdater example requires valid credentials.json and a Google Sheet.")
    print("Please uncomment and configure the example usage block to run tests.")

