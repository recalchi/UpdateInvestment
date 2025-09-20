import pandas as pd

excel_path = "portfolio.xlsx"
sheet_name = "BASE"

try:
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    print("Primeiras 5 linhas da planilha:")
    print(df.head().to_markdown(index=False))
    print("\nColunas da planilha:")
    print(df.columns.tolist())
except FileNotFoundError:
    print(f"Erro: O arquivo {excel_path} não foi encontrado.")
except Exception as e:
    print(f"Erro ao ler a planilha: {e}")

