"""
Sistema de agendamento para automação da carteira de investimentos
Executa atualizações automáticas em intervalos definidos
"""

import schedule
import time
import threading
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import json
import os

from update_portfolio import PortfolioUpdater
from browser_orchestrator import BrowserOrchestrator



class PortfolioScheduler:
    def __init__(self, config_file="scheduler_config.json"):
        """
        Inicializa o sistema de agendamento
        
        Args:
            config_file (str): Arquivo de configuração do agendamento
        """
        self.config_file = config_file
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('portfolio_scheduler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Carregar configurações
        self.load_config()
        
        # Inicializar componentes
        self.portfolio_updater = PortfolioUpdater()
        self.browser_orchestrator = BrowserOrchestrator(headless=True)
        
    
    def load_config(self):
        """Carrega configurações do arquivo JSON"""
        default_config = {
            "frequency": "monthly",  # monthly, weekly, daily
            "day_of_month": 1,       # Para frequência mensal
            "hour": 9,               # Hora de execução
            "minute": 0,             # Minuto de execução
            "enabled": True,         # Se o agendamento está ativo
            "email_notifications": False,  # Enviar notificações por email
            "last_execution": None,  # Última execução
            "next_execution": None   # Próxima execução
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                    
                # Mesclar com configurações padrão
                for key, value in default_config.items():
                    if key not in self.config:
                        self.config[key] = value
            else:
                self.config = default_config
                self.save_config()
                
            self.logger.info(f"Configurações carregadas: {self.config}")
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {e}")
            self.config = default_config
    
    def save_config(self):
        """Salva configurações no arquivo JSON"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False, default=str)
            self.logger.info("Configurações salvas com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {e}")
    
    def update_config(self, new_config):
        """
        Atualiza configurações do agendamento
        
        Args:
            new_config (dict): Novas configurações
        """
        self.config.update(new_config)
        self.save_config()
        
        # Reagendar se necessário
        if self.is_running:
            self.stop_scheduler()
            self.start_scheduler()
    
    def execute_portfolio_update(self):
        """Executa a atualização completa da carteira"""
        try:
            self.logger.info("=== INICIANDO ATUALIZAÇÃO AUTOMÁTICA DA CARTEIRA ===")
            start_time = datetime.now()
            
            # 1. Executar atualização da carteira
            self.logger.info("Executando atualização da carteira...")
            success = self.portfolio_updater.run_update()
            
            if not success:
                self.logger.error("Falha na atualização da carteira")
                return False
            

            
            # 3. Atualizar timestamps
            end_time = datetime.now()
            execution_time = end_time - start_time
            
            self.config['last_execution'] = end_time.isoformat()
            self.calculate_next_execution()
            self.save_config()
            
            self.logger.info(f"=== ATUALIZAÇÃO CONCLUÍDA EM {execution_time} ===")
            
            # 4. Enviar notificação se habilitado
            if self.config.get('email_notifications', False):
                self.send_notification(success=True, execution_time=execution_time)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro durante execução automática: {e}")
            
            # Enviar notificação de erro
            if self.config.get('email_notifications', False):
                self.send_notification(success=False, error=str(e))
            
            return False
        
        finally:
            # Fechar recursos
            self.browser_orchestrator.close_driver()
    
    def calculate_next_execution(self):
        """Calcula a próxima execução baseada na configuração"""
        try:
            now = datetime.now()
            
            if self.config['frequency'] == 'monthly':
                # Próximo mês, mesmo dia e hora
                if now.day <= self.config['day_of_month']:
                    # Ainda não passou o dia deste mês
                    next_exec = now.replace(
                        day=self.config['day_of_month'],
                        hour=self.config['hour'],
                        minute=self.config['minute'],
                        second=0,
                        microsecond=0
                    )
                else:
                    # Já passou, vai para o próximo mês
                    if now.month == 12:
                        next_exec = now.replace(
                            year=now.year + 1,
                            month=1,
                            day=self.config['day_of_month'],
                            hour=self.config['hour'],
                            minute=self.config['minute'],
                            second=0,
                            microsecond=0
                        )
                    else:
                        next_exec = now.replace(
                            month=now.month + 1,
                            day=self.config['day_of_month'],
                            hour=self.config['hour'],
                            minute=self.config['minute'],
                            second=0,
                            microsecond=0
                        )
                        
            elif self.config['frequency'] == 'weekly':
                # Próxima semana, mesmo dia da semana e hora
                days_ahead = 7
                next_exec = now + timedelta(days=days_ahead)
                next_exec = next_exec.replace(
                    hour=self.config['hour'],
                    minute=self.config['minute'],
                    second=0,
                    microsecond=0
                )
                
            elif self.config['frequency'] == 'daily':
                # Próximo dia, mesma hora
                next_exec = now + timedelta(days=1)
                next_exec = next_exec.replace(
                    hour=self.config['hour'],
                    minute=self.config['minute'],
                    second=0,
                    microsecond=0
                )
            else:
                next_exec = now + timedelta(days=30)  # Fallback
            
            self.config['next_execution'] = next_exec.isoformat()
            self.logger.info(f"Próxima execução calculada: {next_exec}")
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular próxima execução: {e}")
    
    def start_scheduler(self):
        """Inicia o sistema de agendamento"""
        try:
            if not self.config.get('enabled', True):
                self.logger.info("Agendamento desabilitado na configuração")
                return
            
            # Limpar jobs existentes
            self.scheduler.remove_all_jobs()
            
            # Configurar job baseado na frequência
            if self.config['frequency'] == 'monthly':
                # Executar no dia X de cada mês
                self.scheduler.add_job(
                    func=self.execute_portfolio_update,
                    trigger=CronTrigger(
                        day=self.config['day_of_month'],
                        hour=self.config['hour'],
                        minute=self.config['minute']
                    ),
                    id='portfolio_update_monthly',
                    name='Atualização Mensal da Carteira',
                    replace_existing=True
                )
                
            elif self.config['frequency'] == 'weekly':
                # Executar semanalmente
                self.scheduler.add_job(
                    func=self.execute_portfolio_update,
                    trigger=CronTrigger(
                        day_of_week=0,  # Segunda-feira
                        hour=self.config['hour'],
                        minute=self.config['minute']
                    ),
                    id='portfolio_update_weekly',
                    name='Atualização Semanal da Carteira',
                    replace_existing=True
                )
                
            elif self.config['frequency'] == 'daily':
                # Executar diariamente
                self.scheduler.add_job(
                    func=self.execute_portfolio_update,
                    trigger=CronTrigger(
                        hour=self.config['hour'],
                        minute=self.config['minute']
                    ),
                    id='portfolio_update_daily',
                    name='Atualização Diária da Carteira',
                    replace_existing=True
                )
            
            # Iniciar scheduler
            self.scheduler.start()
            self.is_running = True
            
            # Calcular próxima execução
            self.calculate_next_execution()
            self.save_config()
            
            self.logger.info(f"Agendamento iniciado - Frequência: {self.config['frequency']}")
            self.logger.info(f"Próxima execução: {self.config['next_execution']}")
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar agendamento: {e}")
    
    def stop_scheduler(self):
        """Para o sistema de agendamento"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
            self.is_running = False
            self.logger.info("Agendamento parado")
        except Exception as e:
            self.logger.error(f"Erro ao parar agendamento: {e}")
    
    def get_status(self):
        """
        Retorna status atual do agendamento
        
        Returns:
            dict: Status do agendamento
        """
        return {
            "is_running": self.is_running,
            "frequency": self.config['frequency'],
            "next_execution": self.config.get('next_execution'),
            "last_execution": self.config.get('last_execution'),
            "enabled": self.config.get('enabled', True),
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in self.scheduler.get_jobs()
            ] if self.is_running else []
        }
    
    def send_notification(self, success=True, execution_time=None, error=None):
        """
        Envia notificação por email (placeholder)
        
        Args:
            success (bool): Se a execução foi bem-sucedida
            execution_time (timedelta): Tempo de execução
            error (str): Mensagem de erro se houver
        """
        # Placeholder para implementação de notificações por email
        # Em produção, integrar com serviço de email (SendGrid, AWS SES, etc.)
        
        if success:
            message = f"✅ Carteira atualizada com sucesso em {execution_time}"
        else:
            message = f"❌ Erro na atualização da carteira: {error}"
        
        self.logger.info(f"Notificação: {message}")
    
    def run_manual_update(self):
        """Executa atualização manual (fora do agendamento)"""
        self.logger.info("Executando atualização manual...")
        return self.execute_portfolio_update()

# Função para executar como serviço
def run_scheduler_service():
    """Executa o agendador como serviço em background"""
    scheduler = PortfolioScheduler()
    
    try:
        scheduler.start_scheduler()
        
        # Manter o serviço rodando
        while True:
            time.sleep(60)  # Verificar a cada minuto
            
    except KeyboardInterrupt:
        print("\nParando o agendador...")
        scheduler.stop_scheduler()
    except Exception as e:
        print(f"Erro no serviço de agendamento: {e}")
        scheduler.stop_scheduler()

if __name__ == "__main__":
    # Executar como serviço
    run_scheduler_service()




