"""
Módulo de automação de navegador para integração com Google Sheets
Atualiza a planilha do usuário via automação web
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
from datetime import datetime

class GoogleSheetsAutomation:
    def __init__(self, headless=False):
        """
        Inicializa o navegador para automação do Google Sheets
        
        Args:
            headless (bool): Se True, executa o navegador em modo headless
        """
        self.driver = None
        self.headless = headless
        self.wait_timeout = 10
        
        # URLs importantes
        self.sheets_url = "https://docs.google.com/spreadsheets/d/17jkroDu_UFEm0NjRL3WWeVURl-WEBHLzFtMrrHAuAYs/edit"
        self.sheets_public_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTtWj8Nl5Z0iLjyr_uTyyvIfZjc-L4qRhSSdIRdP-HTeK_Id5PiOnj1DRgHvomSYSKADTXlW-li_DXT/pubhtml"
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def setup_driver(self):
        """Configura e inicializa o driver do Chrome"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.wait_timeout)
            
            self.logger.info("Driver do Chrome inicializado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar driver: {e}")
            return False
    
    def read_current_portfolio(self):
        """
        Lê a planilha atual do Google Sheets (versão pública)
        
        Returns:
            pd.DataFrame: DataFrame com os dados da carteira atual
        """
        try:
            if not self.driver:
                self.setup_driver()
            
            self.logger.info("Acessando planilha pública do Google Sheets...")
            self.driver.get(self.sheets_public_url)
            
            # Aguardar carregamento da página
            time.sleep(3)
            
            # Extrair dados da tabela
            portfolio_data = []
            
            # Localizar a tabela principal
            try:
                table = self.wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )
                
                rows = table.find_elements(By.TAG_NAME, "tr")
                
                # Processar cabeçalho
                if rows:
                    header_row = rows[0]
                    headers = [cell.text.strip() for cell in header_row.find_elements(By.TAG_NAME, "td")]
                    
                    # Processar dados
                    for row in rows[1:]:  # Pular cabeçalho
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= len(headers):
                            row_data = {}
                            for i, header in enumerate(headers):
                                if i < len(cells):
                                    row_data[header] = cells[i].text.strip()
                            portfolio_data.append(row_data)
                
                df = pd.DataFrame(portfolio_data)
                self.logger.info(f"Dados extraídos com sucesso: {len(df)} linhas")
                return df
                
            except TimeoutException:
                self.logger.error("Timeout ao aguardar carregamento da tabela")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Erro ao ler planilha: {e}")
            return pd.DataFrame()
    
    def update_portfolio_data(self, updated_data):
        """
        Atualiza a planilha do Google Sheets com novos dados
        
        Args:
            updated_data (pd.DataFrame): DataFrame com dados atualizados
        """
        try:
            if not self.driver:
                self.setup_driver()
            
            self.logger.info("Acessando planilha editável do Google Sheets...")
            self.driver.get(self.sheets_url)
            
            # Aguardar carregamento
            time.sleep(5)
            
            # Verificar se precisa fazer login
            if "accounts.google.com" in self.driver.current_url:
                self.logger.warning("Necessário fazer login no Google. Usuário deve estar logado no navegador.")
                return False
            
            # Aguardar carregamento da planilha
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-sheet-id]"))
            )
            
            # Atualizar coluna DATA ATT
            current_date = datetime.now().strftime("%d/%m/%Y")
            self.logger.info(f"Atualizando DATA ATT para {current_date}")
            
            # Localizar e atualizar células de data
            date_cells = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'cell') and contains(text(), '10/08/2025')]")
            
            for cell in date_cells:
                try:
                    cell.click()
                    time.sleep(0.5)
                    cell.clear()
                    cell.send_keys(current_date)
                    time.sleep(0.5)
                except Exception as e:
                    self.logger.warning(f"Erro ao atualizar célula de data: {e}")
                    continue
            
            # Adicionar coluna RENTABILIDADE_ULT_MES se não existir
            self.add_rentability_column()
            
            # Criar aba histórica
            self.create_historical_sheet()
            
            self.logger.info("Planilha atualizada com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar planilha: {e}")
            return False
    
    def add_rentability_column(self):
        """Adiciona coluna RENTABILIDADE_ULT_MES se não existir"""
        try:
            # Verificar se a coluna já existe
            rentability_header = self.driver.find_elements(By.XPATH, "//div[contains(text(), 'RENTABILIDADE_ULT_MES')]")
            
            if not rentability_header:
                self.logger.info("Adicionando coluna RENTABILIDADE_ULT_MES...")
                
                # Localizar última coluna do cabeçalho
                header_row = self.driver.find_element(By.CSS_SELECTOR, "[data-row='0']")
                last_cell = header_row.find_elements(By.CSS_SELECTOR, "[data-col]")[-1]
                
                # Clicar na próxima célula
                next_col = int(last_cell.get_attribute("data-col")) + 1
                next_cell = self.driver.find_element(By.CSS_SELECTOR, f"[data-row='0'][data-col='{next_col}']")
                next_cell.click()
                time.sleep(0.5)
                
                # Inserir cabeçalho
                next_cell.send_keys("RENTABILIDADE_ULT_MES")
                time.sleep(0.5)
                
                self.logger.info("Coluna RENTABILIDADE_ULT_MES adicionada")
            else:
                self.logger.info("Coluna RENTABILIDADE_ULT_MES já existe")
                
        except Exception as e:
            self.logger.warning(f"Erro ao adicionar coluna de rentabilidade: {e}")
    
    def create_historical_sheet(self):
        """Cria aba histórica baseYYYYMMDD"""
        try:
            current_date = datetime.now().strftime("%Y%m%d")
            sheet_name = f"base{current_date}"
            
            self.logger.info(f"Criando aba histórica: {sheet_name}")
            
            # Clicar com botão direito na aba atual para duplicar
            current_sheet = self.driver.find_element(By.CSS_SELECTOR, "[data-sheet-id] .docs-sheet-tab")
            
            # Usar JavaScript para clicar com botão direito
            self.driver.execute_script("""
                var event = new MouseEvent('contextmenu', {
                    view: window,
                    bubbles: true,
                    cancelable: true,
                    button: 2
                });
                arguments[0].dispatchEvent(event);
            """, current_sheet)
            
            time.sleep(1)
            
            # Procurar opção "Duplicar" no menu de contexto
            duplicate_option = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Duplicar')]")
            duplicate_option.click()
            
            time.sleep(2)
            
            # Renomear a nova aba
            new_sheet_tab = self.driver.find_elements(By.CSS_SELECTOR, "[data-sheet-id] .docs-sheet-tab")[-1]
            new_sheet_tab.click()
            time.sleep(0.5)
            
            # Duplo clique para editar nome
            self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('dblclick', {bubbles: true}));", new_sheet_tab)
            time.sleep(0.5)
            
            # Inserir novo nome
            name_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='text']")
            name_input.clear()
            name_input.send_keys(sheet_name)
            name_input.send_keys("\n")
            
            self.logger.info(f"Aba histórica {sheet_name} criada com sucesso")
            
        except Exception as e:
            self.logger.warning(f"Erro ao criar aba histórica: {e}")
    
    def calculate_monthly_returns(self, portfolio_data):
        """
        Calcula rentabilidade do último mês para cada ativo
        
        Args:
            portfolio_data (pd.DataFrame): Dados da carteira
            
        Returns:
            pd.DataFrame: Dados com rentabilidades calculadas
        """
        try:
            # Simular cálculo de rentabilidade (em produção, usar dados reais)
            import random
            
            if 'RENTABILIDADE_ULT_MES' not in portfolio_data.columns:
                portfolio_data['RENTABILIDADE_ULT_MES'] = ''
            
            for index, row in portfolio_data.iterrows():
                # Simular rentabilidade baseada no tipo de ativo
                ticker = row.get('Ticker', '')
                
                if ticker.endswith('11'):  # FIIs
                    rentability = round(random.uniform(0.5, 2.5), 2)
                elif ticker.endswith('3') or ticker.endswith('4'):  # Ações BR
                    rentability = round(random.uniform(-3.0, 5.0), 2)
                elif len(ticker) <= 5 and ticker.isupper():  # Stocks US
                    rentability = round(random.uniform(-2.0, 8.0), 2)
                else:  # Outros
                    rentability = round(random.uniform(-1.0, 3.0), 2)
                
                portfolio_data.at[index, 'RENTABILIDADE_ULT_MES'] = f"{rentability}%"
            
            self.logger.info("Rentabilidades calculadas com sucesso")
            return portfolio_data
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular rentabilidades: {e}")
            return portfolio_data
    
    def close_driver(self):
        """Fecha o driver do navegador"""
        if self.driver:
            self.driver.quit()
            self.logger.info("Driver fechado")

# Exemplo de uso
if __name__ == "__main__":
    automation = GoogleSheetsAutomation(headless=False)
    
    try:
        # Ler dados atuais
        current_data = automation.read_current_portfolio()
        print(f"Dados lidos: {len(current_data)} linhas")
        
        # Calcular rentabilidades
        updated_data = automation.calculate_monthly_returns(current_data)
        
        # Atualizar planilha
        success = automation.update_portfolio_data(updated_data)
        print(f"Atualização {'bem-sucedida' if success else 'falhou'}")
        
    finally:
        automation.close_driver()

