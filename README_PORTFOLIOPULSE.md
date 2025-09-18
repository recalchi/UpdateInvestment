# PortfolioPulse 📈

**Automação Inteligente para Carteira de Investimentos**

Uma solução completa e moderna para automatizar a atualização e otimização de carteiras de investimentos, integrando dados de múltiplas fontes com interface web profissional e sincronização automática com Google Sheets.

---

## 🎯 **Visão Geral**

O PortfolioPulse é uma evolução completa do projeto UpdateInvestment, desenvolvido para automatizar todo o processo de gestão de carteiras de investimentos. O sistema combina conectores inteligentes para fontes de dados premium (Nord Research, Levante Ideias) com fallbacks para APIs públicas, oferecendo uma interface web moderna e sistema de agendamento robusto.

### **Principais Características**

- **🤖 Automação Completa**: Atualização automática mensal, semanal ou diária
- **🎨 Interface Moderna**: Dashboard dark mode com métricas em tempo real
- **📊 Múltiplas Fontes**: Nord Research, Levante Ideias, yfinance, APIs públicas
- **📈 Otimização Inteligente**: Algoritmos de rebalanceamento e substituição de ativos
- **☁️ Sincronização**: Integração automática com Google Sheets via browser automation
- **📱 Responsivo**: Interface adaptável para desktop e mobile
- **🔒 Seguro**: Credenciais protegidas, logs detalhados, fallbacks gracioso

---

## 🏗️ **Arquitetura do Sistema**

### **Componentes Principais**

```
PortfolioPulse/
├── src/                          # Lógica de negócio
│   ├── update_portfolio.py       # Orquestrador principal
│   ├── excel_processor.py        # Processamento de planilhas
│   ├── browser_automation.py     # Automação Google Sheets
│   ├── scheduler.py              # Sistema de agendamento
│   ├── nord_connector.py         # Conector Nord Research
│   ├── levante_connector.py      # Conector Levante Ideias
│   └── portfolio_optimizer.py    # Otimização de carteira
├── PortfolioPulse/               # Backend Flask
│   └── src/
│       ├── main.py               # Servidor principal
│       └── routes/
│           └── portfolio.py      # API endpoints
└── PortfolioPulse-frontend/      # Frontend React
    └── src/
        ├── App.jsx               # Interface principal
        └── components/           # Componentes UI
```

### **Fluxo de Dados**

1. **Trigger** → Interface web ou agendamento automático
2. **Extração** → Conectores acessam fontes de dados (Nord/Levante/APIs)
3. **Processamento** → Cálculo de rentabilidades e otimizações
4. **Atualização** → Sincronização com planilha local e Google Sheets
5. **Feedback** → Logs em tempo real e notificações

---


## 🚀 **Instalação e Configuração**

### **Pré-requisitos**

- **Python 3.8+** com pip instalado
- **Node.js 18+** com npm instalado
- **Google Chrome** ou Chromium para automação web
- **Conta Google** para sincronização com Google Sheets
- **Acesso às plataformas** Nord Research e/ou Levante Ideias (opcional)

### **Instalação Rápida**

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/recalchi/UpdateInvestment.git
   cd UpdateInvestment
   ```

2. **Instale dependências Python:**
   ```bash
   pip install -r requirements.txt
   pip install selenium apscheduler flask-cors
   ```

3. **Configure o backend Flask:**
   ```bash
   cd PortfolioPulse
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

4. **Configure o frontend React:**
   ```bash
   cd ../PortfolioPulse-frontend
   npm install
   ```

### **Configuração do Ambiente**

1. **Arquivo .env** (raiz do projeto):
   ```env
   # Configurações da Nord Research (opcional)
   NORD_USERNAME=seu_usuario
   NORD_PASSWORD=sua_senha
   
   # Configurações da Levante Ideias (opcional)
   LEVANTE_USERNAME=seu_usuario
   LEVANTE_PASSWORD=sua_senha
   
   # Configurações do sistema
   PORTFOLIO_FILE_PATH=C:\Users\Renan\OneDrive\Documentos\planilhas\Carteira_Investimento_test\Carteira_Investimento_test.xlsx
   GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/17jkroDu_UFEm0NjRL3WWeVURl-WEBHLzFtMrrHAuAYs/edit
   ```

2. **Configuração do Google Sheets:**
   - Abra sua planilha no Google Sheets
   - Certifique-se de que está logado na conta Google
   - O sistema usará automação de navegador para sincronização

3. **Estrutura da Planilha:**
   ```
   Colunas obrigatórias:
   - NOME DA EMPRESA
   - TICKER
   - PESO
   - PREÇO TETO
   - CARTEIRA
   - DATA ATT
   - OBS
   - RENTABILIDADE_ULT_MES (será criada automaticamente)
   ```

---

## 🎮 **Como Usar**

### **Execução via Interface Web**

1. **Inicie o backend:**
   ```bash
   cd PortfolioPulse
   python src/main.py
   ```
   O servidor estará disponível em `http://localhost:5000`

2. **Inicie o frontend:**
   ```bash
   cd PortfolioPulse-frontend
   npm run dev
   ```
   A interface estará disponível em `http://localhost:5173`

3. **Acesse o PortfolioPulse:**
   - Abra `http://localhost:5173` no navegador
   - Use o dashboard para monitorar sua carteira
   - Clique em "Atualizar Carteira" para execução manual
   - Configure agendamento na aba "Configurações"

### **Execução via Linha de Comando**

```bash
# Atualização manual completa
python src/main.py

# Apenas conectores específicos
python src/nord_connector_improved.py
python src/levante_connector_improved.py

# Sistema de agendamento
python src/scheduler.py
```

### **Interface Web - Funcionalidades**

#### **Dashboard Principal**
- **Valor Total da Carteira**: Valor consolidado com variação mensal
- **Status da Automação**: Estado atual do sistema (Pronto/Executando)
- **Próxima Execução**: Countdown para próxima atualização automática
- **Distribuição por Categorias**: Gráfico de pizza interativo
- **Atualizações Recentes**: Timeline das últimas modificações

#### **Abas Disponíveis**

1. **Visão Geral**: Dashboard principal com métricas consolidadas
2. **Categorias**: Detalhamento por tipo de investimento (Ações LP, DY, STOCKS, FII, Cripto, Renda Fixa)
3. **Logs**: Terminal em tempo real com progresso das atualizações
4. **Configurações**: Personalização de frequência, caminhos e notificações

#### **Sistema de Logs**
```
[12:23:46 AM] Conectando com Nord Research...
[12:23:47 AM] Extraindo dados de Ações DY...
[12:23:48 AM] Processando FIIs...
[12:23:49 AM] Atualizando Stocks US...
[12:23:50 AM] Calculando rentabilidades...
[12:23:51 AM] Sincronizando com planilha...
[12:23:52 AM] Atualização concluída!
```

---

## 📊 **Conectores de Dados**

### **Nord Research Integration**

O sistema mapeia automaticamente as seguintes páginas da Nord Research:

| Categoria | URL | Dados Extraídos |
|-----------|-----|-----------------|
| **Ações DY** | `/conteudo/41-dividendos-o-que-comprar-` | BBSE3, ITUB3, RECV3, VLID3, SPY111, POMO3 |
| **FIIs** | `/conteudo/121-fundos-imobiliarios` | VRTA11, RBRY11, RBRF11, VILG11, HSML11 |
| **Stocks US** | `/conteudo/112-global` | TSM, META, HALO, KWEB, ASML, NFLX |
| **Ações LP** | `/conteudo/5-o-investidor-de-valor` | PRIO3, BPAC11, INBR32, SHUL4, CSUD3, MILS3 |
| **Renda Fixa** | `/conteudo/7-renda-fixa-pro` | Tesouro Selic, IPCA+, Prefixado |

**Funcionalidades:**
- Login automático com credenciais do .env
- Download de CSVs das tabelas "O QUE COMPRAR"
- Fallback para yfinance se credenciais não disponíveis
- Análise de performance e recomendações de rebalanceamento

### **Levante Ideias Integration**

Focado em criptomoedas e análises complementares:

- **Relatórios PDF**: Download automático de relatórios mensais
- **Sinais Telegram**: Integração com canal de sinais (opcional)
- **Priorização**: BTC, ETH, SOL + 2 altcoins selecionadas
- **Análise Técnica**: Indicadores e tendências de mercado

### **APIs Públicas (Fallback)**

Quando credenciais premium não estão disponíveis:

- **yfinance**: Preços e dados históricos de ações e FIIs
- **CoinGecko**: Cotações de criptomoedas
- **Tesouro Direto**: Taxas oficiais de renda fixa
- **B3 API**: Dados complementares do mercado brasileiro

---

## ⚙️ **Sistema de Agendamento**

### **Configuração de Frequência**

```json
{
  "frequency": "monthly",
  "day_of_month": 1,
  "hour": 9,
  "minute": 0,
  "enabled": true,
  "email_notifications": false
}
```

### **Opções Disponíveis**

- **Mensal**: 1º dia de cada mês (recomendado)
- **Quinzenal**: A cada 15 dias
- **Semanal**: Toda segunda-feira
- **Diário**: Todos os dias úteis

### **Monitoramento**

- **Status em Tempo Real**: Via API `/status`
- **Logs Persistentes**: Arquivo `portfolio_scheduler.log`
- **Próxima Execução**: Cálculo automático baseado na configuração
- **Recuperação de Falhas**: Retry automático em caso de erro

---

## 🔧 **Otimização de Carteira**

### **Algoritmos Implementados**

#### **Rebalanceamento Automático**
- Análise de performance relativa por categoria
- Identificação de ativos com baixo desempenho
- Sugestões de substituição baseadas em critérios objetivos
- Manutenção de pesos target por categoria

#### **Regras de Otimização**

1. **FIIs**: Substituir por top 10 do mês se rentabilidade < -2%
2. **Ações DY**: Priorizar dividend yield > 6% e payout < 80%
3. **Ações LP**: Manter WEG, avaliar P/VPA e ROE
4. **Stocks US**: Incluir CCJ, diversificar setores
5. **Cripto**: Manter 70% BTC/ETH/SOL, 30% altcoins
6. **Renda Fixa**: Seguir alocação 55% pós-fixado, 35% IPCA+, 10% prefixado

#### **Métricas de Avaliação**
- **Rentabilidade Acumulada**: Performance histórica
- **Volatilidade**: Risco ajustado
- **Correlação**: Diversificação do portfólio
- **Liquidez**: Facilidade de negociação
- **Fundamentals**: Indicadores financeiros

---

## 🔒 **Segurança e Boas Práticas**

### **Proteção de Credenciais**
- Variáveis de ambiente para senhas
- Nunca commit de credenciais no código
- Criptografia local opcional
- Timeout automático de sessões

### **Logs e Auditoria**
- Registro detalhado de todas as operações
- Timestamps precisos para rastreabilidade
- Separação de logs por nível (INFO, WARNING, ERROR)
- Rotação automática de arquivos de log

### **Tratamento de Erros**
- Fallbacks gracioso para todas as fontes de dados
- Retry automático com backoff exponencial
- Notificações de falhas críticas
- Continuidade de operação mesmo com falhas parciais

### **Backup e Recuperação**
- Criação automática de abas históricas (baseYYYYMMDD)
- Backup local antes de modificações
- Versionamento de configurações
- Rollback automático em caso de falhas

---


## 🌐 **API Reference**

### **Endpoints Disponíveis**

#### **GET /api/status**
Retorna status atual da carteira e sistema de agendamento.

```json
{
  "success": true,
  "portfolio": {
    "totalValue": 125430.50,
    "monthlyReturn": 3.2,
    "categories": [
      {
        "name": "Ações LP",
        "value": 35.2,
        "change": 2.1,
        "color": "#10b981"
      }
    ],
    "recentUpdates": [
      {
        "asset": "PRIO3",
        "action": "Atualizado",
        "time": "2 min",
        "status": "success"
      }
    ]
  },
  "scheduler": {
    "is_running": true,
    "frequency": "monthly",
    "next_execution": "2025-10-01T09:00:00",
    "last_execution": "2025-09-01T09:00:00"
  }
}
```

#### **POST /api/update**
Dispara atualização manual da carteira.

```json
{
  "success": true,
  "message": "Atualização iniciada"
}
```

#### **GET /api/logs**
Retorna logs da última atualização em tempo real.

```json
{
  "success": true,
  "logs": [
    {
      "message": "Conectando com Nord Research...",
      "time": "12:23:46",
      "type": "info"
    }
  ],
  "is_updating": false,
  "progress": 100
}
```

#### **GET /api/health**
Health check do sistema.

```json
{
  "success": true,
  "message": "PortfolioPulse API está funcionando",
  "timestamp": "2025-09-17T12:23:46.123Z"
}
```

---

## 🛠️ **Troubleshooting**

### **Problemas Comuns**

#### **1. Erro "No positions found in Excel"**
```bash
# Verificar se o arquivo existe
ls -la "C:\Users\Renan\OneDrive\Documentos\planilhas\Carteira_Investimento_test\"

# Verificar estrutura da planilha
python -c "
import pandas as pd
df = pd.read_excel('caminho/para/planilha.xlsx')
print(df.columns.tolist())
print(df.head())
"
```

**Solução**: Certifique-se de que a planilha contém as colunas obrigatórias e dados válidos.

#### **2. Erro de Login Nord Research/Levante**
```bash
# Verificar credenciais no .env
cat .env | grep -E "(NORD|LEVANTE)"

# Testar login manual
python src/nord_connector_improved.py
```

**Solução**: Verifique se as credenciais estão corretas e se as contas estão ativas.

#### **3. Erro de Sincronização Google Sheets**
```bash
# Verificar se o Chrome está instalado
google-chrome --version
# ou
chromium --version

# Testar automação
python src/browser_automation.py
```

**Solução**: Instale o Chrome/Chromium e certifique-se de estar logado na conta Google.

#### **4. Frontend não carrega**
```bash
# Verificar se o backend está rodando
curl http://localhost:5000/api/health

# Verificar logs do React
cd PortfolioPulse-frontend
npm run dev
```

**Solução**: Inicie o backend antes do frontend e verifique se as portas estão livres.

### **Logs de Debug**

#### **Habilitar Logs Detalhados**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### **Localização dos Logs**
- **Sistema**: `portfolio_scheduler.log`
- **Backend**: Console do Flask
- **Frontend**: Console do navegador (F12)
- **Automação**: `browser_automation.log`

### **Performance e Otimização**

#### **Configurações Recomendadas**
```json
{
  "headless_browser": true,
  "timeout_seconds": 30,
  "retry_attempts": 3,
  "cache_duration_minutes": 15
}
```

#### **Monitoramento de Recursos**
```bash
# CPU e memória
top -p $(pgrep -f "python.*main.py")

# Espaço em disco
df -h

# Conexões de rede
netstat -an | grep :5000
```

---

## 📚 **Exemplos de Uso**

### **Exemplo 1: Configuração Básica**

```python
# config_example.py
from src.scheduler import PortfolioScheduler
from src.browser_automation import GoogleSheetsAutomation

# Configurar agendamento mensal
scheduler = PortfolioScheduler()
scheduler.update_config({
    "frequency": "monthly",
    "day_of_month": 1,
    "hour": 9,
    "minute": 0,
    "enabled": True
})

# Iniciar automação
scheduler.start_scheduler()
print("Agendamento configurado para 1º de cada mês às 9h")
```

### **Exemplo 2: Atualização Manual**

```python
# manual_update.py
from src.update_portfolio import PortfolioUpdater
from src.browser_automation import GoogleSheetsAutomation

# Executar atualização completa
updater = PortfolioUpdater()
success = updater.run_update()

if success:
    # Sincronizar com Google Sheets
    sheets = GoogleSheetsAutomation(headless=True)
    current_data = sheets.read_current_portfolio()
    updated_data = sheets.calculate_monthly_returns(current_data)
    sheets.update_portfolio_data(updated_data)
    sheets.close_driver()
    print("Atualização concluída com sucesso!")
else:
    print("Falha na atualização")
```

### **Exemplo 3: Análise de Performance**

```python
# performance_analysis.py
import pandas as pd
from src.portfolio_optimizer import PortfolioOptimizer

# Carregar dados da carteira
df = pd.read_excel("carteira.xlsx")

# Analisar performance
optimizer = PortfolioOptimizer()
analysis = optimizer.analyze_performance(df)

print(f"Rentabilidade total: {analysis['total_return']:.2f}%")
print(f"Melhor ativo: {analysis['best_performer']}")
print(f"Pior ativo: {analysis['worst_performer']}")

# Sugestões de otimização
suggestions = optimizer.get_optimization_suggestions(df)
for suggestion in suggestions:
    print(f"- {suggestion}")
```

### **Exemplo 4: Integração com Webhook**

```python
# webhook_integration.py
from flask import Flask, request, jsonify
from src.scheduler import PortfolioScheduler

app = Flask(__name__)
scheduler = PortfolioScheduler()

@app.route('/webhook/update', methods=['POST'])
def webhook_update():
    """Endpoint para trigger externo"""
    try:
        # Validar token de segurança
        token = request.headers.get('Authorization')
        if token != 'Bearer YOUR_SECRET_TOKEN':
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Executar atualização
        success = scheduler.run_manual_update()
        
        return jsonify({
            'success': success,
            'message': 'Atualização executada via webhook'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

---

## 🚀 **Deploy e Produção**

### **Deploy Local (Desenvolvimento)**

```bash
# 1. Configurar ambiente
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configurar variáveis
cp .env.example .env
# Editar .env com suas configurações

# 3. Iniciar serviços
# Terminal 1 - Backend
cd PortfolioPulse
python src/main.py

# Terminal 2 - Frontend
cd PortfolioPulse-frontend
npm run dev

# Terminal 3 - Scheduler (opcional)
python src/scheduler.py
```

### **Deploy em Servidor (Produção)**

```bash
# 1. Configurar servidor
sudo apt update
sudo apt install python3 python3-pip nodejs npm chromium-browser

# 2. Clonar e configurar
git clone https://github.com/recalchi/UpdateInvestment.git
cd UpdateInvestment
pip3 install -r requirements.txt

# 3. Configurar systemd service
sudo nano /etc/systemd/system/portfoliopulse.service
```

```ini
[Unit]
Description=PortfolioPulse Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/UpdateInvestment/PortfolioPulse
ExecStart=/usr/bin/python3 src/main.py
Restart=always
Environment=PYTHONPATH=/path/to/UpdateInvestment

[Install]
WantedBy=multi-user.target
```

```bash
# 4. Ativar e iniciar serviço
sudo systemctl enable portfoliopulse
sudo systemctl start portfoliopulse
sudo systemctl status portfoliopulse

# 5. Configurar nginx (opcional)
sudo nano /etc/nginx/sites-available/portfoliopulse
```

### **Deploy com Docker**

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Configurar diretório de trabalho
WORKDIR /app

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar código fonte
COPY . .

# Expor porta
EXPOSE 5000

# Comando de inicialização
CMD ["python", "PortfolioPulse/src/main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  portfoliopulse-backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped

  portfoliopulse-frontend:
    build:
      context: ./PortfolioPulse-frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - portfoliopulse-backend
    restart: unless-stopped
```

```bash
# Executar com Docker
docker-compose up -d
```

---

## 📈 **Roadmap e Melhorias Futuras**

### **Versão 2.0 - Planejada**

#### **Novas Funcionalidades**
- **📱 App Mobile**: React Native para iOS/Android
- **🤖 IA Integrada**: Recomendações baseadas em machine learning
- **📊 Dashboards Avançados**: Gráficos interativos com Chart.js
- **🔔 Notificações Push**: Alertas em tempo real
- **📧 Relatórios por Email**: Resumos automáticos mensais
- **🌐 Multi-idioma**: Suporte para inglês e espanhol

#### **Integrações Adicionais**
- **🏦 Bancos**: Open Banking para saldos automáticos
- **📱 Corretoras**: APIs diretas (Rico, XP, BTG)
- **📈 Análise Técnica**: Indicadores avançados (RSI, MACD, Bollinger)
- **🌍 Mercados Globais**: Ações europeias e asiáticas
- **💰 DeFi**: Protocolos de finanças descentralizadas

#### **Melhorias Técnicas**
- **⚡ Performance**: Cache Redis, otimização de queries
- **🔐 Segurança**: Autenticação 2FA, criptografia end-to-end
- **📊 Analytics**: Métricas de uso, performance tracking
- **🧪 Testes**: Cobertura 100%, testes E2E
- **📦 CI/CD**: Deploy automático, rollback inteligente

### **Versão 1.1 - Próximas Melhorias**

- [ ] **Otimização de Performance**: Cache de dados, requests paralelos
- [ ] **Melhor UX**: Loading states, animações, feedback visual
- [ ] **Configurações Avançadas**: Customização de regras de otimização
- [ ] **Backup Automático**: Sincronização com cloud storage
- [ ] **Alertas Inteligentes**: Notificações baseadas em thresholds
- [ ] **Relatórios PDF**: Geração automática de relatórios mensais

---

## 🤝 **Contribuição**

### **Como Contribuir**

1. **Fork** o repositório
2. **Crie** uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. **Commit** suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/nova-funcionalidade`)
5. **Abra** um Pull Request

### **Diretrizes de Desenvolvimento**

- **Código**: Seguir PEP 8 para Python, ESLint para JavaScript
- **Testes**: Manter cobertura > 80%
- **Documentação**: Atualizar README e docstrings
- **Commits**: Usar Conventional Commits
- **Issues**: Usar templates fornecidos

### **Estrutura de Commits**

```
feat: adiciona integração com nova corretora
fix: corrige erro de sincronização com Google Sheets
docs: atualiza documentação da API
style: formata código conforme PEP 8
refactor: reorganiza estrutura dos conectores
test: adiciona testes para portfolio optimizer
chore: atualiza dependências
```

---

## 📄 **Licença**

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

```
MIT License

Copyright (c) 2025 PortfolioPulse

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 **Suporte e Contato**

### **Documentação e Recursos**

- **📖 Wiki**: [GitHub Wiki](https://github.com/recalchi/UpdateInvestment/wiki)
- **🐛 Issues**: [GitHub Issues](https://github.com/recalchi/UpdateInvestment/issues)
- **💬 Discussões**: [GitHub Discussions](https://github.com/recalchi/UpdateInvestment/discussions)
- **📺 Demos**: [YouTube Channel](https://youtube.com/portfoliopulse)

### **Comunidade**

- **💬 Discord**: [PortfolioPulse Community](https://discord.gg/portfoliopulse)
- **📱 Telegram**: [@portfoliopulse_br](https://t.me/portfoliopulse_br)
- **🐦 Twitter**: [@PortfolioPulse](https://twitter.com/portfoliopulse)
- **📧 Email**: support@portfoliopulse.com

### **Agradecimentos**

Agradecimentos especiais a:

- **Nord Research** pela qualidade dos dados e análises
- **Levante Ideias** pelas insights de criptomoedas
- **Comunidade Open Source** pelas bibliotecas utilizadas
- **Beta Testers** pelos feedbacks valiosos
- **Contribuidores** que ajudaram a melhorar o projeto

---

**Desenvolvido com ❤️ pela comunidade PortfolioPulse**

*"Automatize seus investimentos, maximize seus resultados"*

---

## 📊 **Estatísticas do Projeto**

![GitHub stars](https://img.shields.io/github/stars/recalchi/UpdateInvestment?style=social)
![GitHub forks](https://img.shields.io/github/forks/recalchi/UpdateInvestment?style=social)
![GitHub issues](https://img.shields.io/github/issues/recalchi/UpdateInvestment)
![GitHub license](https://img.shields.io/github/license/recalchi/UpdateInvestment)
![Python version](https://img.shields.io/badge/python-3.8+-blue.svg)
![React version](https://img.shields.io/badge/react-18+-blue.svg)
![Flask version](https://img.shields.io/badge/flask-2.0+-green.svg)

**Última atualização**: Setembro 2025  
**Versão**: 1.0.0  
**Status**: Produção  
**Mantenedor**: [@recalchi](https://github.com/recalchi)

