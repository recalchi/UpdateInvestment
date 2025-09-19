import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict, Any
import re

class LevanteConnector:
    def __init__(self, base_url: str = "https://app.levanteideias.com.br"): # Base URL para login
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.is_logged_in = False

    def _get_page_content(self, url: str) -> BeautifulSoup:
        """Fetches the content of a given URL and parses it with BeautifulSoup."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            return None

    def _download_csv(self, url: str, filename: str) -> str:
        """Downloads a CSV file from a given URL."""
        try:
            response = self.session.get(url, stream=True, timeout=10)
            response.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"CSV baixado para: {filename}")
            return filename
        except requests.exceptions.RequestException as e:
            print(f"Error downloading CSV from {url}: {e}")
            return None

    def login(self, email, password):
        login_url = f"{self.base_url}/users/sign_in"
        print(f"Tentando fazer login na Levante Ideias em: {login_url}")
        
        soup = self._get_page_content(login_url)
        if not soup:
            print("Não foi possível carregar a página de login da Levante Ideias.")
            return False

        # Extract CSRF token and other hidden fields if present
        auth_token = soup.find('meta', {'name': 'csrf-token'})
        if auth_token:
            auth_token = auth_token['content']
        else:
            print("CSRF token não encontrado na página de login da Levante.")
            return False

        form_data = {
            'user[email]': email,
            'user[password]': password,
            'authenticity_token': auth_token, # CSRF token
            'user[remember_me]': '0', # Or '1' if you want to remember
            'commit': 'Entrar'
        }

        try:
            response = self.session.post(login_url, data=form_data, timeout=10)
            response.raise_for_status()
            
            # Check if login was successful
            if "users/sign_in" not in response.url: # If not redirected back to login page
                print("Login na Levante Ideias bem-sucedido!")
                self.is_logged_in = True
                return True
            else:
                print("Login na Levante Ideias falhou. Verifique as credenciais.")
                self.is_logged_in = False
                return False
        except requests.exceptions.RequestException as e:
            print(f"Erro durante o login na Levante Ideias: {e}")
            self.is_logged_in = False
            return False

    def fetch_report_data_from_url(self, report_url: str) -> pd.DataFrame:
        """Fetches data from a specific report URL, trying to find CSV downloads or tables."""
        if not self.is_logged_in:
            print("Não logado na Levante Ideias. Por favor, faça login primeiro.")
            return pd.DataFrame()

        print(f"Acessando relatório em: {report_url}")
        soup = self._get_page_content(report_url)
        if not soup:
            return pd.DataFrame()

        # 1. Tentar encontrar links de download de CSV
        csv_links = soup.find_all('a', href=re.compile(r'.*\.csv$'))
        if csv_links:
            print(f"Encontrado(s) {len(csv_links)} link(s) de CSV na página.")
            csv_url = csv_links[0]['href']
            if not csv_url.startswith('http'):
                csv_url = self.base_url + csv_url # Ajustar para URL absoluta
            
            filename = f"levante_report_{report_url.split('/')[-1].replace('-', '_')}.csv"
            downloaded_file = self._download_csv(csv_url, filename)
            if downloaded_file:
                try:
                    df = pd.read_csv(downloaded_file)
                    print(f"Dados lidos do CSV: {downloaded_file}")
                    return df
                except Exception as e:
                    print(f"Erro ao ler CSV {downloaded_file}: {e}")

        # 2. Se não houver CSV, tentar extrair dados de tabelas HTML
        tables = soup.find_all('table')
        if tables:
            print(f"Encontrado(s) {len(tables)} tabela(s) na página.")
            try:
                df = pd.read_html(str(tables[0]))[0]
                print("Dados extraídos da primeira tabela HTML.")
                return df
            except Exception as e:
                print(f"Erro ao ler tabela HTML: {e}")

        print(f"Nenhum CSV ou tabela de dados encontrado em {report_url}.")
        return pd.DataFrame()

    def fetch_data(self, urls: List[str]) -> Dict[str, pd.DataFrame]:
        """Fetches data from a list of specific report URLs."""
        all_data = {}
        for url in urls:
            df = self.fetch_report_data_from_url(url)
            if not df.empty:
                all_data[url] = df
        return all_data


if __name__ == '__main__':
    levante = LevanteConnector()
    # Exemplo de URL de relatório da Levante (substitua por URLs reais)
    # if levante.login("recalchi.consultoria@gmail.com", "Gordinez123@"):
    #     report_urls = [
    #         "https://www.levanteideias.com.br/relatorio-exemplo-1", # Substitua por URLs reais
    #         "https://www.levanteideias.com.br/relatorio-exemplo-2"
    #     ]

    #     print("\nTentando buscar dados dos relatórios da Levante Ideias:")
    #     data_from_reports = levante.fetch_data(report_urls)

    #     for url, df in data_from_reports.items():
    #         print(f"\nDados do relatório {url}:")
    #         print(df.head())

    #     if not data_from_reports:
    #         print("Nenhum dado foi coletado dos relatórios da Levante Ideias.")
    # else:
    #     print("Não foi possível fazer login na Levante Ideias.")


