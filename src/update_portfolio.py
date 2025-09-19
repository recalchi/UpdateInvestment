import pandas as pd
from data_coordinator import DataCoordinator
from excel_processor import ExcelProcessor
from yfinance_connector import YFinanceConnector
from nord_connector import NordConnector
from levante_connector import LevanteConnector # Importar LevanteConnector
from investment_analyzer import InvestmentAnalyzer
from portfolio_manager import PortfolioManager

import os
import json
from typing import Dict, Any

class PortfolioUpdater:
    def __init__(self, config_path: str = 'config/config.json'):
        self.config = self._load_config(config_path)

        self.excel_processor = ExcelProcessor(self.config['excel_file_path'])
        self.data_coordinator = DataCoordinator(excel_processor=self.excel_processor) # Pass ExcelProcessor here
        self.investment_analyzer = InvestmentAnalyzer()
        self.portfolio_manager = PortfolioManager()

        # Initialize connectors
        self.yfinance_connector = YFinanceConnector()
        self.nord_connector = NordConnector()
        self.levante_connector = LevanteConnector() # Inicializar LevanteConnector

        # Register data sources with the coordinator
        self.data_coordinator.register_source('yfinance', self.yfinance_connector)
        self.data_coordinator.register_source('nord', self.nord_connector)
        self.data_coordinator.register_source('levante', self.levante_connector) # Registrar LevanteConnector

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

        # 3. Collect data from Nord Research reports
        print("Collecting data from Nord Research reports...")
        nord_report_urls = list(self.config.get('nord_report_urls', {}).values())
        if nord_report_urls:
            nord_data = self.data_coordinator.collect_data('nord', urls=nord_report_urls)
            if nord_data:
                print(f"Collected data from {len(nord_data)} Nord Research reports.")
                # Aqui você precisará adicionar a lógica para processar os DataFrames retornados
                # pelo NordConnector e integrá-los à sua planilha ou análise.
                # Por exemplo, você pode consolidar todos os DataFrames em um único:
                # consolidated_nord_df = pd.concat(nord_data.values(), ignore_index=True)
                # E então usar consolidated_nord_df para atualizar sua planilha ou fazer análises.
                # Por enquanto, apenas imprimimos as chaves para verificar que os dados foram coletados.
                for url, df in nord_data.items():
                    print(f"  - Report {url} with {len(df)} rows.")
            else:
                print("No data collected from Nord Research reports.")
        else:
            print("No Nord Research report URLs configured.")

        # 4. Calculate current portfolio values and summary
        print("Calculating portfolio values and summary...")
        self.portfolio_manager.calculate_current_value()
        portfolio_data_with_values = self.portfolio_manager.get_portfolio_data()
        portfolio_summary = self.investment_analyzer.get_portfolio_summary(portfolio_data_with_values)
        print("Portfolio values and summary calculated.")

        # Atualizar DATA ATT na planilha principal
        positions_df["DATA ATT"] = pd.to_datetime("today").strftime("%Y-%m-%d")
        self.excel_processor.write_sheet(positions_df, self.config["excel_positions_sheet_name"])
        print("DATA ATT atualizada na planilha principal.")

        # Criar aba histórica
        self.excel_processor.create_historical_sheet(portfolio_data_with_values)
        print("Aba histórica criada.")

        print("Portfolio update process completed successfully.")




if __name__ == '__main__':
    updater = PortfolioUpdater()
    updater.run_update()


