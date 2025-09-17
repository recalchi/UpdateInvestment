import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any

class InvestmentAnalyzer:
    def __init__(self):
        pass

    def calculate_roi(self, initial_value: float, current_value: float) -> float:
        """Calculates the Return on Investment (ROI)."""
        if initial_value == 0:
            return 0.0
        return ((current_value - initial_value) / initial_value) * 100

    def calculate_portfolio_value(self, positions_df: pd.DataFrame) -> float:
        """Calculates the total current value of the portfolio.
        Assumes positions_df has 'Quantidade' and 'PrecoAtual' columns.
        """
        if positions_df.empty or not all(col in positions_df.columns for col in ['Quantidade', 'PrecoAtual']):
            return 0.0
        return (positions_df['Quantidade'] * positions_df['PrecoAtual']).sum()

    def calculate_asset_roi(self, asset_data: pd.DataFrame) -> pd.DataFrame:
        """Calculates ROI for each asset.
        Assumes asset_data has 'PrecoMedio', 'PrecoAtual', 'Quantidade' columns.
        """
        if asset_data.empty or not all(col in asset_data.columns for col in ['PrecoMedio', 'PrecoAtual', 'Quantidade']):
            return pd.DataFrame()
        
        df = asset_data.copy()
        df['ValorInvestido'] = df['PrecoMedio'] * df['Quantidade']
        df['ValorAtual'] = df['PrecoAtual'] * df['Quantidade']
        df['ROI_Percentual'] = df.apply(lambda row: self.calculate_roi(row['ValorInvestido'], row['ValorAtual']), axis=1)
        df['LucroPrejuizo'] = df['ValorAtual'] - df['ValorInvestido']
        return df

    def calculate_volatility(self, prices: pd.Series, window: int = 20) -> float:
        """Calculates the annualized volatility of a series of prices.
        :param prices: A pandas Series of daily closing prices.
        :param window: The rolling window for calculating standard deviation (e.g., 20 for 20 trading days).
        :return: Annualized volatility.
        """
        if len(prices) < 2:
            return 0.0
        returns = prices.pct_change().dropna()
        if returns.empty:
            return 0.0
        daily_volatility = returns.rolling(window=window).std().iloc[-1]
        annualized_volatility = daily_volatility * np.sqrt(252) # 252 trading days in a year
        return annualized_volatility

    def compare_to_benchmark(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> pd.DataFrame:
        """Compares portfolio returns to a benchmark.
        :param portfolio_returns: Daily returns of the portfolio.
        :param benchmark_returns: Daily returns of the benchmark.
        :return: DataFrame with comparative metrics.
        """
        comparison_df = pd.DataFrame({
            'Portfolio': portfolio_returns,
            'Benchmark': benchmark_returns
        }).dropna()

        if comparison_df.empty:
            return pd.DataFrame()

        portfolio_cumulative = (1 + comparison_df['Portfolio']).cumprod() - 1
        benchmark_cumulative = (1 + comparison_df['Benchmark']).cumprod() - 1

        return pd.DataFrame({
            'Total_Return_Portfolio': [portfolio_cumulative.iloc[-1] if not portfolio_cumulative.empty else 0],
            'Total_Return_Benchmark': [benchmark_cumulative.iloc[-1] if not benchmark_cumulative.empty else 0],
            'Outperformance': [portfolio_cumulative.iloc[-1] - benchmark_cumulative.iloc[-1] if not portfolio_cumulative.empty and not benchmark_cumulative.empty else 0]
        })

    def get_portfolio_summary(self, positions_df: pd.DataFrame) -> Dict[str, Any]:
        """Generates a summary of the portfolio including total value and overall ROI.
        Assumes positions_df has 'PrecoMedio', 'PrecoAtual', 'Quantidade' columns.
        """
        if positions_df.empty:
            return {
                'TotalValorAtual': 0.0,
                'TotalValorInvestido': 0.0,
                'ROI_Percentual_Total': 0.0,
                'LucroPrejuizo_Total': 0.0
            }

        analyzed_positions = self.calculate_asset_roi(positions_df)
        
        total_valor_investido = analyzed_positions['ValorInvestido'].sum()
        total_valor_atual = analyzed_positions['ValorAtual'].sum()
        total_lucro_prejuizo = analyzed_positions['LucroPrejuizo'].sum()
        total_roi_percentual = self.calculate_roi(total_valor_investido, total_valor_atual)

        return {
            'TotalValorAtual': total_valor_atual,
            'TotalValorInvestido': total_valor_investido,
            'ROI_Percentual_Total': total_roi_percentual,
            'LucroPrejuizo_Total': total_lucro_prejuizo
        }


if __name__ == '__main__':
    analyzer = InvestmentAnalyzer()

    # Example 1: Calculate ROI
    roi = analyzer.calculate_roi(1000, 1200)
    print(f"ROI: {roi:.2f}%") # Expected: 20.00%

    # Example 2: Calculate Portfolio Value
    positions_data = pd.DataFrame({
        'Ativo': ['PETR4', 'VALE3'],
        'Quantidade': [100, 50],
        'PrecoMedio': [30.0, 60.0],
        'PrecoAtual': [32.0, 65.0]
    })
    portfolio_value = analyzer.calculate_portfolio_value(positions_data)
    print(f"Portfolio Value: R${portfolio_value:.2f}") # Expected: R$6450.00

    # Example 3: Calculate Asset ROI
    asset_roi_df = analyzer.calculate_asset_roi(positions_data)
    print("\nAsset ROI:")
    print(asset_roi_df)
    # Expected:
    #    Ativo  Quantidade  PrecoMedio  PrecoAtual  ValorInvestido  ValorAtual  ROI_Percentual  LucroPrejuizo
    # 0  PETR4         100        30.0        32.0          3000.0      3200.0        6.666667          200.0
    # 1  VALE3          50        60.0        65.0          3000.0      3250.0        8.333333          250.0

    # Example 4: Get Portfolio Summary
    portfolio_summary = analyzer.get_portfolio_summary(positions_data)
    print("\nPortfolio Summary:")
    print(portfolio_summary)
    # Expected:
    # {
    #   'TotalValorAtual': 6450.0,
    #   'TotalValorInvestido': 6000.0,
    #   'ROI_Percentual_Total': 7.5,
    #   'LucroPrejuizo_Total': 450.0
    # }

    # Example 5: Calculate Volatility
    # Create a dummy price series for volatility calculation
    np.random.seed(42)
    prices = pd.Series(np.random.normal(loc=100, scale=1, size=100)).cumsum() + 100
    volatility = analyzer.calculate_volatility(prices)
    print(f"\nAnnualized Volatility: {volatility:.2f}")

    # Example 6: Compare to Benchmark
    # Create dummy returns
    portfolio_returns = pd.Series(np.random.normal(0.001, 0.01, 100))
    benchmark_returns = pd.Series(np.random.normal(0.0005, 0.008, 100))
    comparison = analyzer.compare_to_benchmark(portfolio_returns, benchmark_returns)
    print("\nPortfolio vs Benchmark Comparison:")
    print(comparison)

