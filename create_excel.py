import pandas as pd

data = {
    'Ativo': ['PETR4.SA', 'VALE3.SA'],
    'Quantidade': [100, 50],
    'PrecoMedio': [25.00, 70.00]
}
df = pd.DataFrame(data)

with pd.ExcelWriter('portfolio.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Posicoes', index=False)

print('portfolio.xlsx criado com sucesso.')

