
import pandas as pd
import os
from openpyxl import load_workbook, Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import get_column_letter, column_index_from_string

class ExcelProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_sheet(self, sheet_name: str) -> pd.DataFrame:
        try:
            print(f"[ExcelProcessor] Tentando ler o arquivo: {self.file_path}, planilha: {sheet_name}")
            if not os.path.exists(self.file_path):
                print(f"[ExcelProcessor] Erro: Arquivo não encontrado em {self.file_path}")
                return pd.DataFrame()
            
            df = pd.read_excel(self.file_path, sheet_name=sheet_name, engine="openpyxl")
            print(f"[ExcelProcessor] DataFrame lido com {len(df)} linhas e {len(df.columns)} colunas.")
            print(f"[ExcelProcessor] Colunas: {df.columns.tolist()}")
            
            # Adicionar a coluna RENTABILIDADE_ULT_MES se não existir
            if "RENTABILIDADE_ULT_MES" not in df.columns:
                df["RENTABILIDADE_ULT_MES"] = 0.0  # Valor padrão

            # Adicionar a coluna DATA ATT se não existir
            if "DATA ATT" not in df.columns:
                df["DATA ATT"] = pd.to_datetime("today").strftime("%Y-%m-%d")

            return df
        except ValueError as ve: # Handles cases where the sheet does not exist
            print(f"Planilha \"{sheet_name}\" não encontrada ou erro de valor: {ve}")
            return pd.DataFrame()
        except Exception as e:
            print(f"Erro inesperado ao ler a planilha '{sheet_name}': {e}")
            return pd.DataFrame()

    def write_sheet(self, df: pd.DataFrame, sheet_name: str):
        try:
            # If file exists, load it to append/replace specific sheet
            if os.path.exists(self.file_path):
                with pd.ExcelWriter(self.file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                # If file does not exist, create a new one
                with pd.ExcelWriter(self.file_path, engine='openpyxl', mode='w') as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        except Exception as e:
            print(f"Erro ao escrever na planilha '{sheet_name}': {e}")

    def update_sheet_range(self, df_update: pd.DataFrame, sheet_name: str, start_cell: str):
        if not os.path.exists(self.file_path):
            print(f"Erro: Arquivo Excel não encontrado em {self.file_path}")
            return

        try:
            book = load_workbook(self.file_path)
            if sheet_name not in book.sheetnames:
                print(f"Erro: Planilha '{sheet_name}' não encontrada.")
                return
            
            ws = book[sheet_name]

            # Convert start_cell to row/column coordinates (1-based index for openpyxl)
            start_row = int("".join(filter(str.isdigit, start_cell)))
            start_col_str = "".join(filter(str.isalpha, start_cell))
            start_col = column_index_from_string(start_col_str)

            # Write the DataFrame data to the sheet, without headers
            # Iterate over DataFrame rows and write cell by cell
            for r_idx, row_data in enumerate(df_update.values):
                for c_idx, value in enumerate(row_data):
                    ws.cell(row=start_row + r_idx, column=start_col + c_idx, value=value)

            book.save(self.file_path)

        except Exception as e:
            print(f"Erro ao atualizar o intervalo da planilha '{sheet_name}': {e}")



    def create_historical_sheet(self, df: pd.DataFrame):
        try:
            today_str = pd.to_datetime("today").strftime("%Y%m%d")
            sheet_name = f"base{today_str}"
            self.write_sheet(df, sheet_name)
            print(f"Aba histórica \'{sheet_name}\' criada com sucesso.")
        except Exception as e:
            print(f"Erro ao criar aba histórica: {e}")

