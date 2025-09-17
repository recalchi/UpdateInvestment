# PortfolioPulse: Automação de Carteira de Investimentos

## Visão Geral

O PortfolioPulse é um sistema de automação projetado para simplificar e otimizar o gerenciamento de carteiras de investimentos. Ele integra dados de diversas fontes, processa informações financeiras, analisa o desempenho da carteira e atualiza automaticamente planilhas no Google Sheets, além de enviar notificações via Telegram. O objetivo é fornecer aos investidores uma ferramenta robusta para monitorar e ajustar suas estratégias de investimento com eficiência.

## Componentes Principais

### 1. Coordenador de Dados (`data_coordinator.py`)

Responsável por orquestrar a coleta e o processamento de dados de diferentes fontes. Ele atua como o hub central para agregar informações antes que sejam analisadas e utilizadas para atualização da carteira.

### 2. Processador de Excel (`excel_processor.py`)

Gerencia a leitura e escrita de dados em arquivos Excel. Essencial para importar dados de transações, posições atuais e outras informações relevantes que podem estar armazenadas em formato de planilha.

### 3. Atualizador do Google Sheets (`google_sheets_updater.py`)

Permite a interação com o Google Sheets API para ler e escrever dados. Fundamental para manter a carteira de investimentos atualizada em uma plataforma acessível e colaborativa.

### 4. Analisador de Investimentos (`investment_analyzer.py`)

Calcula métricas de desempenho, como retorno sobre investimento (ROI), volatilidade, e compara o desempenho da carteira com benchmarks. Fornece insights cruciais para a tomada de decisões.

### 5. Gerenciador de Portfólio (`portfolio_manager.py`)

Responsável por consolidar todas as informações da carteira, incluindo ativos, quantidades, preços médios e alocações. Ele interage com o analisador para obter insights e com o atualizador para refletir as mudanças.

### 6. Conectores de Dados (Ex: `yfinance_connector.py`, `nord_connector.py`, `levante_connector.py`)

Esses módulos são responsáveis por coletar dados de preços de ativos, notícias e relatórios de mercado de fontes específicas (Yahoo Finance, Nord Research, Levante Ideias de Investimento, etc.). Eles fornecem os dados brutos para o Coordenador de Dados.

### 7. Conector do Telegram (`telegram_connector.py`)

Permite o envio de notificações e alertas personalizados sobre o desempenho da carteira, eventos de mercado ou ações recomendadas diretamente para o usuário via Telegram.

### 8. Aplicação Principal (`main.py` ou `update_portfolio.py`)

O ponto de entrada do sistema, onde todos os componentes são inicializados e a lógica principal de automação é executada. Ele coordena o fluxo de trabalho desde a coleta de dados até a atualização e notificação.

## Fluxo de Trabalho Típico

1. **Coleta de Dados:** O `data_coordinator` utiliza os conectores (`yfinance_connector`, `nord_connector`, `levante_connector`) para coletar dados de mercado, preços de ativos e informações de relatórios.
2. **Processamento de Dados:** O `excel_processor` lê dados de transações e posições de arquivos Excel, enquanto o `data_coordinator` agrega e padroniza todas as informações.
3. **Análise da Carteira:** O `investment_analyzer` processa os dados agregados para calcular métricas de desempenho e identificar tendências.
4. **Gerenciamento e Atualização:** O `portfolio_manager` utiliza os resultados da análise para atualizar a estrutura da carteira. O `google_sheets_updater` então reflete essas mudanças na planilha do Google Sheets.
5. **Notificação:** O `telegram_connector` envia resumos, alertas ou recomendações com base nas atualizações e análises da carteira.

## Tecnologias Utilizadas

*   **Python:** Linguagem de programação principal.
*   **Pandas:** Para manipulação e análise de dados.
*   **OpenPyXL/Xlrd/Xlwt:** Para interação com arquivos Excel.
*   **Google Sheets API:** Para integração com planilhas Google.
*   **`python-telegram-bot`:** Para integração com o Telegram.
*   **`yfinance`:** Para dados de mercado do Yahoo Finance.
*   **Bibliotecas de Web Scraping (ex: `BeautifulSoup`, `Requests`):** Para coletar dados de Nord Research e Levante Ideias de Investimento.

## Próximos Passos

1.  **Configuração:** Detalhar as variáveis de ambiente e credenciais necessárias para cada conector (APIs, tokens, etc.).
2.  **Implementação:** Desenvolver os módulos conforme a arquitetura proposta.
3.  **Testes:** Criar testes unitários e de integração para garantir a robustez do sistema.
4.  **Deploy:** Estratégias para deploy em ambiente de produção (ex: cloud functions, servidores dedicados).

---

**Autor:** Agente IA (Manus AI)
**Data:** 16 de Setembro de 2025
