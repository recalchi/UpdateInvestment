# Automação de Carteira de Investimentos (PortfolioPulse)

Este projeto é uma automação para atualização de carteiras de investimentos, que busca dados de diversas fontes, processa as informações e atualiza uma planilha com os dados consolidados.

## Estrutura do Projeto

O projeto está organizado da seguinte forma:

```
.UpdateInvestment/
├── src/                    # Código fonte da automação
│   ├── __init__.py
│   ├── data_coordinator.py
│   ├── excel_processor.py
│   ├── google_sheets_updater.py
│   ├── investment_analyzer.py
│   ├── levante_connector.py
│   ├── main.py
│   ├── nord_connector.py
│   ├── portfolio_manager.py
│   ├── telegram_connector.py
│   ├── update_portfolio.py
│   └── yfinance_connector.py
├── tests/                  # Testes unitários
│   ├── test_data_coordinator.py
│   ├── test_excel_processor.py
│   ├── test_investment_analyzer.py
│   ├── test_levante_connector.py
│   ├── test_nord_connector.py
│   ├── test_portfolio_manager.py
│   └── test_telegram_connector.py
├── docs/                   # Documentação do projeto
│   ├── PortfolioPulse_AutomaçãodeCarteiradeInvestimentos.md
│   ├── Relatorio_Melhorias_Automacao.md
│   └── promptinicial.txt
├── web/                    # Arquivos da interface web (se aplicável)
│   ├── App.css
│   ├── App.jsx
│   └── index.html
├── config/                 # Arquivos de configuração
│   └── config.json
├── requirements.txt        # Dependências do projeto
└── LICENSE                 # Licença do projeto
```

## Como Usar

1.  **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure o `config/config.json`:**

    O arquivo `config/config.json` contém as configurações necessárias para a execução da automação. Se ele não existir, será criado um arquivo de exemplo ao executar `python src/main.py`. Preencha os campos com suas credenciais e IDs:

    ```json
    {
        "excel_file_path": "caminho/para/seu/arquivo.xlsx",
        "excel_positions_sheet_name": "Posicoes",
        "google_sheets_credentials_path": "caminho/para/suas/credenciais.json",
        "google_sheets_spreadsheet_name": "MyInvestmentPortfolio",
        "google_sheets_summary_sheet_name": "Resumo",
        "google_sheets_details_sheet_name": "Detalhes",
        "google_sheets_spreadsheet_url": "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit",
        "telegram_bot_token": "SEU_TOKEN_DE_BOT",
        "telegram_chat_id": "SEU_CHAT_ID",
        "web_scraping": {
            "nord_url": "https://www.nordresearch.com.br/analises/",
            "levante_url": "https://www.levanteideias.com.br/analises/"
        }
    }
    ```

3.  **Atualize os Seletores de Web Scraping:**

    Os seletores CSS nos arquivos `src/nord_connector.py` e `src/levante_connector.py` são placeholders. Você **precisa** inspecionar os sites da Nord Research e Levante Ideias de Investimento e atualizar os seletores para que a coleta de dados funcione corretamente.

4.  **Execute a Automação:**

    ```bash
    python src/main.py
    ```

## Fluxo de Atualização da Carteira (Passo a Passo)

O processo de atualização da carteira de investimentos segue os seguintes passos, orquestrados pelo `PortfolioUpdater` em `src/update_portfolio.py`:

1.  **Carregamento das Posições da Carteira:**
    *   O `DataCoordinator` utiliza o `ExcelProcessor` para ler as posições atuais da sua carteira de um arquivo Excel (`excel_file_path` e `excel_positions_sheet_name` configurados no `config.json`).
    *   As posições são então carregadas no `PortfolioManager`.

2.  **Coleta de Preços Atuais:**
    *   Os tickers dos ativos da sua carteira são extraídos.
    *   O `DataCoordinator` utiliza o `YFinanceConnector` para buscar os preços mais recentes desses ativos no Yahoo Finance.
    *   Caso não seja possível obter os preços mais recentes, o sistema tentará usar os preços existentes como fallback, emitindo um aviso.
    *   Os preços atualizados são então repassados ao `PortfolioManager`.

3.  **Cálculo de Valores e Resumo da Carteira:**
    *   O `PortfolioManager` calcula o valor atual de cada posição e o valor total da carteira com base nos preços mais recentes.
    *   O `InvestmentAnalyzer` gera um resumo da carteira, incluindo métricas como valor total atual, total investido, lucro/prejuízo e ROI percentual.

4.  **Atualização do Google Sheets:**
    *   O `GoogleSheetsUpdater` é utilizado para enviar os dados atualizados da carteira para uma planilha específica no Google Sheets.
    *   São atualizadas duas planilhas: uma com o resumo geral (`google_sheets_summary_sheet_name`) e outra com os detalhes de cada posição (`google_sheets_details_sheet_name`).

5.  **Envio de Notificação via Telegram:**
    *   O `TelegramConnector` envia uma mensagem para um chat do Telegram (configurado no `config.json`) com um resumo da atualização da carteira, incluindo os principais indicadores e um link para a planilha do Google Sheets.

## Testes

Para executar os testes unitários, utilize o seguinte comando na raiz do projeto:

```bash
python -m unittest discover -s tests
```

## Licença

Este projeto está licenciado sob a licença MIT. Consulte o arquivo `LICENSE` para mais detalhes.

