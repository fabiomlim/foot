#!/usr/bin/env python3
"""
Sistema de visualização das predições e value bets
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from datetime import datetime
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')

# Configurar matplotlib para português
plt.rcParams['font.size'] = 10
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

class PredictionVisualizer:
    """Classe para visualização de predições"""
    
    def __init__(self, predictions_file: str = "predictions_history.json"):
        self.predictions_file = predictions_file
        self.predictions_data = self._load_predictions()
        
    def _load_predictions(self) -> List[Dict]:
        """Carrega dados de predições"""
        try:
            with open(self.predictions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Arquivo não encontrado: {self.predictions_file}")
            return []
        except Exception as e:
            print(f"❌ Erro ao carregar predições: {e}")
            return []
    
    def create_predictions_dashboard(self):
        """Cria dashboard completo das predições"""
        
        if not self.predictions_data:
            print("❌ Nenhum dado de predição disponível")
            return
        
        print("📊 Criando dashboard de predições...")
        
        # Configurar figura com subplots
        fig = plt.figure(figsize=(20, 16))
        fig.suptitle('🔮 DASHBOARD DE PREDIÇÕES DE FUTEBOL', fontsize=20, fontweight='bold', y=0.98)
        
        # 1. Probabilidades por partida
        ax1 = plt.subplot(3, 3, 1)
        self._plot_match_probabilities(ax1)
        
        # 2. Distribuição de confiança
        ax2 = plt.subplot(3, 3, 2)
        self._plot_confidence_distribution(ax2)
        
        # 3. Value bets por partida
        ax3 = plt.subplot(3, 3, 3)
        self._plot_value_bets_summary(ax3)
        
        # 4. Predições de gols
        ax4 = plt.subplot(3, 3, 4)
        self._plot_goals_predictions(ax4)
        
        # 5. Mercados mais lucrativos
        ax5 = plt.subplot(3, 3, 5)
        self._plot_market_profitability(ax5)
        
        # 6. Timeline de confiança
        ax6 = plt.subplot(3, 3, 6)
        self._plot_confidence_timeline(ax6)
        
        # 7. Heatmap de probabilidades
        ax7 = plt.subplot(3, 3, 7)
        self._plot_probability_heatmap(ax7)
        
        # 8. Value distribution
        ax8 = plt.subplot(3, 3, 8)
        self._plot_value_distribution(ax8)
        
        # 9. Resumo estatístico
        ax9 = plt.subplot(3, 3, 9)
        self._plot_statistics_summary(ax9)
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.95)
        
        # Salvar dashboard
        plt.savefig('predictions_dashboard.png', dpi=300, bbox_inches='tight')
        print("💾 Dashboard salvo: predictions_dashboard.png")
        
        plt.show()
    
    def _plot_match_probabilities(self, ax):
        """Gráfico de probabilidades por partida"""
        
        matches = []
        home_probs = []
        draw_probs = []
        away_probs = []
        
        for pred in self.predictions_data:
            match_name = f"{pred['home_team']} vs {pred['away_team']}"
            matches.append(match_name)
            home_probs.append(pred['home_win_prob'] * 100)
            draw_probs.append(pred['draw_prob'] * 100)
            away_probs.append(pred['away_win_prob'] * 100)
        
        x = np.arange(len(matches))
        width = 0.25
        
        ax.bar(x - width, home_probs, width, label='Casa', color='#2E8B57', alpha=0.8)
        ax.bar(x, draw_probs, width, label='Empate', color='#FFD700', alpha=0.8)
        ax.bar(x + width, away_probs, width, label='Fora', color='#DC143C', alpha=0.8)
        
        ax.set_xlabel('Partidas')
        ax.set_ylabel('Probabilidade (%)')
        ax.set_title('🎯 Probabilidades 1X2 por Partida')
        ax.set_xticks(x)
        ax.set_xticklabels(matches, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_confidence_distribution(self, ax):
        """Distribuição de confiança das predições"""
        
        confidences = [pred['confidence_score'] * 100 for pred in self.predictions_data]
        
        ax.hist(confidences, bins=10, color='#4169E1', alpha=0.7, edgecolor='black')
        ax.axvline(np.mean(confidences), color='red', linestyle='--', 
                  label=f'Média: {np.mean(confidences):.1f}%')
        
        ax.set_xlabel('Confiança (%)')
        ax.set_ylabel('Frequência')
        ax.set_title('📊 Distribuição de Confiança')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_value_bets_summary(self, ax):
        """Resumo de value bets"""
        
        total_bets = 0
        strong_bets = 0
        regular_bets = 0
        consider_bets = 0
        
        for pred in self.predictions_data:
            for bet in pred['value_bets']:
                total_bets += 1
                if bet['recommendation'] == 'STRONG_BET':
                    strong_bets += 1
                elif bet['recommendation'] == 'BET':
                    regular_bets += 1
                elif bet['recommendation'] == 'CONSIDER':
                    consider_bets += 1
        
        categories = ['STRONG_BET', 'BET', 'CONSIDER', 'AVOID']
        counts = [strong_bets, regular_bets, consider_bets, 
                 max(0, total_bets - strong_bets - regular_bets - consider_bets)]
        colors = ['#FF4500', '#32CD32', '#FFD700', '#808080']
        
        wedges, texts, autotexts = ax.pie(counts, labels=categories, colors=colors, 
                                         autopct='%1.1f%%', startangle=90)
        
        ax.set_title('💰 Distribuição de Value Bets')
    
    def _plot_goals_predictions(self, ax):
        """Predições de gols"""
        
        matches = []
        home_goals = []
        away_goals = []
        total_goals = []
        
        for pred in self.predictions_data:
            match_name = f"{pred['home_team'][:3]} vs {pred['away_team'][:3]}"
            matches.append(match_name)
            home_goals.append(pred['expected_home_goals'])
            away_goals.append(pred['expected_away_goals'])
            total_goals.append(pred['expected_total_goals'])
        
        x = np.arange(len(matches))
        width = 0.25
        
        ax.bar(x - width, home_goals, width, label='Gols Casa', color='#2E8B57', alpha=0.8)
        ax.bar(x, away_goals, width, label='Gols Fora', color='#DC143C', alpha=0.8)
        ax.plot(x, total_goals, 'o-', color='#4169E1', linewidth=2, 
               markersize=6, label='Total Esperado')
        
        ax.set_xlabel('Partidas')
        ax.set_ylabel('Gols Esperados')
        ax.set_title('⚽ Predições de Gols')
        ax.set_xticks(x)
        ax.set_xticklabels(matches, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_market_profitability(self, ax):
        """Mercados mais lucrativos"""
        
        market_values = {}
        
        for pred in self.predictions_data:
            for bet in pred['value_bets']:
                market = bet['market']
                value = bet['value']
                
                if market not in market_values:
                    market_values[market] = []
                market_values[market].append(value * 100)
        
        if market_values:
            markets = list(market_values.keys())
            avg_values = [np.mean(values) for values in market_values.values()]
            
            bars = ax.bar(markets, avg_values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
            
            # Adicionar valores nas barras
            for bar, value in zip(bars, avg_values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{value:.1f}%', ha='center', va='bottom')
            
            ax.set_xlabel('Mercados')
            ax.set_ylabel('Value Médio (%)')
            ax.set_title('📈 Mercados Mais Lucrativos')
            ax.tick_params(axis='x', rotation=45)
        else:
            ax.text(0.5, 0.5, 'Nenhum dado disponível', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12)
            ax.set_title('📈 Mercados Mais Lucrativos')
        
        ax.grid(True, alpha=0.3)
    
    def _plot_confidence_timeline(self, ax):
        """Timeline de confiança"""
        
        times = []
        confidences = []
        
        for pred in self.predictions_data:
            times.append(pred['elapsed_time'])
            confidences.append(pred['confidence_score'] * 100)
        
        if times and confidences:
            ax.scatter(times, confidences, c=confidences, cmap='RdYlGn', 
                      s=100, alpha=0.7, edgecolors='black')
            
            # Linha de tendência
            if len(times) > 1:
                z = np.polyfit(times, confidences, 1)
                p = np.poly1d(z)
                ax.plot(times, p(times), "r--", alpha=0.8, linewidth=2)
            
            ax.set_xlabel('Tempo Decorrido (min)')
            ax.set_ylabel('Confiança (%)')
            ax.set_title('⏱️ Evolução da Confiança')
            
            # Colorbar
            cbar = plt.colorbar(ax.collections[0], ax=ax)
            cbar.set_label('Confiança (%)')
        else:
            ax.text(0.5, 0.5, 'Nenhum dado disponível', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12)
            ax.set_title('⏱️ Evolução da Confiança')
        
        ax.grid(True, alpha=0.3)
    
    def _plot_probability_heatmap(self, ax):
        """Heatmap de probabilidades"""
        
        if len(self.predictions_data) < 2:
            ax.text(0.5, 0.5, 'Dados insuficientes\npara heatmap', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_title('🔥 Heatmap de Probabilidades')
            return
        
        # Criar matriz de probabilidades
        prob_data = []
        match_names = []
        
        for pred in self.predictions_data:
            match_name = f"{pred['home_team'][:8]} vs {pred['away_team'][:8]}"
            match_names.append(match_name)
            
            prob_data.append([
                pred['home_win_prob'] * 100,
                pred['draw_prob'] * 100,
                pred['away_win_prob'] * 100,
                pred['over_2_5_prob'] * 100,
                pred['btts_prob'] * 100
            ])
        
        prob_df = pd.DataFrame(prob_data, 
                              columns=['Casa', 'Empate', 'Fora', 'Over 2.5', 'BTTS'],
                              index=match_names)
        
        sns.heatmap(prob_df, annot=True, fmt='.1f', cmap='RdYlGn', 
                   ax=ax, cbar_kws={'label': 'Probabilidade (%)'})
        
        ax.set_title('🔥 Heatmap de Probabilidades')
        ax.set_xlabel('Mercados')
        ax.set_ylabel('Partidas')
    
    def _plot_value_distribution(self, ax):
        """Distribuição de values"""
        
        all_values = []
        
        for pred in self.predictions_data:
            for bet in pred['value_bets']:
                all_values.append(bet['value'] * 100)
        
        if all_values:
            ax.hist(all_values, bins=15, color='#32CD32', alpha=0.7, edgecolor='black')
            ax.axvline(np.mean(all_values), color='red', linestyle='--', 
                      label=f'Média: {np.mean(all_values):.1f}%')
            ax.axvline(15, color='orange', linestyle=':', 
                      label='Threshold (15%)')
            
            ax.set_xlabel('Value (%)')
            ax.set_ylabel('Frequência')
            ax.set_title('💎 Distribuição de Values')
            ax.legend()
        else:
            ax.text(0.5, 0.5, 'Nenhum value bet\nencontrado', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_title('💎 Distribuição de Values')
        
        ax.grid(True, alpha=0.3)
    
    def _plot_statistics_summary(self, ax):
        """Resumo estatístico"""
        
        # Calcular estatísticas
        total_predictions = len(self.predictions_data)
        avg_confidence = np.mean([pred['confidence_score'] for pred in self.predictions_data]) * 100
        
        total_value_bets = sum(len(pred['value_bets']) for pred in self.predictions_data)
        
        if total_value_bets > 0:
            all_values = []
            for pred in self.predictions_data:
                for bet in pred['value_bets']:
                    all_values.append(bet['value'] * 100)
            avg_value = np.mean(all_values)
            max_value = np.max(all_values)
        else:
            avg_value = 0
            max_value = 0
        
        # Criar texto de estatísticas
        stats_text = f"""
📊 ESTATÍSTICAS GERAIS

🔮 Total de Predições: {total_predictions}
📈 Confiança Média: {avg_confidence:.1f}%
💰 Total Value Bets: {total_value_bets}
💎 Value Médio: {avg_value:.1f}%
🚀 Maior Value: {max_value:.1f}%

⏰ Última Atualização:
{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        """
        
        ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=11,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.set_title('📋 Resumo Estatístico')
    
    def create_value_bets_report(self):
        """Cria relatório detalhado de value bets"""
        
        print("💰 Criando relatório de value bets...")
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('💰 RELATÓRIO DETALHADO DE VALUE BETS', fontsize=16, fontweight='bold')
        
        # 1. Value bets por partida
        self._plot_value_bets_by_match(ax1)
        
        # 2. ROI simulado por mercado
        self._plot_simulated_roi(ax2)
        
        # 3. Kelly fractions
        self._plot_kelly_fractions(ax3)
        
        # 4. Recomendações por categoria
        self._plot_recommendations_breakdown(ax4)
        
        plt.tight_layout()
        plt.savefig('value_bets_report.png', dpi=300, bbox_inches='tight')
        print("💾 Relatório salvo: value_bets_report.png")
        
        plt.show()
    
    def _plot_value_bets_by_match(self, ax):
        """Value bets por partida"""
        
        matches = []
        max_values = []
        bet_counts = []
        
        for pred in self.predictions_data:
            match_name = f"{pred['home_team'][:8]} vs {pred['away_team'][:8]}"
            matches.append(match_name)
            
            if pred['value_bets']:
                max_value = max(bet['value'] for bet in pred['value_bets']) * 100
                bet_count = len(pred['value_bets'])
            else:
                max_value = 0
                bet_count = 0
            
            max_values.append(max_value)
            bet_counts.append(bet_count)
        
        x = np.arange(len(matches))
        
        # Barras com cores baseadas no value
        colors = ['#FF4500' if v > 30 else '#32CD32' if v > 15 else '#FFD700' if v > 5 else '#808080' 
                 for v in max_values]
        
        bars = ax.bar(x, max_values, color=colors, alpha=0.8, edgecolor='black')
        
        # Adicionar número de bets em cada barra
        for i, (bar, count) in enumerate(zip(bars, bet_counts)):
            if count > 0:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{count}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_xlabel('Partidas')
        ax.set_ylabel('Maior Value (%)')
        ax.set_title('🎯 Value Bets por Partida')
        ax.set_xticks(x)
        ax.set_xticklabels(matches, rotation=45, ha='right')
        ax.grid(True, alpha=0.3)
        
        # Legenda de cores
        legend_elements = [
            plt.Rectangle((0,0),1,1, facecolor='#FF4500', label='> 30% (Excelente)'),
            plt.Rectangle((0,0),1,1, facecolor='#32CD32', label='15-30% (Bom)'),
            plt.Rectangle((0,0),1,1, facecolor='#FFD700', label='5-15% (Moderado)'),
            plt.Rectangle((0,0),1,1, facecolor='#808080', label='< 5% (Baixo)')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
    
    def _plot_simulated_roi(self, ax):
        """ROI simulado por mercado"""
        
        market_roi = {}
        
        for pred in self.predictions_data:
            for bet in pred['value_bets']:
                market = bet['market']
                value = bet['value']
                
                # Simular ROI baseado no value
                simulated_roi = value * 0.8  # Assumir 80% de eficiência
                
                if market not in market_roi:
                    market_roi[market] = []
                market_roi[market].append(simulated_roi * 100)
        
        if market_roi:
            markets = list(market_roi.keys())
            avg_rois = [np.mean(rois) for rois in market_roi.values()]
            
            bars = ax.bar(markets, avg_rois, 
                         color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'][:len(markets)])
            
            # Adicionar valores
            for bar, roi in zip(bars, avg_rois):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{roi:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            ax.set_xlabel('Mercados')
            ax.set_ylabel('ROI Simulado (%)')
            ax.set_title('📈 ROI Simulado por Mercado')
            ax.tick_params(axis='x', rotation=45)
            
            # Linha de break-even
            ax.axhline(y=0, color='red', linestyle='--', alpha=0.7, label='Break-even')
            ax.legend()
        else:
            ax.text(0.5, 0.5, 'Nenhum dado disponível', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12)
            ax.set_title('📈 ROI Simulado por Mercado')
        
        ax.grid(True, alpha=0.3)
    
    def _plot_kelly_fractions(self, ax):
        """Distribuição de Kelly fractions"""
        
        kelly_fractions = []
        
        for pred in self.predictions_data:
            for bet in pred['value_bets']:
                kelly_fractions.append(bet['kelly_fraction'] * 100)
        
        if kelly_fractions:
            ax.hist(kelly_fractions, bins=10, color='#4169E1', alpha=0.7, edgecolor='black')
            ax.axvline(np.mean(kelly_fractions), color='red', linestyle='--', 
                      label=f'Média: {np.mean(kelly_fractions):.1f}%')
            ax.axvline(5, color='orange', linestyle=':', 
                      label='Conservador (5%)')
            
            ax.set_xlabel('Kelly Fraction (%)')
            ax.set_ylabel('Frequência')
            ax.set_title('🎲 Distribuição de Kelly Fractions')
            ax.legend()
        else:
            ax.text(0.5, 0.5, 'Nenhum dado disponível', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12)
            ax.set_title('🎲 Distribuição de Kelly Fractions')
        
        ax.grid(True, alpha=0.3)
    
    def _plot_recommendations_breakdown(self, ax):
        """Breakdown de recomendações"""
        
        recommendations = {'STRONG_BET': 0, 'BET': 0, 'CONSIDER': 0, 'AVOID': 0}
        
        for pred in self.predictions_data:
            for bet in pred['value_bets']:
                rec = bet['recommendation']
                if rec in recommendations:
                    recommendations[rec] += 1
        
        labels = list(recommendations.keys())
        sizes = list(recommendations.values())
        colors = ['#FF4500', '#32CD32', '#FFD700', '#808080']
        explode = (0.1, 0.05, 0, 0)  # Destacar STRONG_BET
        
        if sum(sizes) > 0:
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, 
                                             autopct='%1.1f%%', startangle=90, explode=explode)
            
            # Melhorar aparência do texto
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        else:
            ax.text(0.5, 0.5, 'Nenhuma\nrecomendação', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12)
        
        ax.set_title('🏆 Breakdown de Recomendações')
    
    def generate_text_report(self) -> str:
        """Gera relatório textual detalhado"""
        
        if not self.predictions_data:
            return "Nenhum dado de predição disponível."
        
        report = "# RELATÓRIO DE PREDIÇÕES E VALUE BETS\n\n"
        report += f"**Data do Relatório:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
        
        # Estatísticas gerais
        total_predictions = len(self.predictions_data)
        avg_confidence = np.mean([pred['confidence_score'] for pred in self.predictions_data]) * 100
        total_value_bets = sum(len(pred['value_bets']) for pred in self.predictions_data)
        
        report += "## 📊 ESTATÍSTICAS GERAIS\n\n"
        report += f"- **Total de Predições:** {total_predictions}\n"
        report += f"- **Confiança Média:** {avg_confidence:.1f}%\n"
        report += f"- **Total de Value Bets:** {total_value_bets}\n\n"
        
        # Detalhes por partida
        report += "## ⚽ DETALHES POR PARTIDA\n\n"
        
        for i, pred in enumerate(self.predictions_data, 1):
            report += f"### {i}. {pred['home_team']} vs {pred['away_team']}\n\n"
            report += f"- **Tempo:** {pred['elapsed_time']}'\n"
            report += f"- **Placar:** {pred['current_score'][0]}-{pred['current_score'][1]}\n"
            report += f"- **Confiança:** {pred['confidence_score']*100:.1f}%\n\n"
            
            report += "**Probabilidades:**\n"
            report += f"- Casa: {pred['home_win_prob']*100:.1f}%\n"
            report += f"- Empate: {pred['draw_prob']*100:.1f}%\n"
            report += f"- Fora: {pred['away_win_prob']*100:.1f}%\n"
            report += f"- Over 2.5: {pred['over_2_5_prob']*100:.1f}%\n"
            report += f"- BTTS: {pred['btts_prob']*100:.1f}%\n\n"
            
            report += "**Predições de Gols:**\n"
            report += f"- Total Esperado: {pred['expected_total_goals']:.2f}\n"
            report += f"- Casa: {pred['expected_home_goals']:.2f}\n"
            report += f"- Fora: {pred['expected_away_goals']:.2f}\n\n"
            
            if pred['value_bets']:
                report += "**Value Bets:**\n"
                for bet in pred['value_bets']:
                    report += f"- {bet['market']}: {bet['value']*100:.1f}% value ({bet['recommendation']})\n"
                    report += f"  - Odds: {bet['odds']:.2f}\n"
                    report += f"  - Kelly: {bet['kelly_fraction']*100:.1f}%\n"
            else:
                report += "**Value Bets:** Nenhum encontrado\n"
            
            report += "\n---\n\n"
        
        # Resumo de value bets
        if total_value_bets > 0:
            all_values = []
            market_summary = {}
            
            for pred in self.predictions_data:
                for bet in pred['value_bets']:
                    all_values.append(bet['value'] * 100)
                    market = bet['market']
                    if market not in market_summary:
                        market_summary[market] = {'count': 0, 'avg_value': 0, 'values': []}
                    market_summary[market]['count'] += 1
                    market_summary[market]['values'].append(bet['value'] * 100)
            
            # Calcular médias
            for market in market_summary:
                market_summary[market]['avg_value'] = np.mean(market_summary[market]['values'])
            
            report += "## 💰 RESUMO DE VALUE BETS\n\n"
            report += f"- **Value Médio:** {np.mean(all_values):.1f}%\n"
            report += f"- **Maior Value:** {np.max(all_values):.1f}%\n"
            report += f"- **Menor Value:** {np.min(all_values):.1f}%\n\n"
            
            report += "**Por Mercado:**\n"
            for market, data in sorted(market_summary.items(), key=lambda x: x[1]['avg_value'], reverse=True):
                report += f"- {market}: {data['count']} bets, {data['avg_value']:.1f}% value médio\n"
        
        return report

def demo_visualization():
    """Demonstração das visualizações"""
    print("📊 DEMONSTRAÇÃO DE VISUALIZAÇÕES DE PREDIÇÕES")
    print("=" * 70)
    
    # Inicializar visualizador
    visualizer = PredictionVisualizer()
    
    if not visualizer.predictions_data:
        print("❌ Nenhum dado de predição encontrado")
        print("💡 Execute primeiro o sistema de predição em tempo real")
        return
    
    print(f"📈 Dados carregados: {len(visualizer.predictions_data)} predições")
    
    # Criar dashboard principal
    visualizer.create_predictions_dashboard()
    
    # Criar relatório de value bets
    visualizer.create_value_bets_report()
    
    # Gerar relatório textual
    text_report = visualizer.generate_text_report()
    
    with open('predictions_text_report.md', 'w', encoding='utf-8') as f:
        f.write(text_report)
    
    print("💾 Relatório textual salvo: predictions_text_report.md")
    
    print(f"\n✅ Visualizações criadas:")
    print(f"   📊 predictions_dashboard.png")
    print(f"   💰 value_bets_report.png")
    print(f"   📄 predictions_text_report.md")
    
    return visualizer

if __name__ == "__main__":
    demo_visualization()

