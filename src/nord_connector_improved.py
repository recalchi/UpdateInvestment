import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
from typing import List, Dict, Any, Optional
import os
from datetime import datetime, timedelta

class NordConnectorImproved:
    def __init__(self, username: str = None, password: str = None):
        self.base_url = "https://www.nordinvestimentos.com.br"
        self.login_url = "https://members.nordinvestimentos.com.br/Login"
        self.session = requests.Session()
        self.username = username or os.getenv('NORD_USERNAME')
        self.password = password or os.getenv('NORD_PASSWORD')
        self.logged_in = False
        
        # Headers para simular um navegador
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def login(self) -> bool:
        """Tenta fazer login na Nord Research"""
        if not self.username or not self.password:
            print("Credenciais da Nord não fornecidas. Usando fallback para yfinance.")
            return False
        
        try:
            # Primeiro, obter a página de login para possíveis tokens CSRF
            login_page = self.session.get(self.login_url)
            soup = BeautifulSoup(login_page.text, 'html.parser')
            
            # Dados de login
            login_data = {
                'email': self.username,
                'password': self.password
            }
            
            # Procurar por tokens CSRF ou outros campos ocultos
            csrf_token = soup.find('input', {'name': '_token'})
            if csrf_token:
                login_data['_token'] = csrf_token.get('value')
            
            # Tentar fazer login
            response = self.session.post(self.login_url, data=login_data)
            
            # Verificar se o login foi bem-sucedido
            if response.status_code == 200 and 'dashboard' in response.url.lower():
                self.logged_in = True
                print("Login na Nord Research realizado com sucesso.")
                return True
            else:
                print("Falha no login da Nord Research. Usando fallback para yfinance.")
                return False
                
        except Exception as e:
            print(f"Erro ao fazer login na Nord Research: {e}. Usando fallback para yfinance.")
            return False

    def fetch_fiis_data(self, tickers: List[str]) -> pd.DataFrame:
        """Busca dados de FIIs da Nord ou usa yfinance como fallback"""
        if not self.logged_in and not self.login():
            return self._fetch_fiis_yfinance_fallback(tickers)
        
        try:
            # Tentar buscar dados da Nord (implementação específica seria necessária)
            # Por enquanto, usar fallback
            return self._fetch_fiis_yfinance_fallback(tickers)
        except Exception as e:
            print(f"Erro ao buscar dados de FIIs da Nord: {e}")
            return self._fetch_fiis_yfinance_fallback(tickers)

    def _fetch_fiis_yfinance_fallback(self, tickers: List[str]) -> pd.DataFrame:
        """Fallback usando yfinance para dados de FIIs"""
        fiis_data = []
        
        for ticker in tickers:
            try:
                # Adicionar .SA se não estiver presente
                ticker_formatted = ticker if ticker.endswith('.SA') else f"{ticker}.SA"
                
                # Buscar dados do último mês
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                
                stock = yf.Ticker(ticker_formatted)
                hist = stock.history(start=start_date, end=end_date)
                
                if not hist.empty:
                    # Calcular rentabilidade do último mês
                    first_price = hist['Close'].iloc[0]
                    last_price = hist['Close'].iloc[-1]
                    monthly_return = ((last_price - first_price) / first_price) * 100
                    
                    # Buscar informações adicionais
                    info = stock.info
                    
                    fiis_data.append({
                        'Ticker': ticker,
                        'Preco_Atual': last_price,
                        'Rentabilidade_Ultimo_Mes': monthly_return,
                        'Volume_Medio': hist['Volume'].mean(),
                        'Setor': info.get('sector', 'N/A'),
                        'Fonte': 'yfinance'
                    })
                    
            except Exception as e:
                print(f"Erro ao buscar dados para {ticker}: {e}")
                continue
        
        return pd.DataFrame(fiis_data)

    def fetch_top_fiis(self, limit: int = 10) -> pd.DataFrame:
        """Busca os top FIIs do mês"""
        if not self.logged_in and not self.login():
            return self._fetch_top_fiis_fallback(limit)
        
        try:
            # Implementação específica da Nord seria necessária aqui
            return self._fetch_top_fiis_fallback(limit)
        except Exception as e:
            print(f"Erro ao buscar top FIIs da Nord: {e}")
            return self._fetch_top_fiis_fallback(limit)

    def _fetch_top_fiis_fallback(self, limit: int = 10) -> pd.DataFrame:
        """Fallback para buscar FIIs populares usando uma lista conhecida"""
        # Lista de FIIs populares (seria melhor ter uma fonte dinâmica)
        popular_fiis = [
            'HGLG11', 'XPML11', 'VISC11', 'BCFF11', 'KNRI11',
            'MXRF11', 'HGRU11', 'IRDM11', 'BTLG11', 'KNCR11',
            'XPIN11', 'RBRF11', 'RBRR11', 'HGRE11', 'VILG11'
        ]
        
        return self.fetch_fiis_data(popular_fiis[:limit])

    def download_csv_report(self, report_type: str = 'fiis') -> Optional[str]:
        """Tenta baixar relatório CSV da Nord"""
        if not self.logged_in and not self.login():
            print("Não foi possível fazer login para baixar relatórios CSV.")
            return None
        
        try:
            # URL específica para download de CSV seria necessária
            # Esta é uma implementação placeholder
            csv_url = f"{self.base_url}/reports/{report_type}/download.csv"
            response = self.session.get(csv_url)
            
            if response.status_code == 200:
                filename = f"nord_{report_type}_{datetime.now().strftime('%Y%m%d')}.csv"
                filepath = os.path.join(os.getcwd(), filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                print(f"Relatório CSV baixado: {filepath}")
                return filepath
            else:
                print(f"Falha ao baixar relatório CSV: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Erro ao baixar relatório CSV: {e}")
            return None

    def fetch_data(self, tickers: List[str] = None, data_type: str = 'fiis') -> pd.DataFrame:
        """Método genérico para buscar dados"""
        if data_type == 'fiis':
            if tickers:
                return self.fetch_fiis_data(tickers)
            else:
                return self.fetch_top_fiis()
        else:
            return pd.DataFrame()

if __name__ == '__main__':
    # Teste do conector
    nord = NordConnectorImproved()
    
    print("Testando busca de FIIs...")
    fiis_data = nord.fetch_fiis_data(['HGLG11', 'XPML11', 'VISC11'])
    print(fiis_data)
    
    print("\nTestando busca de top FIIs...")
    top_fiis = nord.fetch_top_fiis(5)
    print(top_fiis)

