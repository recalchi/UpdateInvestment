import pandas as pd
from typing import List, Dict, Any, Tuple
from datetime import datetime
import numpy as np

class PortfolioOptimizer:
    def __init__(self):
        self.optimization_rules = {
            'fiis': {
                'max_positions': 10,
                'min_monthly_return': 2.0,  # 2% ao mês
                'weight_adjustment_factor': 0.1
            },
            'acoes_dy': {
                'max_positions': 8,
                'min_dividend_yield': 5.0,  # 5% de dividend yield
                'weight_adjustment_factor': 0.15
            },
            'acoes_lp': {
                'max_positions': 6,
                'target_stocks': ['WEGE3'],  # WEG como especificado
                'weight_adjustment_factor': 0.2
            },
            'stocks_us': {
                'max_positions': 5,
                'target_stocks': ['CCJ'],  # CCJ como especificado
                'weight_adjustment_factor': 0.15
            },
            'cripto': {
                'max_positions': 5,
                'priority_coins': ['BTC', 'ETH', 'SOL'],  # Prioridade como especificado
                'altcoin_limit': 2,
                'weight_adjustment_factor': 0.25
            }
        }

    def analyze_portfolio_segment(self, current_positions: pd.DataFrame, 
                                market_data: pd.DataFrame, 
                                segment: str) -> Dict[str, Any]:
        """Analisa um segmento da carteira e sugere otimizações"""
        
        if segment not in self.optimization_rules:
            return {'recommendations': [], 'analysis': 'Segmento não reconhecido'}
        
        rules = self.optimization_rules[segment]
        recommendations = []
        
        if segment == 'fiis':
            recommendations = self._optimize_fiis(current_positions, market_data, rules)
        elif segment == 'acoes_dy':
            recommendations = self._optimize_dividend_stocks(current_positions, market_data, rules)
        elif segment == 'acoes_lp':
            recommendations = self._optimize_growth_stocks(current_positions, market_data, rules)
        elif segment == 'stocks_us':
            recommendations = self._optimize_us_stocks(current_positions, market_data, rules)
        elif segment == 'cripto':
            recommendations = self._optimize_crypto(current_positions, market_data, rules)
        
        return {
            'segment': segment,
            'recommendations': recommendations,
            'analysis': f'Análise completa para {segment}',
            'timestamp': datetime.now().isoformat()
        }

    def _optimize_fiis(self, positions: pd.DataFrame, market_data: pd.DataFrame, rules: Dict) -> List[Dict]:
        """Otimiza posições de FIIs"""
        recommendations = []
        
        # Verificar FIIs com baixa performance
        if 'RENTABILIDADE_ULT_MES' in positions.columns:
            underperforming = positions[positions['RENTABILIDADE_ULT_MES'] < rules['min_monthly_return']]
            
            for _, fii in underperforming.iterrows():
                # Procurar substitutos no market_data
                better_options = market_data[
                    (market_data['Rentabilidade_Ultimo_Mes'] > rules['min_monthly_return']) &
                    (~market_data['Ticker'].isin(positions['TICKER'].values))
                ].head(3)
                
                if not better_options.empty:
                    best_option = better_options.iloc[0]
                    recommendations.append({
                        'action': 'substitute',
                        'current_asset': fii['TICKER'],
                        'suggested_asset': best_option['Ticker'],
                        'reason': f'Baixa performance: {fii["RENTABILIDADE_ULT_MES"]:.2f}% vs {best_option["Rentabilidade_Ultimo_Mes"]:.2f}%',
                        'priority': 'high'
                    })
        
        return recommendations

    def _optimize_dividend_stocks(self, positions: pd.DataFrame, market_data: pd.DataFrame, rules: Dict) -> List[Dict]:
        """Otimiza ações de dividend yield"""
        recommendations = []
        
        # Verificar se há ações com baixo DY
        for _, stock in positions.iterrows():
            # Lógica para reduzir peso de ações com menor resultado acumulado
            if 'RENTABILIDADE_ULT_MES' in positions.columns:
                if stock['RENTABILIDADE_ULT_MES'] < 0:  # Ações com resultado negativo
                    new_weight = max(stock.get('PESO', 0) * (1 - rules['weight_adjustment_factor']), 0.01)
                    recommendations.append({
                        'action': 'reduce_weight',
                        'asset': stock['TICKER'],
                        'current_weight': stock.get('PESO', 0),
                        'suggested_weight': new_weight,
                        'reason': f'Resultado negativo no último mês: {stock["RENTABILIDADE_ULT_MES"]:.2f}%',
                        'priority': 'medium'
                    })
        
        return recommendations

    def _optimize_growth_stocks(self, positions: pd.DataFrame, market_data: pd.DataFrame, rules: Dict) -> List[Dict]:
        """Otimiza ações de crescimento (longo prazo)"""
        recommendations = []
        
        # Verificar se WEG está na carteira
        target_stocks = rules.get('target_stocks', [])
        current_tickers = positions['TICKER'].values if 'TICKER' in positions.columns else []
        
        for target in target_stocks:
            if target not in current_tickers:
                recommendations.append({
                    'action': 'add',
                    'suggested_asset': target,
                    'suggested_weight': 0.05,  # 5% inicial
                    'reason': f'Ação estratégica {target} não está na carteira',
                    'priority': 'high'
                })
        
        return recommendations

    def _optimize_us_stocks(self, positions: pd.DataFrame, market_data: pd.DataFrame, rules: Dict) -> List[Dict]:
        """Otimiza ações americanas"""
        recommendations = []
        
        # Verificar se CCJ está na carteira
        target_stocks = rules.get('target_stocks', [])
        current_tickers = positions['TICKER'].values if 'TICKER' in positions.columns else []
        
        for target in target_stocks:
            if target not in current_tickers:
                recommendations.append({
                    'action': 'add',
                    'suggested_asset': target,
                    'suggested_weight': 0.03,  # 3% inicial
                    'reason': f'Ação estratégica {target} (urânio) não está na carteira',
                    'priority': 'high'
                })
        
        return recommendations

    def _optimize_crypto(self, positions: pd.DataFrame, market_data: pd.DataFrame, rules: Dict) -> List[Dict]:
        """Otimiza posições de criptomoedas"""
        recommendations = []
        
        priority_coins = rules.get('priority_coins', [])
        current_cryptos = positions['TICKER'].values if 'TICKER' in positions.columns else []
        
        # Verificar se as criptos prioritárias estão na carteira
        for coin in priority_coins:
            if coin not in current_cryptos:
                recommendations.append({
                    'action': 'add',
                    'suggested_asset': coin,
                    'suggested_weight': 0.02 if coin in ['BTC', 'ETH'] else 0.01,
                    'reason': f'Criptomoeda prioritária {coin} não está na carteira',
                    'priority': 'high'
                })
        
        # Limitar altcoins minoritárias
        altcoin_count = len([c for c in current_cryptos if c not in priority_coins])
        if altcoin_count > rules['altcoin_limit']:
            recommendations.append({
                'action': 'reduce_altcoins',
                'current_count': altcoin_count,
                'target_count': rules['altcoin_limit'],
                'reason': f'Muitas altcoins na carteira ({altcoin_count}), reduzir para {rules["altcoin_limit"]}',
                'priority': 'medium'
            })
        
        return recommendations

    def calculate_new_weights(self, current_positions: pd.DataFrame, 
                            recommendations: List[Dict]) -> pd.DataFrame:
        """Calcula novos pesos baseado nas recomendações"""
        
        updated_positions = current_positions.copy()
        
        for rec in recommendations:
            if rec['action'] == 'reduce_weight':
                mask = updated_positions['TICKER'] == rec['asset']
                updated_positions.loc[mask, 'PESO'] = rec['suggested_weight']
            
            elif rec['action'] == 'add':
                new_row = {
                    'TICKER': rec['suggested_asset'],
                    'PESO': rec['suggested_weight'],
                    'DATA ATT': datetime.now().strftime('%Y-%m-%d'),
                    'OBS': f'Adicionado por otimização: {rec["reason"]}'
                }
                updated_positions = pd.concat([updated_positions, pd.DataFrame([new_row])], ignore_index=True)
        
        # Normalizar pesos para somar 100%
        total_weight = updated_positions['PESO'].sum()
        if total_weight > 0:
            updated_positions['PESO'] = updated_positions['PESO'] / total_weight
        
        return updated_positions

    def generate_optimization_report(self, all_recommendations: Dict[str, Any]) -> str:
        """Gera relatório de otimização"""
        
        report = f"""
# Relatório de Otimização de Carteira
**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

## Resumo das Recomendações

"""
        
        total_recommendations = 0
        high_priority = 0
        
        for segment, data in all_recommendations.items():
            recommendations = data.get('recommendations', [])
            total_recommendations += len(recommendations)
            high_priority += len([r for r in recommendations if r.get('priority') == 'high'])
            
            if recommendations:
                report += f"\n### {segment.upper()}\n"
                for rec in recommendations:
                    priority_icon = "🔴" if rec.get('priority') == 'high' else "🟡"
                    report += f"- {priority_icon} **{rec['action'].title()}**: {rec.get('reason', 'N/A')}\n"
        
        report += f"""
## Estatísticas
- **Total de recomendações:** {total_recommendations}
- **Alta prioridade:** {high_priority}
- **Média/Baixa prioridade:** {total_recommendations - high_priority}

## Próximos Passos
1. Revisar recomendações de alta prioridade
2. Implementar mudanças gradualmente
3. Monitorar performance após ajustes
"""
        
        return report

if __name__ == '__main__':
    # Teste do otimizador
    optimizer = PortfolioOptimizer()
    
    # Dados de exemplo
    positions = pd.DataFrame({
        'TICKER': ['HGLG11', 'XPML11', 'PETR4'],
        'PESO': [0.3, 0.3, 0.4],
        'RENTABILIDADE_ULT_MES': [1.5, 3.2, -2.1]
    })
    
    market_data = pd.DataFrame({
        'Ticker': ['VISC11', 'BCFF11'],
        'Rentabilidade_Ultimo_Mes': [4.5, 3.8]
    })
    
    recommendations = optimizer.analyze_portfolio_segment(positions, market_data, 'fiis')
    print("Recomendações para FIIs:")
    print(recommendations)

