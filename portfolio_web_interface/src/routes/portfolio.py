from flask import Blueprint, request, jsonify
import sys
import os

# Adicionar o diretório pai ao path para importar módulos do projeto principal
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from update_portfolio import PortfolioUpdater
from excel_processor import ExcelProcessor
from browser_orchestrator import BrowserOrchestrator

portfolio_bp = Blueprint('portfolio', __name__)

# Instância global do atualizador de portfólio
portfolio_updater = None

def get_portfolio_updater():
    global portfolio_updater
    if portfolio_updater is None:
        portfolio_updater = PortfolioUpdater()
    return portfolio_updater

@portfolio_bp.route('/status', methods=['GET'])
def get_status():
    """Retorna o status atual do sistema."""
    try:
        return jsonify({
            'status': 'running',
            'message': 'Sistema de atualização de portfólio operacional'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@portfolio_bp.route('/config', methods=['GET'])
def get_config():
    """Retorna a configuração atual do sistema."""
    try:
        updater = get_portfolio_updater()
        config = updater.config
        
        # Remover credenciais sensíveis da resposta
        safe_config = config.copy()
        if 'nord_credentials' in safe_config:
            safe_config['nord_credentials'] = {'email': safe_config['nord_credentials'].get('email', ''), 'password': '***'}
        if 'levante_credentials' in safe_config:
            safe_config['levante_credentials'] = {'email': safe_config['levante_credentials'].get('email', ''), 'password': '***'}
        
        return jsonify(safe_config)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@portfolio_bp.route('/config', methods=['POST'])
def update_config():
    """Atualiza a configuração do sistema."""
    try:
        data = request.get_json()
        updater = get_portfolio_updater()
        
        # Atualizar configuração (implementar validação conforme necessário)
        for key, value in data.items():
            if key in updater.config:
                updater.config[key] = value
        
        # Salvar configuração (implementar persistência se necessário)
        
        return jsonify({
            'status': 'success',
            'message': 'Configuração atualizada com sucesso'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@portfolio_bp.route('/update', methods=['POST'])
def run_update():
    """Executa uma atualização manual do portfólio."""
    try:
        updater = get_portfolio_updater()
        success = updater.run_update()
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Atualização do portfólio executada com sucesso'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Falha na atualização do portfólio'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@portfolio_bp.route('/portfolio', methods=['GET'])
def get_portfolio():
    """Retorna os dados atuais do portfólio."""
    try:
        updater = get_portfolio_updater()
        excel_processor = ExcelProcessor(updater.config['excel_file_path'])
        
        # Ler dados do portfólio
        positions_df = excel_processor.read_sheet(updater.config['excel_positions_sheet_name'])
        
        if positions_df.empty:
            return jsonify({
                'status': 'success',
                'data': [],
                'message': 'Nenhuma posição encontrada'
            })
        
        # Converter DataFrame para lista de dicionários
        portfolio_data = positions_df.to_dict('records')
        
        return jsonify({
            'status': 'success',
            'data': portfolio_data,
            'total_positions': len(portfolio_data)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@portfolio_bp.route('/test-nord', methods=['POST'])
def test_nord_connection():
    """Testa a conexão com Nord Research."""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'status': 'error',
                'message': 'Email e senha são obrigatórios'
            }), 400
        
        browser = BrowserOrchestrator(headless=True)
        success = False
        
        if browser.setup_driver():
            success = browser.login_nord(email, password)
            browser.close_driver()
        
        return jsonify({
            'status': 'success' if success else 'error',
            'message': 'Conexão com Nord Research bem-sucedida' if success else 'Falha na conexão com Nord Research'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@portfolio_bp.route('/test-levante', methods=['POST'])
def test_levante_connection():
    """Testa a conexão com Levante Ideias."""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'status': 'error',
                'message': 'Email e senha são obrigatórios'
            }), 400
        
        browser = BrowserOrchestrator(headless=True)
        success = False
        
        if browser.setup_driver():
            success = browser.login_levante(email, password)
            browser.close_driver()
        
        return jsonify({
            'status': 'success' if success else 'error',
            'message': 'Conexão com Levante Ideias bem-sucedida' if success else 'Falha na conexão com Levante Ideias'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

