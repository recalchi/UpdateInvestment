"""
Rotas da API para o PortfolioPulse
Integração com sistema de agendamento e automação
"""

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import sys
import os
import threading
import logging
from datetime import datetime

# Adicionar o diretório src ao path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..', 'src'))

try:
    from scheduler import PortfolioScheduler
    from update_portfolio import PortfolioUpdater
    from browser_automation import GoogleSheetsAutomation
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    # Fallback para desenvolvimento
    PortfolioScheduler = None
    PortfolioUpdater = None
    GoogleSheetsAutomation = None

portfolio_bp = Blueprint('portfolio', __name__)

# Instância global do scheduler
scheduler_instance = None
update_thread = None
update_status = {
    "is_updating": False,
    "progress": 0,
    "current_step": "",
    "logs": [],
    "last_update": None,
    "error": None
}

def get_scheduler():
    """Obtém instância do scheduler (singleton)"""
    global scheduler_instance
    if scheduler_instance is None and PortfolioScheduler:
        scheduler_instance = PortfolioScheduler()
        scheduler_instance.start_scheduler()
    return scheduler_instance

@portfolio_bp.route('/status', methods=['GET'])
@cross_origin()
def get_portfolio_status():
    """Retorna status atual da carteira e agendamento"""
    try:
        scheduler = get_scheduler()
        
        # Dados simulados da carteira (em produção, ler de fonte real)
        portfolio_data = {
            "totalValue": 125430.50,
            "monthlyReturn": 3.2,
            "categories": [
                {"name": "Ações LP", "value": 35.2, "change": 2.1, "color": "#10b981"},
                {"name": "Ações DY", "value": 28.5, "change": 1.8, "color": "#3b82f6"},
                {"name": "STOCKS", "value": 18.3, "change": 4.2, "color": "#8b5cf6"},
                {"name": "FII", "value": 12.0, "change": 0.9, "color": "#f59e0b"},
                {"name": "Cripto", "value": 4.5, "change": -2.1, "color": "#ef4444"},
                {"name": "Renda Fixa", "value": 1.5, "change": 0.5, "color": "#6b7280"}
            ],
            "recentUpdates": [
                {"asset": "PRIO3", "action": "Atualizado", "time": "2 min", "status": "success"},
                {"asset": "BBSE3", "action": "Rebalanceado", "time": "5 min", "status": "warning"},
                {"asset": "META", "action": "Novo preço", "time": "8 min", "status": "info"}
            ]
        }
        
        # Status do agendamento
        scheduler_status = scheduler.get_status() if scheduler else {
            "is_running": False,
            "frequency": "monthly",
            "next_execution": None,
            "last_execution": None,
            "enabled": False,
            "jobs": []
        }
        
        return jsonify({
            "success": True,
            "portfolio": portfolio_data,
            "scheduler": scheduler_status,
            "update_status": update_status
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@portfolio_bp.route('/update', methods=['POST'])
@cross_origin()
def trigger_portfolio_update():
    """Dispara atualização manual da carteira"""
    global update_thread, update_status
    
    try:
        # Verificar se já está atualizando
        if update_status["is_updating"]:
            return jsonify({
                "success": False,
                "message": "Atualização já em andamento"
            }), 409
        
        # Iniciar atualização em thread separada
        update_thread = threading.Thread(target=run_portfolio_update)
        update_thread.daemon = True
        update_thread.start()
        
        return jsonify({
            "success": True,
            "message": "Atualização iniciada"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def run_portfolio_update():
    """Executa atualização da carteira em background"""
    global update_status
    
    try:
        update_status["is_updating"] = True
        update_status["progress"] = 0
        update_status["logs"] = []
        update_status["error"] = None
        
        steps = [
            "Conectando com Nord Research...",
            "Extraindo dados de Ações DY...",
            "Processando FIIs...",
            "Atualizando Stocks US...",
            "Calculando rentabilidades...",
            "Sincronizando com planilha...",
            "Atualização concluída!"
        ]
        
        for i, step in enumerate(steps):
            update_status["current_step"] = step
            update_status["progress"] = int((i + 1) / len(steps) * 100)
            
            # Adicionar log
            log_entry = {
                "message": step,
                "time": datetime.now().strftime("%H:%M:%S"),
                "type": "success" if i == len(steps) - 1 else "info"
            }
            update_status["logs"].append(log_entry)
            
            # Simular tempo de processamento
            import time
            time.sleep(2)
        
        update_status["last_update"] = datetime.now().isoformat()
        
    except Exception as e:
        update_status["error"] = str(e)
        logging.error(f"Erro na atualização: {e}")
    
    finally:
        update_status["is_updating"] = False

@portfolio_bp.route('/logs', methods=['GET'])
@cross_origin()
def get_update_logs():
    """Retorna logs da última atualização"""
    try:
        return jsonify({
            "success": True,
            "logs": update_status["logs"],
            "is_updating": update_status["is_updating"],
            "progress": update_status["progress"],
            "current_step": update_status["current_step"]
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@portfolio_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """Endpoint de health check"""
    return jsonify({
        "success": True,
        "message": "PortfolioPulse API está funcionando",
        "timestamp": datetime.now().isoformat()
    })

