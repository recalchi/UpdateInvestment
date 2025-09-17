import yfinance as yf
import pandas as pd
from typing import List, Dict, Any

class YFinanceConnector:
    def __init__(self):
        pass

    def fetch_current_prices(self, tickers: List[str]) -> pd.DataFrame:
        """Fetches the current closing prices for a list of tickers from Yahoo Finance.
        :param tickers: A list of stock tickers (e.g., ["PETR4.SA", "VALE3.SA"]).
        :return: A Pandas DataFrame with 'Ativo' and 'PrecoAtual' columns.
        """
        if not tickers:
            return pd.DataFrame()

        # Use yf.download with a short period to get recent data
        # auto_adjust=True gets adjusted close prices
        data = yf.download(tickers, period="1d", interval="1m", progress=False, auto_adjust=True)
        
        if data.empty:
            print(f"No data fetched for tickers: {tickers}")
            return pd.DataFrame()

        prices = []
        if len(tickers) == 1:
            # If only one ticker, data is a DataFrame with 'Close' column
            if 'Close' in data.columns:
                prices.append({
                    'Ativo': tickers[0],
                    'PrecoAtual': data['Close'].iloc[-1] # Get the last available close price
                })
            else:
                print(f"Warning: No 'Close' price found for {tickers[0]}")
        else:
            # For multiple tickers, data is a MultiIndex DataFrame
            for ticker in tickers:
                # Check if the ticker exists in the MultiIndex columns
                if ('Close', ticker) in data.columns:
                    # Get the last valid close price for each ticker
                    last_close = data['Close'][ticker].dropna().iloc[-1] if not data['Close'][ticker].dropna().empty else None
                    if last_close is not None:
                        prices.append({
                            'Ativo': ticker,
                            'PrecoAtual': last_close
                        })
                else:
                    print(f"Warning: No 'Close' price found for {ticker} or ticker data is incomplete.")

        return pd.DataFrame(prices)

    def fetch_historical_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetches historical data for a single ticker.
        :param ticker: The stock ticker.
        :param start_date: Start date in 'YYYY-MM-DD' format.
        :param end_date: End date in 'YYYY-MM-DD' format.
        :return: A Pandas DataFrame with historical data.
        """
        try:
            data = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
            if data.empty:
                print(f"No historical data found for {ticker} from {start_date} to {end_date}")
                return pd.DataFrame()
            data.reset_index(inplace=True)
            data["Ativo"] = ticker
            return data
        except Exception as e:
            print(f"Error fetching historical data for {ticker}: {e}")
            return pd.DataFrame()

    def fetch_data(self, tickers: List[str] = None, ticker: str = None, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Generic fetch data method to be used by DataCoordinator.
           Can fetch current prices (if tickers provided) or historical data (if single ticker and dates provided).
        """
        if tickers:
            return self.fetch_current_prices(tickers)
        elif ticker and start_date and end_date:
            return self.fetch_historical_data(ticker, start_date, end_date)
        else:
            print("Invalid parameters for YFinanceConnector. Please provide tickers or (ticker, start_date, end_date).")
            return pd.DataFrame()


if __name__ == '__main__':
    connector = YFinanceConnector()

    # Test fetching current prices for multiple tickers
    tickers_list = ["PETR4.SA", "VALE3.SA", "MGLU3.SA"]
    current_prices_df = connector.fetch_current_prices(tickers_list)
    print("\nCurrent Prices:")
    print(current_prices_df)

    # Test fetching current price for a single ticker
    single_ticker_price_df = connector.fetch_current_prices(["ITUB4.SA"])
    print("\nSingle Ticker Current Price:")
    print(single_ticker_price_df)

    # Test fetching historical data
    historical_df = connector.fetch_historical_data("PETR4.SA", "2023-01-01", "2023-01-05")
    print("\nHistorical Data for PETR4.SA:")
    print(historical_df)

    # Test with invalid ticker
    invalid_prices_df = connector.fetch_current_prices(["INVALIDTICKER"])
    print("\nInvalid Ticker Prices:")
    print(invalid_prices_df)

    # Test with empty tickers list
    empty_prices_df = connector.fetch_current_prices([])
    print("\nEmpty Tickers List Prices:")
    print(empty_prices_df)

