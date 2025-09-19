
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import os
import glob

class BrowserOrchestrator:
    def __init__(self, headless=True):
        self.driver = None
        self.headless = headless
        self.wait_timeout = 20  # Aumentado para 20 segundos
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def setup_driver(self):
        """Configura e inicializa o driver do Chrome."""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            
            # Configurar diretório de download para o driver
            download_dir = os.path.join(os.getcwd(), "downloads")
            os.makedirs(download_dir, exist_ok=True)
            prefs = {"download.default_directory": download_dir,
                     "download.prompt_for_download": False,
                     "download.directory_upgrade": True,
                     "safebrowsing.enabled": True}
            chrome_options.add_experimental_option("prefs", prefs)

            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.wait_timeout)
            self.logger.info("Driver do Chrome inicializado com sucesso.")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao inicializar driver: {e}")
            return False

    def navigate(self, url):
        """Navega para a URL especificada."""
        try:
            self.driver.get(url)
            self.logger.info(f"Navegado para: {url}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao navegar para {url}: {e}")
            return False

    def login_nord(self, email, password):
        """Realiza o login na Nord Research."""
        login_url = "https://members.nordinvestimentos.com.br/Login"
        self.navigate(login_url)
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "Email"))).send_keys(email)
            self.driver.find_element(By.ID, "Senha").send_keys(password)
            self.driver.find_element(By.XPATH, "//button[@type=\'submit\']").click()
            self.wait.until(EC.url_to_be("https://members.nordinvestimentos.com.br/")) # Espera redirecionar para a página inicial
            self.logger.info("Login na Nord Research bem-sucedido via Selenium.")
            return True
        except TimeoutException:
            self.logger.error("Timeout ao tentar fazer login na Nord Research. Credenciais inválidas ou página não carregou.")
            return False
        except Exception as e:
            self.logger.error(f"Erro durante o login na Nord Research: {e}")
            return False

    def login_levante(self, email, password):
        """Realiza o login na Levante Ideias."""
        login_url = "https://www.levanteideias.com.br/login/"
        self.navigate(login_url)
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "user_login"))).send_keys(email)
            self.driver.find_element(By.ID, "user_pass").send_keys(password)
            self.driver.find_element(By.ID, "wp-submit").click()
            # Pode ser necessário ajustar a URL de destino ou um elemento específico para verificar o login
            self.wait.until(EC.url_contains("levanteideias.com.br/minha-conta")) # Exemplo, ajustar conforme a página pós-login
            self.logger.info("Login na Levante Ideias bem-sucedido via Selenium.")
            return True
        except TimeoutException:
            self.logger.error("Timeout ao tentar fazer login na Levante Ideias. Credenciais inválidas ou página não carregou.")
            return False
        except Exception as e:
            self.logger.error(f"Erro durante o login na Levante Ideias: {e}")
            return False

    def extract_nord_data(self, url):
        """Extrai dados de uma URL da Nord Research, tentando usar o botão CSV."""
        self.navigate(url)
        try:
            # Tentar encontrar o botão CSV
            csv_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, \'buttons-csv\')] | //a[contains(text(), \'CSV\')] | //button[contains(span, \'CSV\')] | //button[contains(@class, \'dt-button\') and contains(@class, \'buttons-csv\')] "))
            )
            self.logger.info("Botão CSV encontrado. Clicando para baixar...")
            csv_button.click()
            time.sleep(5)  # Dar tempo para o download iniciar e completar
            self.logger.info("Download do CSV da Nord Research iniciado.")
            # Esperar o arquivo CSV ser baixado
            download_dir = os.path.join(os.getcwd(), "downloads")
            downloaded_file = self._wait_for_download(download_dir, ".csv")
            if downloaded_file:
                self.logger.info(f"Arquivo CSV baixado: {downloaded_file}")
                df = pd.read_csv(downloaded_file)
                os.remove(downloaded_file) # Limpar o arquivo baixado
                return df
            else:
                self.logger.error("Não foi possível baixar o arquivo CSV da Nord Research.")
                return pd.DataFrame()
        except TimeoutException:
            self.logger.warning("Botão CSV não encontrado ou não clicável. Tentando extrair da tabela HTML...")
            return self._extract_table_from_html()
        except Exception as e:
            self.logger.error(f"Erro ao extrair dados da Nord Research de {url}: {e}")
            return pd.DataFrame()

    def _extract_table_from_html(self):
        """Extrai dados de uma tabela HTML na página atual."""
        try:
            table = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            self.logger.info("Tabela HTML encontrada. Extraindo dados...")
            df = pd.read_html(self.driver.page_source)[0]
            self.logger.info("Dados extraídos da tabela HTML.")
            return df
        except TimeoutException:
            self.logger.error("Nenhuma tabela HTML encontrada na página.")
            return pd.DataFrame()
        except Exception as e:
            self.logger.error(f"Erro ao extrair tabela HTML: {e}")
            return pd.DataFrame()

    def extract_levante_data(self, url):
        """Extrai dados de uma URL da Levante Ideias, tentando usar o botão de download."""
        self.navigate(url)
        try:
            # Tentar encontrar um botão de download ou link para CSV/Excel
            download_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, \'.csv\')] | //a[contains(@href, \'.xls\')] | //a[contains(@href, \'.xlsx\')] | //button[contains(text(), \'Download\')] "))
            )
            self.logger.info("Botão de download encontrado. Clicando para baixar...")
            download_button.click()
            time.sleep(5)  # Dar tempo para o download iniciar e completar
            self.logger.info("Download da Levante Ideias iniciado.")
            download_dir = os.path.join(os.getcwd(), "downloads")
            downloaded_file = self._wait_for_download(download_dir, ".csv") or self._wait_for_download(download_dir, ".xls") or self._wait_for_download(download_dir, ".xlsx")
            if downloaded_file:
                self.logger.info(f"Arquivo baixado: {downloaded_file}")
                if downloaded_file.endswith(".csv"):
                    df = pd.read_csv(downloaded_file)
                elif downloaded_file.endswith(".xls") or downloaded_file.endswith(".xlsx"):
                    df = pd.read_excel(downloaded_file)
                else:
                    self.logger.error("Formato de arquivo não suportado.")
                    return pd.DataFrame()
                os.remove(downloaded_file) # Limpar o arquivo baixado
                return df
            else:
                self.logger.error("Não foi possível baixar o arquivo da Levante Ideias.")
                return pd.DataFrame()
        except TimeoutException:
            self.logger.warning("Botão de download não encontrado ou não clicável. Verifique a página.")
            return pd.DataFrame()
        except Exception as e:
            self.logger.error(f"Erro ao extrair dados da Levante Ideias de {url}: {e}")
            return pd.DataFrame()

    def close_driver(self):
        """Fecha o driver do navegador."""
        if self.driver:
            self.driver.quit()
            self.logger.info("Driver do navegador fechado.")

if __name__ == "__main__":
    orchestrator = BrowserOrchestrator(headless=False)
    if orchestrator.setup_driver():
        # Exemplo de uso para Nord Research
        nord_email = "renan.recalchi.adm@gmail.com"
        nord_password = "Gordinez123@"
        if orchestrator.login_nord(nord_email, nord_password):
            nord_dividendos_url = "https://members.nordinvestimentos.com.br/conteudo/41-dividendos-o-que-comprar-"
            nord_data = orchestrator.extract_nord_data(nord_dividendos_url)
            if not nord_data.empty:
                print("Dados da Nord Research (Dividendos) extraídos:")
                print(nord_data.head())

        # Exemplo de uso para Levante Ideias
        levante_email = "recalchi.consultoria@gmail.com"
        levante_password = "Gordinez123@"
        if orchestrator.login_levante(levante_email, levante_password):
            # URL de exemplo para Levante, precisa ser ajustada para uma página com download
            levante_exemplo_url = "https://www.levanteideias.com.br/analises-e-relatorios/"
            levante_data = orchestrator.extract_levante_data(levante_exemplo_url)
            if not levante_data.empty:
                print("Dados da Levante Ideias extraídos:")
                print(levante_data.head())

        orchestrator.close_driver()





    def _wait_for_download(self, download_dir, extension, timeout=30):
        """Espera por um arquivo com a extensão especificada no diretório de download."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            list_of_files = glob.glob(os.path.join(download_dir, f"*{extension}"))
            if list_of_files:
                # Encontrar o arquivo mais recente
                latest_file = max(list_of_files, key=os.path.getctime)
                # Verificar se o download está completo (tamanho não muda por um curto período)
                initial_size = os.path.getsize(latest_file)
                time.sleep(1)
                current_size = os.path.getsize(latest_file)
                if initial_size == current_size:
                    return latest_file
            time.sleep(0.5)
        return None


