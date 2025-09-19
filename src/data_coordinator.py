import pandas as pd
from typing import List, Dict, Any
from excel_processor import ExcelProcessor # Import ExcelProcessor

class DataCoordinator:
    def __init__(self, excel_processor: ExcelProcessor = None):
        self.data_sources = {}
        self.excel_processor = excel_processor # Inject ExcelProcessor

    def register_source(self, name: str, connector):
        self.data_sources[name] = connector

    def collect_data(self, source_name: str, **kwargs) -> pd.DataFrame:
        if source_name not in self.data_sources:
            raise ValueError(f"Data source \'{source_name}\' not registered.")
        return self.data_sources[source_name].fetch_data(**kwargs)

    def consolidate_data(self, dataframes: List[pd.DataFrame]) -> pd.DataFrame:
        if not dataframes:
            return pd.DataFrame()
        
        all_columns = sorted(list(set.union(*[set(df.columns) for df in dataframes])))
        aligned_dataframes = []
        for df in dataframes:
            for col in all_columns:
                if col not in df.columns:
                    df[col] = None
            aligned_dataframes.append(df[all_columns])
            
        return pd.concat(aligned_dataframes, ignore_index=True)

    def standardize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        if 'Price' in df.columns:
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        return df

    def get_portfolio_positions(self, sheet_name: str = 'Posicoes') -> pd.DataFrame:
        if not self.excel_processor:
            print("ExcelProcessor not provided to DataCoordinator. Cannot read portfolio positions.")
            return pd.DataFrame()
        try:
            df = self.excel_processor.read_sheet(sheet_name)
            return self.standardize_data(df)
        except Exception as e:
            print(f"Error reading portfolio positions from Excel: {e}")
            return pd.DataFrame()

    def get_transactions(self, sheet_name: str = 'Transacoes') -> pd.DataFrame:
        if not self.excel_processor:
            print("ExcelProcessor not provided to DataCoordinator. Cannot read transactions.")
            return pd.DataFrame()
        try:
            df = self.excel_processor.read_sheet(sheet_name)
            return self.standardize_data(df)
        except Exception as e:
            print(f"Error reading transactions from Excel: {e}")
            return pd.DataFrame()


if __name__ == '__main__':
    # Example Usage (requires mock connectors or actual implementations)
    class MockYFinanceConnector:
        def fetch_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
            print(f"Fetching data for {ticker} from {start_date} to {end_date} (Mock)")
            return pd.DataFrame({
                'Date': pd.to_datetime(['2023-01-01', '2023-01-02']),
                'Ticker': [ticker, ticker],
                'Close': [100.0, 101.5]
            })

    # Mock ExcelProcessor for example usage
    class MockExcelProcessor:
        def __init__(self, file_path):
            self.file_path = file_path
        def read_sheet(self, sheet_name):
            if sheet_name == 'Posicoes':
                return pd.DataFrame({
                    'Ativo': ['MOCK1'], 'Quantidade': [10], 'PrecoMedio': [50.0]
                })
            return pd.DataFrame()

    mock_excel_processor = MockExcelProcessor('mock_portfolio.xlsx')
    dc = DataCoordinator(excel_processor=mock_excel_processor)
    dc.register_source('yfinance', MockYFinanceConnector())

    # Collect data from different sources
    yfinance_data = dc.collect_data('yfinance', ticker='PETR4.SA', start_date='2023-01-01', end_date='2023-01-02')

    print("\nYFinance Data:")
    print(yfinance_data)


    # Consolidate data (example, usually different types of data are not simply concatenated)
    consolidated_df = dc.consolidate_data([yfinance_data])
    print("\nConsolidated Data (simple concat example):")
    print(consolidated_df)

    # Standardize data
    standardized_df = dc.standardize_data(yfinance_data.copy())
    print("\nStandardized YFinance Data:")
    print(standardized_df)

    # Example of getting portfolio positions using the injected ExcelProcessor
    df_positions = dc.get_portfolio_positions('Posicoes')
    print("\nPortfolio Positions (via injected ExcelProcessor):")
    print(df_positions)

    df_transactions = dc.get_transactions('Transacoes')
    print("\nTransactions (via injected ExcelProcessor):")
    print(df_transactions)

