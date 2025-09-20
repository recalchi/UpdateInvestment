import pandas as pd

excel_path = "portfolio.xlsx"

try:
    xls = pd.ExcelFile(excel_path)
    print("Abas encontradas na planilha:")
    for sheet_name in xls.sheet_names:
        print(f"- {sheet_name}")
except FileNotFoundError:
    print(f"Erro: O arquivo {excel_path} não foi encontrado.")
except Exception as e:
    print(f"Erro ao ler a planilha: {e}")

