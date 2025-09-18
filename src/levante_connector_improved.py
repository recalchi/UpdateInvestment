import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
from typing import List, Dict, Any, Optional
import os
from datetime import datetime, timedelta

class LevanteConnectorImproved:
    def __init__(self, username: str = None, password: str = None):
        self.base_url = "https://levanteideias.com.br"
        self.session = requests.Session()
        self.username = username or os.getenv('LEVANTE_USERNAME')
        self.password = password or os.getenv('LEVANTE_PASSWORD')
        self.logged_in = False
        
        # Headers para simular um navegador
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def login(self) -> bool:
        """Tenta fazer login na Levante Ideias"""
        if not self.username or not self.password:
            print("Credenciais da Levante não fornecidas. Usando fallback para APIs públicas.")
            return False
        
        try:
            # Procurar pela página de login
            login_page = self.session.get(f"{self.base_url}/login")
            soup = BeautifulSoup(login_page.text, 'html.parser')
            
            # Dados de login (ajustar conforme necessário)
            login_data = {
                'email': self.username,
                'password': self.password
            }
            
            # Procurar por tokens CSRF
            csrf_token = soup.find('input', {'name': '_token'})
            if csrf_token:
                login_data['_token'] = csrf_token.get('value')
            
            # Tentar fazer login
            response = self.session.post(f"{self.base_url}/login", data=login_data)
            
            if response.status_code == 200 and 'dashboard' in response.url.lower():
                self.logged_in = True
                print("Login na Levante Ideias realizado com sucesso.")
                return True
            else:
                print("Falha no login da Levante Ideias. Usando fallback para APIs públicas.")
                return False
                
        except Exception as e:
            print(f"Erro ao fazer login na Levante Ideias: {e}. Usando fallback para APIs públicas.")
            return False

    def fetch_crypto_data(self, symbols: List[str] = None) -> pd.DataFrame:
        """Busca dados de criptomoedas da Levante ou usa API pública como fallback"""
        if not self.logged_in and not self.login():
            return self._fetch_crypto_public_fallback(symbols)
        
        try:
            # Implementação específica da Levante seria necessária aqui
            return self._fetch_crypto_public_fallback(symbols)
        except Exception as e:
            print(f"Erro ao buscar dados de cripto da Levante: {e}")
            return self._fetch_crypto_public_fallback(symbols)

    def _fetch_crypto_public_fallback(self, symbols: List[str] = None) -> pd.DataFrame:
        """Fallback usando API pública para dados de criptomoedas"""
        if not symbols:
            # Priorizar BTC, ETH, SOL + 2 altcoins como especificado
            symbols = ['bitcoin', 'ethereum', 'solana', 'cardano', 'polkadot']
        
        crypto_data = []
        
        try:
            # Usar CoinGecko API (gratuita)
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': ','.join(symbols),
                'vs_currencies': 'usd,brl',
                'include_24hr_change': 'true',
                'include_30d_change': 'true'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                for symbol, info in data.items():
                    crypto_data.append({
                        'Symbol': symbol.upper(),
                        'Preco_USD': info.get('usd', 0),
                        'Preco_BRL': info.get('brl', 0),
                        'Variacao_24h': info.get('usd_24h_change', 0),
                        'Variacao_30d': info.get('usd_30d_change', 0),
                        'Fonte': 'CoinGecko'
                    })
            
        except Exception as e:
            print(f"Erro ao buscar dados de cripto via API pública: {e}")
        
        return pd.DataFrame(crypto_data)

    def fetch_stocks_recommendations(self, category: str = 'dy') -> pd.DataFrame:
        """Busca recomendações de ações (DY, LP, Stocks US)"""
        if not self.logged_in and not self.login():
            return self._fetch_stocks_fallback(category)
        
        try:
            # Implementação específica da Levante seria necessária aqui
            return self._fetch_stocks_fallback(category)
        except Exception as e:
            print(f"Erro ao buscar recomendações de ações da Levante: {e}")
            return self._fetch_stocks_fallback(category)

    def _fetch_stocks_fallback(self, category: str = 'dy') -> pd.DataFrame:
        """Fallback para recomendações de ações usando listas conhecidas"""
        stocks_data = []
        
        if category == 'dy':  # Dividend Yield
            tickers = ['ITSA4', 'BBDC4', 'PETR4', 'VALE3', 'BBAS3']
        elif category == 'lp':  # Longo Prazo
            tickers = ['MGLU3', 'WEGE3', 'ASAI3', 'RENT3', 'RADL3']
        elif category == 'us':  # Stocks US
            tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'CCJ']  # Incluindo CCJ como especificado
        else:
            tickers = []
        
        for ticker in tickers:
            try:
                # Adicionar .SA para ações brasileiras
                if category != 'us':
                    ticker_formatted = f"{ticker}.SA"
                else:
                    ticker_formatted = ticker
                
                stock = yf.Ticker(ticker_formatted)
                info = stock.info
                hist = stock.history(period="1mo")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    monthly_return = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                    
                    stocks_data.append({
                        'Ticker': ticker,
                        'Preco_Atual': current_price,
                        'Rentabilidade_Ultimo_Mes': monthly_return,
                        'Categoria': category.upper(),
                        'Setor': info.get('sector', 'N/A'),
                        'Fonte': 'yfinance'
                    })
                    
            except Exception as e:
                print(f"Erro ao buscar dados para {ticker}: {e}")
                continue
        
        return pd.DataFrame(stocks_data)

    def download_pdf_report(self, report_type: str = 'crypto') -> Optional[str]:
        """Tenta baixar relatório PDF da Levante"""
        if not self.logged_in and not self.login():
            print("Não foi possível fazer login para baixar relatórios PDF.")
            return None
        
        try:
            # URL específica para download de PDF seria necessária
            pdf_url = f"{self.base_url}/reports/{report_type}/download.pdf"
            response = self.session.get(pdf_url)
            
            if response.status_code == 200:
                filename = f"levante_{report_type}_{datetime.now().strftime('%Y%m%d')}.pdf"
                filepath = os.path.join(os.getcwd(), filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                print(f"Relatório PDF baixado: {filepath}")
                return filepath
            else:
                print(f"Falha ao baixar relatório PDF: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Erro ao baixar relatório PDF: {e}")
            return None

    def fetch_renda_fixa_data(self) -> pd.DataFrame:
        """Busca dados de renda fixa ou usa Tesouro Direto como fallback"""
        try:
            # Usar API do Tesouro Direto (pública)
            url = "https://www.tesourotransparente.gov.br/ckan/api/3/action/datastore_search"
            params = {
                'resource_id': 'af6ebb98-2057-4cf7-9aaa-2a3a0c1a9e9f',  # ID do dataset do Tesouro
                'limit': 10
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                records = data.get('result', {}).get('records', [])
                
                renda_fixa_data = []
                for record in records:
                    renda_fixa_data.append({
                        'Titulo': record.get('titulo', 'N/A'),
                        'Taxa': record.get('taxa', 0),
                        'Vencimento': record.get('vencimento', 'N/A'),
                        'Preco': record.get('preco', 0),
                        'Fonte': 'Tesouro Direto'
                    })
                
                return pd.DataFrame(renda_fixa_data)
            
        except Exception as e:
            print(f"Erro ao buscar dados de renda fixa: {e}")
        
        return pd.DataFrame()

    def fetch_data(self, data_type: str = 'crypto', **kwargs) -> pd.DataFrame:
        """Método genérico para buscar dados"""
        if data_type == 'crypto':
            return self.fetch_crypto_data(kwargs.get('symbols'))
        elif data_type == 'stocks':
            return self.fetch_stocks_recommendations(kwargs.get('category', 'dy'))
        elif data_type == 'renda_fixa':
            return self.fetch_renda_fixa_data()
        else:
            return pd.DataFrame()

if __name__ == '__main__':
    # Teste do conector
    levante = LevanteConnectorImproved()
    
    print("Testando busca de criptomoedas...")
    crypto_data = levante.fetch_crypto_data()
    print(crypto_data)
    
    print("\nTestando busca de ações DY...")
    dy_stocks = levante.fetch_stocks_recommendations('dy')
    print(dy_stocks)
    
    print("\nTestando busca de renda fixa...")
    renda_fixa = levante.fetch_renda_fixa_data()
    print(renda_fixa)

