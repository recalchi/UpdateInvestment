import unittest
import pandas as pd
from data_coordinator import DataCoordinator

class MockConnector:
    def __init__(self, name):
        self.name = name

    def fetch_data(self, **kwargs):
        if self.name == "yfinance":
            return pd.DataFrame({
                "Date": pd.to_datetime(["2023-01-01", "2023-01-02"]),
                "Ticker": [kwargs.get("ticker"), kwargs.get("ticker")],
                "Close": [100.0, 101.0]
            })
        elif self.name == "nord":
            return pd.DataFrame({
                "ReportDate": pd.to_datetime(["2023-01-01"]),
                "Company": [kwargs.get("query")],
                "Recommendation": ["Buy"]
            })
        return pd.DataFrame()

class TestDataCoordinator(unittest.TestCase):
    def setUp(self):
        self.coordinator = DataCoordinator()
        self.mock_yfinance = MockConnector("yfinance")
        self.mock_nord = MockConnector("nord")
        self.coordinator.register_source("yfinance", self.mock_yfinance)
        self.coordinator.register_source("nord", self.mock_nord)

    def test_register_source(self):
        self.assertIn("yfinance", self.coordinator.data_sources)
        self.assertIn("nord", self.coordinator.data_sources)
        self.assertEqual(self.coordinator.data_sources["yfinance"], self.mock_yfinance)

    def test_collect_data(self):
        yfinance_data = self.coordinator.collect_data("yfinance", ticker="PETR4.SA")
        self.assertFalse(yfinance_data.empty)
        self.assertIn("Ticker", yfinance_data.columns)
        self.assertEqual(yfinance_data["Ticker"].iloc[0], "PETR4.SA")

        nord_data = self.coordinator.collect_data("nord", query="VALE3")
        self.assertFalse(nord_data.empty)
        self.assertIn("Company", nord_data.columns)
        self.assertEqual(nord_data["Company"].iloc[0], "VALE3")

    def test_collect_data_unregistered_source(self):
        with self.assertRaises(ValueError):
            self.coordinator.collect_data("unregistered_source")

    def test_consolidate_data_empty_list(self):
        consolidated = self.coordinator.consolidate_data([])
        self.assertTrue(consolidated.empty)

    def test_consolidate_data_single_df(self):
        df = pd.DataFrame({"A": [1, 2], "B": ["x", "y"]})
        consolidated = self.coordinator.consolidate_data([df])
        pd.testing.assert_frame_equal(consolidated, df)

    def test_consolidate_data_multiple_dfs_same_columns(self):
        df1 = pd.DataFrame({"A": [1, 2], "B": ["x", "y"]})
        df2 = pd.DataFrame({"A": [3, 4], "B": ["z", "w"]})
        expected = pd.DataFrame({"A": [1, 2, 3, 4], "B": ["x", "y", "z", "w"]})
        consolidated = self.coordinator.consolidate_data([df1, df2])
        pd.testing.assert_frame_equal(consolidated, expected)

    def test_consolidate_data_multiple_dfs_different_columns(self):
        df1 = pd.DataFrame({"A": [1, 2], "B": ["x", "y"]})
        df2 = pd.DataFrame({"C": [3, 4], "D": ["z", "w"]})
        consolidated = self.coordinator.consolidate_data([df1, df2])
        self.assertIn("A", consolidated.columns)
        self.assertIn("B", consolidated.columns)
        self.assertIn("C", consolidated.columns)
        self.assertIn("D", consolidated.columns)
        self.assertEqual(len(consolidated), 4)
        self.assertTrue(pd.isna(consolidated.loc[0, "C"]))
        self.assertTrue(pd.isna(consolidated.loc[2, "A"]))

    def test_standardize_data(self):
        df = pd.DataFrame({
            "Date": ["2023-01-01", "invalid_date"],
            "Price": [100, "abc"],
            "Other": [1, 2]
        })
        standardized_df = self.coordinator.standardize_data(df)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(standardized_df["Date"]))
        self.assertTrue(pd.api.types.is_numeric_dtype(standardized_df["Price"]))
        self.assertTrue(pd.isna(standardized_df.loc[1, "Date"]))
        self.assertTrue(pd.isna(standardized_df.loc[1, "Price"]))

    # Mocking ExcelProcessor for get_portfolio_positions and get_transactions
    # These tests would ideally be integration tests or require a mock Excel file
    # For unit testing DataCoordinator, we assume these methods would correctly call ExcelProcessor
    # and focus on DataCoordinator's logic.

if __name__ == "__main__":
    unittest.main()
