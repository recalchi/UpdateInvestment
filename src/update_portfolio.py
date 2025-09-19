import pandas as pd
from data_coordinator import DataCoordinator
from excel_processor import ExcelProcessor
from yfinance_connector import YFinanceConnector
from browser_orchestrator import BrowserOrchestrator
from investment_analyzer import InvestmentAnalyzer
from portfolio_manager import PortfolioManager

import os
import json
from typing import Dict, Any

class PortfolioUpdater:
    def __init__(self, config_path: str = 'config/config.json'):
        self.config = self._load_config(config_path)

        self.excel_processor = ExcelProcessor(self.config['excel_file_path'])
        self.data_coordinator = DataCoordinator(excel_processor=self.excel_processor)
        self.investment_analyzer = InvestmentAnalyzer()
        self.portfolio_manager = PortfolioManager()

        # Initialize connectors
        self.yfinance_connector = YFinanceConnector()
        self.browser_orchestrator = BrowserOrchestrator(headless=True) # Mudar para False para depuração visual


        # Register data sources with the coordinator
        self.data_coordinator.register_source('yfinance', self.yfinance_connector)

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

        # 3. Collect data from Nord Research reports using BrowserOrchestrator
        print("Collecting data from Nord Research reports...")
        nord_credentials = self.config.get("nord_credentials")
        if nord_credentials:
            if self.browser_orchestrator.setup_driver():
                if self.browser_orchestrator.login_nord(nord_credentials["email"], nord_credentials["password"]):
                    nord_report_urls = list(self.config.get("nord_report_urls", {}).values())
                    if nord_report_urls:
                        nord_data = {}
                        for url in nord_report_urls:
                            df = self.browser_orchestrator.extract_nord_data(url)
                            if not df.empty:
                                nord_data[url] = df

                        if nord_data:
                            print(f"Collected data from {len(nord_data)} Nord Research reports.")
                            for url, df in nord_data.items():
                                print(f"  - Report {url} with {len(df)} rows.")
                        else:
                            print("No data collected from Nord Research reports.")
                    else:
                        print("No Nord Research report URLs configured.")
                else:
                    print("Não foi possível fazer login na Nord Research. Pulando coleta de dados.")
                self.browser_orchestrator.close_driver()
            else:
                print("Não foi possível inicializar o driver do navegador para Nord Research. Pulando coleta de dados.")
        else:
            print("Credenciais da Nord Research não configuradas. Pulando coleta de dados.")

        # 4. Collect data from Levante Ideias reports using BrowserOrchestrator
        print("Collecting data from Levante Ideias reports...")
        levante_credentials = self.config.get("levante_credentials")
        if levante_credentials:
            if self.browser_orchestrator.setup_driver(): # Re-setup driver for Levante if it was closed after Nord
                if self.browser_orchestrator.login_levante(levante_credentials["email"], levante_credentials["password"]):
                    levante_report_urls = list(self.config.get("levante_report_urls", {}).values())
                    if levante_report_urls:
                        levante_data = {}
                        for url in levante_report_urls:
                            df = self.browser_orchestrator.extract_levante_data(url)
                            if not df.empty:
                                levante_data[url] = df

                        if levante_data:
                            print(f"Collected data from {len(levante_data)} Levante Ideias reports.")
                            for url, df in levante_data.items():
                                print(f"  - Report {url} with {len(df)} rows.")
                        else:
                            print("No data collected from Levante Ideias reports.")
                    else:
                        print("No Levante Ideias report URLs configured.")
                else:
                    print("Não foi possível fazer login na Levante Ideias. Pulando coleta de dados.")
                self.browser_orchestrator.close_driver()
            else:
                print("Não foi possível inicializar o driver do navegador para Levante Ideias. Pulando coleta de dados.")
        else:
            print("Credenciais da Levante Ideias não configuradas. Pulando coleta de dados.")

        # 5. Calculate current portfolio values and summary
        print("Calculating portfolio values and summary...")
        self.portfolio_manager.calculate_current_value()
        portfolio_data_with_values = self.portfolio_manager.get_portfolio_data()
        portfolio_summary = self.investment_analyzer.get_portfolio_summary(portfolio_data_with_values)
        print("Portfolio values and summary calculated.")

        # Atualizar DATA ATT na planilha principal
        positions_df["DATA ATT"] = pd.to_datetime("today").strftime("%Y-%m-%d")
        self.excel_processor.write_sheet(positions_df, self.config['excel_positions_sheet_name'])
        print("DATA ATT atualizada na planilha principal.")

        # Criar aba histórica
        self.excel_processor.create_historical_sheet(portfolio_data_with_values)
        print("Aba histórica criada.")

        print("Portfolio update process completed successfully.")




if __name__ == '__main__':
    updater = PortfolioUpdater()
    updater.run_update()


