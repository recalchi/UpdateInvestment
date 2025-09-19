import pandas as pd
from typing import Dict, Any

class PortfolioManager:
    def __init__(self):
        self.portfolio_data = pd.DataFrame()

    def load_positions(self, positions_df: pd.DataFrame):
        """Loads current portfolio positions.
        Assumes positions_df has columns like 'Ativo', 'Quantidade', 'PrecoMedio'.
        """
        self.portfolio_data = positions_df.copy()
        print("Portfolio positions loaded.")

    def update_prices(self, prices_df: pd.DataFrame):
        """Updates current prices for assets in the portfolio.
        Assumes prices_df has columns like 'Ativo', 'PrecoAtual'.
        """
        if self.portfolio_data.empty:
            print("No portfolio positions loaded to update prices.")
            return

        # Ensure 'PrecoAtual' column exists in self.portfolio_data, initialize with None if not present
        if 'PrecoAtual' not in self.portfolio_data.columns:
            self.portfolio_data['PrecoAtual'] = None

        if not prices_df.empty:
            # Merge current prices into portfolio data
            # Use 'left' merge to keep all portfolio assets, even if no new price is found
            # The 'PrecoAtual' from prices_df will be 'PrecoAtual_new' after merge
            merged_df = pd.merge(
                self.portfolio_data,
                prices_df[["Ativo", "PrecoAtual"]],
                on="Ativo",
                how="left",
                suffixes=("", "_new")
            )
            
            # Update 'PrecoAtual' column: use 'PrecoAtual_new' if available, otherwise keep existing 'PrecoAtual'
            self.portfolio_data['PrecoAtual'] = merged_df['PrecoAtual_new'].fillna(self.portfolio_data['PrecoAtual'])
            
            # Drop the temporary '_new' column if it exists
            if 'PrecoAtual_new' in merged_df.columns:
                merged_df.drop(columns=['PrecoAtual_new'], inplace=True)
            
            # Update the portfolio_data with the merged result
            self.portfolio_data = merged_df
            print("Portfolio prices updated.")
        else:
            print("Nenhum novo preço para atualizar. Mantendo os preços existentes.")

    def calculate_current_value(self):
        """Calculates the current market value for each position and total portfolio value.
        Requires 'Quantidade' and 'PrecoAtual' columns.
        """
        if self.portfolio_data.empty or not all(col in self.portfolio_data.columns for col in ["Quantidade", "PrecoAtual"]):
            print("Cannot calculate current value: missing 'Quantidade' or 'PrecoAtual' in portfolio data.")
            return
        
        self.portfolio_data["ValorAtual"] = self.portfolio_data["Quantidade"] * self.portfolio_data["PrecoAtual"]
        self.portfolio_data["ValorInvestido"] = self.portfolio_data["Quantidade"] * self.portfolio_data["PrecoMedio"]
        print("Current values calculated.")

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Returns a summary of the portfolio.
        Requires 'ValorAtual', 'PrecoMedio', 'Quantidade' columns.
        """
        if self.portfolio_data.empty or not all(col in self.portfolio_data.columns for col in ["ValorAtual", "PrecoMedio", "Quantidade"]):
            print("Cannot generate summary: missing required columns in portfolio data.")
            return {}

        total_invested = (self.portfolio_data["PrecoMedio"] * self.portfolio_data["Quantidade"]).sum()
        total_current_value = self.portfolio_data["ValorAtual"].sum()
        
        profit_loss = total_current_value - total_invested
        roi = (profit_loss / total_invested) * 100 if total_invested != 0 else 0.0

        return {
            "TotalInvestido": total_invested,
            "ValorTotalAtual": total_current_value,
            "LucroPrejuizo": profit_loss,
            "ROI_Percentual": roi,
            "DetalhesPorAtivo": self.portfolio_data.to_dict(orient="records")
        }

    def get_portfolio_data(self) -> pd.DataFrame:
        """Returns the full portfolio DataFrame."""
        return self.portfolio_data.copy()


if __name__ == '__main__':
    manager = PortfolioManager()

    # 1. Load initial positions
    initial_positions = pd.DataFrame({
        'Ativo': ['PETR4', 'VALE3', 'ITUB4'],
        'Quantidade': [100, 50, 200],
        'PrecoMedio': [28.00, 62.00, 25.00],
        'PrecoAtual': [28.00, 62.00, 25.00] # Initial current price same as average price
    })
    manager.load_positions(initial_positions)
    print("\nInitial Portfolio Data:")
    print(manager.get_portfolio_data())

    # 2. Simulate new prices
    new_prices = pd.DataFrame({
        'Ativo': ['PETR4', 'VALE3', 'ITUB4', 'BBDC4'],
        'PrecoAtual': [29.50, 63.50, 26.10, 22.00] # BBDC4 is a new asset not in portfolio
    })
    manager.update_prices(new_prices)
    print("\nPortfolio Data after price update:")
    print(manager.get_portfolio_data())

    # 3. Calculate current value
    manager.calculate_current_value()
    print("\nPortfolio Data after current value calculation:")
    print(manager.get_portfolio_data())

    # 4. Get portfolio summary
    summary = manager.get_portfolio_summary()
    print("\nPortfolio Summary:")
    print(summary)

    # Example with empty portfolio
    empty_manager = PortfolioManager()
    empty_manager.update_prices(new_prices)
    empty_manager.calculate_current_value()
    print("\nEmpty Portfolio Summary:")
    print(empty_manager.get_portfolio_summary())

