# portfolio_web_interface/src/routes/portfolio.py
import os
import sys
import logging
import json
from datetime import datetime

import numpy as np
import pandas as pd
from flask import Blueprint, request, jsonify

# logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adicionar o diretório 'src' do projeto ao path para permitir imports relativos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

# Função de serialização segura para JSON (corrigida)
def df_to_safe_records(df):
    """
    Converte DataFrame para lista de dicionários JSON-safe.
    Substitui NaN, NaT e outros valores problemáticos por None.
    """
    if df is None or df.empty:
        return []
    
    try:
        # Substitui NaN, NaT, inf, -inf por None
        df_clean = df.replace({
            np.nan: None,
            pd.NaT: None,
            np.inf: None,
            -np.inf: None
        })
        
        # Converte para dicionários
        records = df_clean.to_dict(orient="records")
        
        # Limpeza adicional para garantir compatibilidade JSON
        clean_records = []
        for record in records:
            clean_record = {}
            for key, value in record.items():
                # Verifica se o valor é JSON serializável
                if pd.isna(value) or value is pd.NaT or value is np.nan:
                    clean_record[key] = None
                elif isinstance(value, (np.integer, np.floating)):
                    if np.isnan(value) or np.isinf(value):
                        clean_record[key] = None
                    else:
                        clean_record[key] = float(value) if isinstance(value, np.floating) else int(value)
                elif isinstance(value, np.bool_):
                    clean_record[key] = bool(value)
                elif isinstance(value, (pd.Timestamp, np.datetime64)):
                    try:
                        clean_record[key] = value.isoformat() if pd.notna(value) else None
                    except:
                        clean_record[key] = str(value) if pd.notna(value) else None
                else:
                    clean_record[key] = value
            clean_records.append(clean_record)
        
        return clean_records
        
    except Exception as e:
        logger.error(f"Erro na conversão df_to_safe_records: {e}")
        # Fallback mais simples
        try:
            return df.where(pd.notnull(df), None).to_dict(orient="records")
        except:
            return []

# Importar util de serialização seguro (com fallback)
try:
    from src.utils.serialize import df_to_safe_records as imported_df_to_safe_records
    # Se a importação funcionar, usar a função importada
    df_to_safe_records = imported_df_to_safe_records
    logger.info("Usando df_to_safe_records importada de src.utils.serialize")
except Exception:
    try:
        from utils.serialize import df_to_safe_records as imported_df_to_safe_records
        df_to_safe_records = imported_df_to_safe_records
        logger.info("Usando df_to_safe_records importada de utils.serialize")
    except Exception:
        logger.warning("Usando df_to_safe_records fallback local")

# Importar classes do package src (com fallback melhorado)
PortfolioUpdater = None
ExcelProcessor = None
BrowserOrchestrator = None

# Tentar importar PortfolioUpdater
try:
    from update_portfolio import PortfolioUpdater
    logger.info("PortfolioUpdater importado com sucesso")
except Exception as e:
    try:
        from src.update_portfolio import PortfolioUpdater
        logger.info("PortfolioUpdater importado de src com sucesso")
    except Exception as e2:
        logger.warning(f"Não foi possível importar PortfolioUpdater: {e}, {e2}")

# Tentar importar ExcelProcessor
try:
    from excel_processor import ExcelProcessor
    logger.info("ExcelProcessor importado com sucesso")
except Exception as e:
    try:
        from src.excel_processor import ExcelProcessor
        logger.info("ExcelProcessor importado de src com sucesso")
    except Exception as e2:
        logger.warning(f"Não foi possível importar ExcelProcessor: {e}, {e2}")

# Tentar importar BrowserOrchestrator
try:
    from browser_orchestrator import BrowserOrchestrator
    logger.info("BrowserOrchestrator importado com sucesso")
except Exception as e:
    try:
        from src.browser_orchestrator import BrowserOrchestrator
        logger.info("BrowserOrchestrator importado de src com sucesso")
    except Exception as e2:
        logger.warning(f"Não foi possível importar BrowserOrchestrator: {e}, {e2}")

# Blueprint
portfolio_bp = Blueprint('portfolio', __name__)

# Instância global do atualizador de portfólio
portfolio_updater = None

def get_portfolio_updater():
    """Obtém ou cria instância do PortfolioUpdater com tratamento de erro melhorado."""
    global portfolio_updater
    if portfolio_updater is None:
        if PortfolioUpdater is None:
            raise RuntimeError("PortfolioUpdater não está disponível. Verifique se o módulo update_portfolio está no path correto.")
        try:
            portfolio_updater = PortfolioUpdater()
            logger.info("PortfolioUpdater inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar PortfolioUpdater: {e}")
            raise RuntimeError(f"Falha ao inicializar PortfolioUpdater: {e}")
    return portfolio_updater

def debug_df(df, name="df"):
    """Log detalhado para debug de DataFrames."""
    try:
        if df is None:
            logger.info(f"[DEBUG] {name} is None")
            return
        
        logger.info(f"[DEBUG] {name} shape={df.shape}")
        
        if df.empty:
            logger.info(f"[DEBUG] {name} está vazio")
            return
            
        try:
            logger.info(f"[DEBUG] {name} dtypes:\n{df.dtypes}")
        except Exception as e:
            logger.info(f"[DEBUG] {name} dtypes unavailable: {e}")
            
        try:
            nulls = df.isnull().sum()
            nulls = nulls[nulls > 0]
            if not nulls.empty:
                logger.info(f"[DEBUG] {name} null counts: {nulls.to_dict()}")
            else:
                logger.info(f"[DEBUG] {name} não possui valores nulos")
        except Exception as e:
            logger.info(f"[DEBUG] {name} null check failed: {e}")
            
        try:
            logger.info(f"[DEBUG] {name} colunas: {list(df.columns)}")
        except Exception as e:
            logger.info(f"[DEBUG] {name} columns check failed: {e}")
            
    except Exception as e:
        logger.info(f"[DEBUG] debug_df error: {e}")

# Rotas
@portfolio_bp.route('/status', methods=['GET'])
def get_status():
    """Retorna o status atual do sistema."""
    try:
        # Verificar se os módulos essenciais estão disponíveis
        modules_status = {
            'PortfolioUpdater': PortfolioUpdater is not None,
            'ExcelProcessor': ExcelProcessor is not None,
            'BrowserOrchestrator': BrowserOrchestrator is not None
        }
        
        return jsonify({
            'status': 'running',
            'message': 'Sistema de atualização de portfólio operacional',
            'timestamp': datetime.now().isoformat(),
            'modules': modules_status
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
        
        # Mascarar credenciais sensíveis
        sensitive_keys = ['nord_credentials', 'levante_credentials', 'password', 'senha']
        for key in sensitive_keys:
            if key in safe_config and isinstance(safe_config[key], dict):
                if 'password' in safe_config[key]:
                    safe_config[key]['password'] = '***'
                if 'senha' in safe_config[key]:
                    safe_config[key]['senha'] = '***'
            elif key in safe_config and isinstance(safe_config[key], str):
                safe_config[key] = '***'

        return jsonify({
            'status': 'success',
            'config': safe_config
        })
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
        config = getattr(updater, "config", {}) or {}
        last_update_time = config.get("last_update_timestamp", "N/A")
        
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
    """Atualiza a configuração do sistema com validação."""
    try:
        data = request.get_json(silent=True) or {}
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Nenhum dado fornecido para atualização"
            }), 400
            
        updater = get_portfolio_updater()
        
        # Validar e atualizar configuração
        updated_keys = []
        for key, value in data.items():
            if hasattr(updater, 'config') and isinstance(updater.config, dict):
                updater.config[key] = value
                updated_keys.append(key)
        
        return jsonify({
            "status": "success",
            "message": f"Configuração atualizada com sucesso. Chaves atualizadas: {updated_keys}"
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
        
        if not hasattr(updater, "run_update"):
            raise RuntimeError("Updater não implementa o método run_update()")
        
        logger.info("Iniciando atualização manual do portfólio...")
        success = updater.run_update()
        
        if success:
            logger.info("Atualização do portfólio concluída com sucesso")
            return jsonify({
                'status': 'success',
                'message': 'Atualização do portfólio executada com sucesso',
                'timestamp': datetime.now().isoformat()
            })
        else:
            logger.warning("Atualização do portfólio falhou")
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
        
        # Verificar configuração
        config = getattr(updater, "config", {}) or {}
        excel_path = config.get('excel_file_path')
        sheet_name = config.get('excel_positions_sheet_name')

        if not excel_path:
            raise RuntimeError("excel_file_path não configurado. Verifique a configuração.")
        
        if not sheet_name:
            raise RuntimeError("excel_positions_sheet_name não configurado. Verifique a configuração.")

        if ExcelProcessor is None:
            raise RuntimeError("ExcelProcessor não disponível. Verifique se o módulo excel_processor está no path correto.")

        # Verificar se o arquivo existe
        if not os.path.exists(excel_path):
            raise RuntimeError(f"Arquivo Excel não encontrado: {excel_path}")

        excel_processor = ExcelProcessor(excel_path)
        
        # Ler dados do portfólio
        logger.info(f"Lendo planilha: {excel_path}, aba: {sheet_name}")
        positions_df = excel_processor.read_sheet(sheet_name)
        debug_df(positions_df, name="positions_df")
        
        if positions_df is None or positions_df.empty:
            logger.warning("Nenhuma posição encontrada na planilha")
            return jsonify({
                'status': 'success',
                'data': [],
                'message': 'Nenhuma posição encontrada',
                'total_positions': 0
            })

        # Converter DataFrame para lista de dicionários seguros para JSON
        logger.info("Convertendo dados para formato JSON seguro...")
        portfolio_data = df_to_safe_records(positions_df)
        
        logger.info(f"Dados do portfólio carregados com sucesso: {len(portfolio_data)} posições")
        
        return jsonify({
            "status": "success",
            "data": portfolio_data,
            "total_positions": len(portfolio_data),
            "timestamp": datetime.now().isoformat()
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
        config = getattr(updater, "config", {}) or {}
        excel_path = config.get("excel_file_path")
        sheet_name = config.get("excel_positions_sheet_name")
        
        if not excel_path:
            return jsonify({
                "status": "error", 
                "message": "excel_file_path não configurado"
            }), 400
            
        if not sheet_name:
            return jsonify({
                "status": "error", 
                "message": "excel_positions_sheet_name não configurado"
            }), 400
            
        if ExcelProcessor is None:
            return jsonify({
                "status": "error", 
                "message": "ExcelProcessor não disponível"
            }), 500

        # Verificar se o arquivo existe
        if not os.path.exists(excel_path):
            return jsonify({
                "status": "error",
                "message": f"Arquivo Excel não encontrado: {excel_path}"
            }), 400

        excel_processor = ExcelProcessor(excel_path)
        df = excel_processor.read_sheet(sheet_name)
        debug_df(df, name="excel_preview_df")
        
        if df is None or df.empty:
            return jsonify({
                "status": "error",
                "message": f"A planilha '{sheet_name}' está vazia ou não pôde ser lida. Verifique o nome da aba."
            }), 400

        # Converter preview para formato seguro
        preview_safe = df_to_safe_records(df.head(10))  # Mostrar até 10 linhas
        
        return jsonify({
            "status": "success",
            "message": f"Planilha '{sheet_name}' lida com sucesso!",
            "preview": preview_safe,
            "columns": df.columns.tolist(),
            "total_rows": len(df),
            "file_path": excel_path
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
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({
                'status': 'error',
                'message': 'Email e senha são obrigatórios'
            }), 400
        
        if BrowserOrchestrator is None:
            return jsonify({
                'status': 'error', 
                'message': 'BrowserOrchestrator não disponível'
            }), 500

        logger.info("Testando conexão com Nord Research...")
        browser = BrowserOrchestrator(headless=True)
        success = False
        error_message = ""
        
        try:
            if browser.setup_driver():
                success = browser.login_nord(email, password)
                if not success:
                    error_message = "Falha no login - verifique as credenciais"
            else:
                error_message = "Falha ao configurar o navegador"
        except Exception as e:
            error_message = f"Erro durante o teste: {str(e)}"
        finally:
            try:
                browser.close_driver()
            except:
                pass
        
        return jsonify({
            'status': 'success' if success else 'error',
            'message': 'Conexão com Nord Research bem-sucedida' if success else f'Falha na conexão com Nord Research: {error_message}'
        })
        
    except Exception as e:
        logger.exception("Erro em /test-nord")
        return jsonify({
            'status': 'error',
            'message': f"Erro no teste de conexão Nord: {str(e)}"
        }), 500

@portfolio_bp.route('/test-levante', methods=['POST'])
def test_levante_connection():
    """Testa a conexão com Levante Ideias."""
    try:
        data = request.get_json() or {}
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({
                'status': 'error',
                'message': 'Email e senha são obrigatórios'
            }), 400
        
        if BrowserOrchestrator is None:
            return jsonify({
                'status': 'error', 
                'message': 'BrowserOrchestrator não disponível'
            }), 500

        logger.info("Testando conexão com Levante Ideias...")
        browser = BrowserOrchestrator(headless=True)
        success = False
        error_message = ""
        
        try:
            if browser.setup_driver():
                success = browser.login_levante(email, password)
                if not success:
                    error_message = "Falha no login - verifique as credenciais"
            else:
                error_message = "Falha ao configurar o navegador"
        except Exception as e:
            error_message = f"Erro durante o teste: {str(e)}"
        finally:
            try:
                browser.close_driver()
            except:
                pass
        
        return jsonify({
            'status': 'success' if success else 'error',
            'message': 'Conexão com Levante Ideias bem-sucedida' if success else f'Falha na conexão com Levante Ideias: {error_message}'
        })
        
    except Exception as e:
        logger.exception("Erro em /test-levante")
        return jsonify({
            'status': 'error',
            'message': f"Erro no teste de conexão Levante: {str(e)}"
        }), 500
