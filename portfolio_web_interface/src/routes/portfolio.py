# portfolio_web_interface/src/routes/portfolio.py
import os
import sys
import logging
import json
from datetime import datetime

from flask import Blueprint, request, jsonify

# logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adicionar o diretório 'src' do projeto ao path para permitir imports relativos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

# Importar util de serialização seguro (com fallback caso o package não esteja estruturado)
try:
    from src.utils.serialize import df_to_safe_records
except Exception:
    try:
        from utils.serialize import df_to_safe_records
    except Exception:
        # fallback: função minimal (não ideal — só para evitar crash se util não existir)
        import numpy as notnull
# fallback: função minimal (não ideal — só para evitar crash se util não existir)
        import pandas as _pd

        def df_to_safe_records(df):
            if df is None or df.empty:
                return []
            # Trocar NaN / NaT por None para JSON válido
            return df.where(_pd.notnull(df), None).to_dict(orient="records")

        logger.warning("df_to_safe_records fallback in use. Install src.utils.serialize for full behaviour.")

# Importar classes do package src (com fallback)
try:
    from update_portfolio import PortfolioUpdater
except Exception:
    try:
        from src.update_portfolio import PortfolioUpdater
    except Exception:
        PortfolioUpdater = None
        logger.warning("Não foi possível importar PortfolioUpdater (update_portfolio).")

try:
    from excel_processor import ExcelProcessor
except Exception:
    try:
        from src.excel_processor import ExcelProcessor
    except Exception:
        ExcelProcessor = None
        logger.warning("Não foi possível importar ExcelProcessor (src.excel_processor).")

try:
    from browser_orchestrator import BrowserOrchestrator
except Exception:
    try:
        from src.browser_orchestrator import BrowserOrchestrator
    except Exception:
        BrowserOrchestrator = None
        logger.warning("Não foi possível importar BrowserOrchestrator (src.browser_orchestrator).")

# Blueprint
portfolio_bp = Blueprint('portfolio', __name__)

# Instância global do atualizador de portfólio
portfolio_updater = None

def get_portfolio_updater():
    global portfolio_updater
    if portfolio_updater is None:
        if PortfolioUpdater is None:
            raise RuntimeError("PortfolioUpdater não está disponível (import falhou).")
        portfolio_updater = PortfolioUpdater()
    return portfolio_updater

def debug_df(df, name="df"):
    """Log simples para saber formas, dtypes e contagem de nulos."""
    try:
        if df is None:
            logger.info(f"[DEBUG] {name} is None")
            return
        logger.info(f"[DEBUG] {name} shape={df.shape}")
        # dtypes pode lançar em alguns casos; envolver em try
        try:
            logger.info(f"[DEBUG] {name} dtypes:\\n{df.dtypes}")
        except Exception as e:
            logger.info(f"[DEBUG] {name} dtypes unavailable: {e}")
        try:
            nulls = df.isnull().sum()
            nulls = nulls[nulls > 0]
            if not nulls.empty:
                logger.info(f"[DEBUG] {name} null counts: {nulls.to_dict()}")
        except Exception as e:
            logger.info(f"[DEBUG] {name} null check failed: {e}")
    except Exception as e:
        logger.info(f"[DEBUG] debug_df error: {e}")

# Rotas
@portfolio_bp.route('/status', methods=['GET'])
def get_status():
    """Retorna o status atual do sistema."""
    try:
        return jsonify({
            'status': 'running',
            'message': 'Sistema de atualização de portfólio operacional',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.exception("Erro em /status")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@portfolio_bp.route('/config', methods=['GET'])
def get_config():
    """Retorna a configuração atual do sistema (sem credenciais sensíveis)."""
    try:
        updater = get_portfolio_updater()
        config = getattr(updater, "config", {}) or {}

        # Remover credenciais sensíveis da resposta
        safe_config = dict(config)  # shallow copy
        if 'nord_credentials' in safe_config and isinstance(safe_config['nord_credentials'], dict):
            safe_config['nord_credentials'] = {
                'email': safe_config['nord_credentials'].get('email', ''),
                'password': '***'
            }
        if 'levante_credentials' in safe_config and isinstance(safe_config['levante_credentials'], dict):
            safe_config['levante_credentials'] = {
                'email': safe_config['levante_credentials'].get('email', ''),
                'password': '***'
            }

        return jsonify(safe_config)
    except Exception as e:
        logger.exception("Erro em /config GET")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@portfolio_bp.route("/last-update-time", methods=["GET"])
def get_last_update_time():
    """Retorna a data e hora da última atualização do portfólio."""
    try:
        updater = get_portfolio_updater()
        last_update_time = updater.config.get("last_update_timestamp", "N/A") if updater and getattr(updater, "config", None) else "N/A"
        return jsonify({
            "status": "success",
            "last_update_time": last_update_time
        })
    except Exception as e:
        logger.exception("Erro em /last-update-time")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@portfolio_bp.route("/config", methods=["POST"])
def update_config():
    """Atualiza a configuração do sistema (atenção à validação)."""
    try:
        data = request.get_json(silent=True) or {}
        updater = get_portfolio_updater()
        
        # Atualizar configuração (implementar validação conforme necessário)
        for key, value in data.items():
            if isinstance(updater.config, dict) and key in updater.config:
                updater.config[key] = value
        
        # TODO: persistir configuração se necessário (arquivo / DB)
        return jsonify({
            "status": "success",
            "message": "Configuração atualizada com sucesso"
        })
    except Exception as e:
        logger.exception("Erro em /config POST")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@portfolio_bp.route('/update', methods=['POST'])
def run_update():
    """Executa uma atualização manual do portfólio."""
    try:
        updater = get_portfolio_updater()
        success = False
        if hasattr(updater, "run_update"):
            success = updater.run_update()
        else:
            raise RuntimeError("Updater não implementa run_update()")
        
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
        logger.exception("Erro em /update")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@portfolio_bp.route('/portfolio', methods=['GET'])
def get_portfolio():
    """Retorna os dados atuais do portfólio (JSON seguro)."""
    try:
        updater = get_portfolio_updater()
        if updater is None:
            raise RuntimeError("PortfolioUpdater não inicializado.")

        excel_path = updater.config.get('excel_file_path')
        sheet_name = updater.config.get('excel_positions_sheet_name')

        if excel_path is None:
            raise RuntimeError("excel_file_path não configurado no updater.config")

        if ExcelProcessor is None:
            raise RuntimeError("ExcelProcessor não disponível (import falhou)")

        excel_processor = ExcelProcessor(excel_path)
        
        # Ler dados do portfólio
        positions_df = excel_processor.read_sheet(sheet_name)
        debug_df(positions_df, name="positions_df")
        
        if positions_df is None or positions_df.empty:
            return jsonify({
                'status': 'success',
                'data': [],
                'message': 'Nenhuma posição encontrada'
            })

        # Converter DataFrame para lista de dicionários seguros para JSON
        portfolio_data = df_to_safe_records(positions_df)
        
        return jsonify({
            "status": "success",
            "data": portfolio_data,
            "total_positions": len(portfolio_data)
        })
    except Exception as e:
        logger.exception("Erro em /portfolio")
        return jsonify({
            "status": "error",
            "message": f"Erro ao obter dados do portfólio: {str(e)}"
        }), 500


@portfolio_bp.route("/test-excel", methods=["GET"])
def test_excel_connection():
    """Testa a leitura da planilha Excel configurada (retorna preview seguro)."""
    try:
        updater = get_portfolio_updater()
        excel_path = updater.config.get("excel_file_path")
        sheet_name = updater.config.get("excel_positions_sheet_name")
        
        if excel_path is None:
            return jsonify({"status": "error", "message": "excel_file_path não configurado"}), 500
        if ExcelProcessor is None:
            return jsonify({"status": "error", "message": "ExcelProcessor não disponível"}), 500

        excel_processor = ExcelProcessor(excel_path)
        df = excel_processor.read_sheet(sheet_name)
        debug_df(df, name="excel_preview_df")
        
        if df is None or df.empty:
            return jsonify({
                "status": "error",
                "message": f"A planilha '{sheet_name}' está vazia ou não pôde ser lida. Verifique o caminho e o nome da planilha."
            }), 400

        preview_safe = df_to_safe_records(df.head())
        return jsonify({
            "status": "success",
            "message": f"Planilha '{sheet_name}' lida com sucesso!",
            "preview": preview_safe,  # JSON seguro
            "columns": df.columns.tolist()
        })
    except Exception as e:
        logger.exception("Erro em /test-excel")
        return jsonify({
            "status": "error",
            "message": f"Erro ao testar a planilha Excel: {str(e)}"
        }), 500

@portfolio_bp.route("/test-nord", methods=["POST"])
def test_nord_connection():
    """Testa a conexão com Nord Research."""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'status': 'error',
                'message': 'Email e senha são obrigatórios'
            }), 400
        
        if BrowserOrchestrator is None:
            return jsonify({'status': 'error', 'message': 'BrowserOrchestrator não disponível'}), 500

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
        logger.exception("Erro em /test-nord")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@portfolio_bp.route('/test-levante', methods=['POST'])
def test_levante_connection():
    """Testa a conexão com Levante Ideias."""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'status': 'error',
                'message': 'Email e senha são obrigatórios'
            }), 400
        
        if BrowserOrchestrator is None:
            return jsonify({'status': 'error', 'message': 'BrowserOrchestrator não disponível'}), 500

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
        logger.exception("Erro em /test-levante")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
