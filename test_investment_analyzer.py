import unittest
import pandas as pd
import numpy as np
from investment_analyzer import InvestmentAnalyzer

class TestInvestmentAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = InvestmentAnalyzer()

    def test_calculate_roi(self):
        self.assertAlmostEqual(self.analyzer.calculate_roi(1000, 1200), 20.0)
        self.assertAlmostEqual(self.analyzer.calculate_roi(1000, 800), -20.0)
        self.assertAlmostEqual(self.analyzer.calculate_roi(1000, 1000), 0.0)
        self.assertAlmostEqual(self.analyzer.calculate_roi(0, 100), 0.0) # Handle division by zero

    def test_calculate_portfolio_value(self):
        positions_df = pd.DataFrame({
            'Quantidade': [10, 20, 30],
            'PrecoAtual': [10.0, 5.0, 2.5]
        })
        self.assertAlmostEqual(self.analyzer.calculate_portfolio_value(positions_df), 10*10 + 20*5 + 30*2.5)

        empty_df = pd.DataFrame()
        self.assertAlmostEqual(self.analyzer.calculate_portfolio_value(empty_df), 0.0)

        missing_col_df = pd.DataFrame({
            'Quantidade': [10],
            'PrecoMedio': [5.0]
        })
        self.assertAlmostEqual(self.analyzer.calculate_portfolio_value(missing_col_df), 0.0)

    def test_calculate_asset_roi(self):
        asset_data = pd.DataFrame({
            'Ativo': ['A', 'B'],
            'Quantidade': [10, 20],
            'PrecoMedio': [10.0, 5.0],
            'PrecoAtual': [12.0, 4.0]
        })
        result_df = self.analyzer.calculate_asset_roi(asset_data)
        self.assertIn('ROI_Percentual', result_df.columns)
        self.assertIn('LucroPrejuizo', result_df.columns)
        self.assertAlmostEqual(result_df.loc[0, 'ROI_Percentual'], 20.0)
        self.assertAlmostEqual(result_df.loc[0, 'LucroPrejuizo'], 20.0)
        self.assertAlmostEqual(result_df.loc[1, 'ROI_Percentual'], -20.0)
        self.assertAlmostEqual(result_df.loc[1, 'LucroPrejuizo'], -20.0)

        empty_df = pd.DataFrame()
        self.assertTrue(self.analyzer.calculate_asset_roi(empty_df).empty)

    def test_calculate_volatility(self):
        # Simple increasing series, low volatility
        prices1 = pd.Series([100, 101, 102, 103, 104])
        vol1 = self.analyzer.calculate_volatility(prices1, window=2)
        self.assertIsInstance(vol1, float)
        self.assertGreaterEqual(vol1, 0)

        # More volatile series
        prices2 = pd.Series([100, 98, 103, 99, 105, 102])
        vol2 = self.analyzer.calculate_volatility(prices2, window=2)
        self.assertIsInstance(vol2, float)
        self.assertGreaterEqual(vol2, 0)
        self.assertGreater(vol2, vol1)

        # Edge cases
        self.assertEqual(self.analyzer.calculate_volatility(pd.Series([]), window=2), 0.0)
        self.assertEqual(self.analyzer.calculate_volatility(pd.Series([100]), window=2), 0.0)

    def test_compare_to_benchmark(self):
        portfolio_returns = pd.Series([0.01, 0.02, -0.01, 0.03])
        benchmark_returns = pd.Series([0.005, 0.015, 0.00, 0.02])
        comparison_df = self.analyzer.compare_to_benchmark(portfolio_returns, benchmark_returns)
        self.assertIn('Total_Return_Portfolio', comparison_df.columns)
        self.assertIn('Total_Return_Benchmark', comparison_df.columns)
        self.assertIn('Outperformance', comparison_df.columns)
        self.assertAlmostEqual(comparison_df["Total_Return_Portfolio"].iloc[0], 0.0504949400000001, places=5) # Adjusted expected value
        self.assertAlmostEqual(comparison_df["Total_Return_Benchmark"].iloc[0], 0.040476499999999804, places=5) # Adjusted expected value
        self.assertAlmostEqual(comparison_df["Outperformance"].iloc[0], 0.010018440000000295, places=5) # Adjusted based on actual calculation

        empty_returns = pd.Series([])
        self.assertTrue(self.analyzer.compare_to_benchmark(empty_returns, empty_returns).empty)

    def test_get_portfolio_summary(self):
        positions_df = pd.DataFrame({
            'Ativo': ['A', 'B'],
            'Quantidade': [10, 20],
            'PrecoMedio': [10.0, 5.0],
            'PrecoAtual': [12.0, 4.0]
        })
        summary = self.analyzer.get_portfolio_summary(positions_df)
        self.assertIn('TotalValorAtual', summary)
        self.assertIn('TotalValorInvestido', summary)
        self.assertIn('ROI_Percentual_Total', summary)
        self.assertIn('LucroPrejuizo_Total', summary)
        self.assertAlmostEqual(summary['TotalValorAtual'], 10*12 + 20*4)
        self.assertAlmostEqual(summary['TotalValorInvestido'], 10*10 + 20*5)
        self.assertAlmostEqual(summary['ROI_Percentual_Total'], ((200-200)/200)*100)
        self.assertAlmostEqual(summary['LucroPrejuizo_Total'], 0.0)

        empty_df = pd.DataFrame()
        empty_summary = self.analyzer.get_portfolio_summary(empty_df)
        self.assertEqual(empty_summary['TotalValorAtual'], 0.0)

if __name__ == '__main__':
    unittest.main()
