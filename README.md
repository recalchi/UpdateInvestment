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

2.  **Configure o `config.json`:**

    O arquivo `config/config.json` contém as configurações necessárias para a execução da automação. Preencha os campos com suas credenciais e IDs:

    ```json
    {
        "excel_file_path": "caminho/para/seu/arquivo.xlsx",
        "google_sheets": {
            "credentials_path": "caminho/para/suas/credenciais.json",
            "spreadsheet_id": "ID_DA_SUA_PLANILHA"
        },
        "telegram": {
            "bot_token": "SEU_TOKEN_DE_BOT",
            "chat_id": "SEU_CHAT_ID"
        },
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

## Testes

Para executar os testes unitários, utilize o seguinte comando na raiz do projeto:

```bash
python -m unittest discover -s tests
```

## Licença

Este projeto está licenciado sob a licença MIT. Consulte o arquivo `LICENSE` para mais detalhes.

