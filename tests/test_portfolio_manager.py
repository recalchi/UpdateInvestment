import unittest
import pandas as pd
from portfolio_manager import PortfolioManager

class TestPortfolioManager(unittest.TestCase):
    def setUp(self):
        self.manager = PortfolioManager()
        self.initial_positions = pd.DataFrame({
            'Ativo': ['PETR4', 'VALE3', 'ITUB4'],
            'Quantidade': [100, 50, 200],
            'PrecoMedio': [28.00, 62.00, 25.00],
            'PrecoAtual': [28.00, 62.00, 25.00] # Initial current price same as average price
        })

    def test_load_positions(self):
        self.manager.load_positions(self.initial_positions)
        pd.testing.assert_frame_equal(self.manager.get_portfolio_data(), self.initial_positions)

    def test_update_prices(self):
        self.manager.load_positions(self.initial_positions)
        new_prices = pd.DataFrame({
            'Ativo': ['PETR4', 'VALE3', 'BBDC4'],
            'PrecoAtual': [29.50, 63.50, 22.00] # BBDC4 is a new asset not in portfolio
        })
        self.manager.update_prices(new_prices)
        updated_df = self.manager.get_portfolio_data()
        
        # Check updated prices
        self.assertAlmostEqual(updated_df[updated_df['Ativo'] == 'PETR4']['PrecoAtual'].iloc[0], 29.50)
        self.assertAlmostEqual(updated_df[updated_df['Ativo'] == 'VALE3']['PrecoAtual'].iloc[0], 63.50)
        # ITUB4 should retain its old price as no new price was provided
        self.assertAlmostEqual(updated_df[updated_df['Ativo'] == 'ITUB4']['PrecoAtual'].iloc[0], 25.00)
        # BBDC4 should not be added as it's not in initial positions
        self.assertFalse('BBDC4' in updated_df['Ativo'].values)

    def test_calculate_current_value(self):
        self.manager.load_positions(self.initial_positions)
        # Manually set some current prices for calculation
        self.manager.portfolio_data.loc[self.manager.portfolio_data['Ativo'] == 'PETR4', 'PrecoAtual'] = 30.00
        self.manager.portfolio_data.loc[self.manager.portfolio_data['Ativo'] == 'VALE3', 'PrecoAtual'] = 60.00
        self.manager.calculate_current_value()
        updated_df = self.manager.get_portfolio_data()

        self.assertIn('ValorAtual', updated_df.columns)
        self.assertAlmostEqual(updated_df[updated_df['Ativo'] == 'PETR4']['ValorAtual'].iloc[0], 100 * 30.00)
        self.assertAlmostEqual(updated_df[updated_df['Ativo'] == 'VALE3']['ValorAtual'].iloc[0], 50 * 60.00)
        self.assertAlmostEqual(updated_df[updated_df['Ativo'] == 'ITUB4']['ValorAtual'].iloc[0], 200 * 25.00)

    def test_get_portfolio_summary(self):
        self.manager.load_positions(self.initial_positions)
        self.manager.portfolio_data.loc[self.manager.portfolio_data['Ativo'] == 'PETR4', 'PrecoAtual'] = 30.00
        self.manager.portfolio_data.loc[self.manager.portfolio_data['Ativo'] == 'VALE3', 'PrecoAtual'] = 65.00
        self.manager.calculate_current_value()
        summary = self.manager.get_portfolio_summary()

        total_invested = (100 * 28.00) + (50 * 62.00) + (200 * 25.00)
        total_current_value = (100 * 30.00) + (50 * 65.00) + (200 * 25.00)
        profit_loss = total_current_value - total_invested
        roi = (profit_loss / total_invested) * 100

        self.assertAlmostEqual(summary['TotalInvestido'], total_invested)
        self.assertAlmostEqual(summary['ValorTotalAtual'], total_current_value)
        self.assertAlmostEqual(summary['LucroPrejuizo'], profit_loss)
        self.assertAlmostEqual(summary['ROI_Percentual'], roi)
        self.assertEqual(len(summary['DetalhesPorAtivo']), 3)

    def test_empty_portfolio_summary(self):
        empty_manager = PortfolioManager()
        summary = empty_manager.get_portfolio_summary()
        self.assertEqual(summary, {})

    def test_get_portfolio_data(self):
        self.manager.load_positions(self.initial_positions)
        retrieved_df = self.manager.get_portfolio_data()
        pd.testing.assert_frame_equal(retrieved_df, self.initial_positions)
        # Ensure it's a copy and not the same object
        self.assertIsNot(retrieved_df, self.manager.portfolio_data)

if __name__ == '__main__':
    unittest.main()
