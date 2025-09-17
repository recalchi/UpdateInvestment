import unittest
import pandas as pd
import os
from unittest.mock import patch
from excel_processor import ExcelProcessor

class TestExcelProcessor(unittest.TestCase):
    def setUp(self):
        self.test_file = 'test_excel_processor.xlsx'
        self.processor = ExcelProcessor(self.test_file)
        self.sample_df = pd.DataFrame({
            'ColA': [1, 2, 3],
            'ColB': ['X', 'Y', 'Z']
        })
        self.sample_df2 = pd.DataFrame({
            'ColC': [10, 20],
            'ColD': ['A', 'B']
        })

        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_write_sheet_new_file(self):
        self.processor.write_sheet(self.sample_df, 'NewSheet')
        self.assertTrue(os.path.exists(self.test_file))
        read_df = self.processor.read_sheet('NewSheet')
        pd.testing.assert_frame_equal(self.sample_df, read_df)

    def test_write_sheet_overwrite_existing(self):
        self.processor.write_sheet(self.sample_df, 'ExistingSheet')
        self.processor.write_sheet(self.sample_df2, 'ExistingSheet')
        read_df = self.processor.read_sheet('ExistingSheet')
        pd.testing.assert_frame_equal(self.sample_df2, read_df)

    def test_read_sheet_non_existent_file(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        df = self.processor.read_sheet('AnySheet')
        self.assertTrue(df.empty)

    def test_read_sheet_non_existent_sheet(self):
        self.processor.write_sheet(self.sample_df, 'ExistingSheet')
        df = self.processor.read_sheet('NonExistentSheet')
        self.assertTrue(df.empty)

    def test_update_sheet_range_existing_sheet(self):
        # Write initial data with headers ColA, ColB
        self.processor.write_sheet(self.sample_df, 'SheetToUpdate')
        
        # Data to update, starting from C2
        update_data = pd.DataFrame({
            'ColC_new': [100, 200],
            'ColD_new': ['P', 'Q']
        })
        self.processor.update_sheet_range(update_data, 'SheetToUpdate', 'C2')
        
        # Read the updated sheet
        actual_df_after_update = self.processor.read_sheet('SheetToUpdate')
        
        # The read_sheet method will read the first row as headers.
        # If update_sheet_range writes data starting from C2, and C1, D1 are empty,
        # then pandas.read_excel will likely infer 'Unnamed: 2', 'Unnamed: 3' for these columns.
        
        # Let's find the column names dynamically
        # The original columns are 'ColA', 'ColB'. The new data starts at column C (index 2).
        # So, the columns should be 'ColA', 'ColB', 'Unnamed: 2', 'Unnamed: 3' (or similar).
        
        # We need to ensure the DataFrame has at least 4 columns for 'ColA', 'ColB', and the two updated columns.
        self.assertGreaterEqual(len(actual_df_after_update.columns), 4)

        # Check the values at the specific updated cells.
        # The first row of data in the updated range is at index 0 of the DataFrame (after headers).
        # The updated data starts at column C, which is the 3rd column (index 2) in the Excel sheet.
        # So, actual_df_after_update.iloc[0, 2] should be 100, actual_df_after_update.iloc[1, 2] should be 200.
        # And actual_df_after_update.iloc[0, 3] should be 'P', actual_df_after_update.iloc[1, 3] should be 'Q'.
        
        self.assertEqual(actual_df_after_update.iloc[0, 2], 100)
        self.assertEqual(actual_df_after_update.iloc[1, 2], 200)
        self.assertTrue(pd.isna(actual_df_after_update.iloc[2, 2]))
        
        self.assertEqual(actual_df_after_update.iloc[0, 3], 'P')
        self.assertEqual(actual_df_after_update.iloc[1, 3], 'Q')
        self.assertTrue(pd.isna(actual_df_after_update.iloc[2, 3]))

    def test_update_sheet_range_non_existent_sheet(self):
        update_df = pd.DataFrame({'Val': [1]})
        with patch("builtins.print") as mock_print:
            self.processor.write_sheet(self.sample_df, 'TempSheet') # Ensure file exists
            self.processor.update_sheet_range(update_df, "NonExistent", "A1")
            mock_print.assert_called_with("Erro: Planilha 'NonExistent' não encontrada.")

    def test_update_sheet_range_non_existent_file(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        update_df = pd.DataFrame({'Val': [1]})
        with patch("builtins.print") as mock_print:
            self.processor.update_sheet_range(update_df, "Sheet1", "A1")
            mock_print.assert_called_with(f"Erro: Arquivo Excel não encontrado em {self.test_file}")

if __name__ == '__main__':
    unittest.main()
