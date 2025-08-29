#!/usr/bin/env python3
"""
Sistema simplificado de treinamento de modelos ML para futebol
"""

import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Imports para ML
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
import os

# XGBoost
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

class SimplifiedFootballMLTrainer:
    """Versão simplificada do trainer de ML para futebol"""
    
    def __init__(self, db_path: str = "football_data.db"):
        self.db_path = db_path
        self.models = {}
        self.scalers = {}
        self.performance_metrics = {}
        
    def create_basic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features básicas a partir dos dados das partidas"""
        
        print("🔧 Criando features básicas...")
        
        features_list = []
        
        for _, row in df.iterrows():
            features = {}
            
            # Features básicas da partida
            features['home_team_id'] = row['home_team_id']
            features['away_team_id'] = row['away_team_id']
            
            # Features temporais básicas
            try:
                date_str = row['date'].split('T')[0] if 'T' in row['date'] else row['date']
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                features['day_of_week'] = date_obj.weekday()
                features['month'] = date_obj.month
                features['is_weekend'] = 1 if date_obj.weekday() >= 5 else 0
            except:
                features['day_of_week'] = 0
                features['month'] = 1
                features['is_weekend'] = 0
            
            # Calcular estatísticas históricas simples
            home_stats = self._get_team_historical_stats(row['home_team_id'], row['date'])
            away_stats = self._get_team_historical_stats(row['away_team_id'], row['date'])
            
            # Features dos times
            features.update({f'home_{k}': v for k, v in home_stats.items()})
            features.update({f'away_{k}': v for k, v in away_stats.items()})
            
            # Features de interação
            features['goal_difference_avg'] = home_stats['avg_goals_for'] - away_stats['avg_goals_for']
            features['defense_difference'] = away_stats['avg_goals_against'] - home_stats['avg_goals_against']
            features['win_rate_difference'] = home_stats['win_rate'] - away_stats['win_rate']
            
            # Targets
            home_goals = row['home_goals']
            away_goals = row['away_goals']
            
            features['target_home_win'] = 1 if home_goals > away_goals else 0
            features['target_draw'] = 1 if home_goals == away_goals else 0
            features['target_away_win'] = 1 if away_goals > home_goals else 0
            features['target_over_2_5'] = 1 if (home_goals + away_goals) > 2.5 else 0
            features['target_btts'] = 1 if home_goals > 0 and away_goals > 0 else 0
            features['target_total_goals'] = home_goals + away_goals
            features['target_home_goals'] = home_goals
            features['target_away_goals'] = away_goals
            
            features_list.append(features)
        
        features_df = pd.DataFrame(features_list)
        print(f"✅ {len(features_df)} partidas processadas, {len(features_df.columns)} features criadas")
        
        return features_df
    
    def _get_team_historical_stats(self, team_id: int, match_date: str) -> Dict:
        """Calcula estatísticas históricas básicas de um time"""
        
        conn = sqlite3.connect(self.db_path)
        
        # Buscar jogos anteriores do time
        query = '''
            SELECT home_goals, away_goals, home_team_id, away_team_id
            FROM fixtures 
            WHERE (home_team_id = ? OR away_team_id = ?) 
            AND date < ? AND status_short = 'FT'
            ORDER BY date DESC 
            LIMIT 10
        '''
        
        games = conn.execute(query, [team_id, team_id, match_date]).fetchall()
        conn.close()
        
        if not games:
            # Valores padrão se não há histórico
            return {
                'games_played': 0,
                'avg_goals_for': 1.2,
                'avg_goals_against': 1.2,
                'win_rate': 0.4,
                'draw_rate': 0.3,
                'loss_rate': 0.3
            }
        
        # Calcular estatísticas
        goals_for = []
        goals_against = []
        results = []
        
        for game in games:
            home_goals, away_goals, home_id, away_id = game
            
            if home_id == team_id:
                # Time jogou em casa
                goals_for.append(home_goals)
                goals_against.append(away_goals)
                if home_goals > away_goals:
                    results.append('W')
                elif home_goals == away_goals:
                    results.append('D')
                else:
                    results.append('L')
            else:
                # Time jogou fora
                goals_for.append(away_goals)
                goals_against.append(home_goals)
                if away_goals > home_goals:
                    results.append('W')
                elif away_goals == home_goals:
                    results.append('D')
                else:
                    results.append('L')
        
        wins = results.count('W')
        draws = results.count('D')
        losses = results.count('L')
        total_games = len(results)
        
        return {
            'games_played': total_games,
            'avg_goals_for': np.mean(goals_for) if goals_for else 1.2,
            'avg_goals_against': np.mean(goals_against) if goals_against else 1.2,
            'win_rate': wins / total_games if total_games > 0 else 0.4,
            'draw_rate': draws / total_games if total_games > 0 else 0.3,
            'loss_rate': losses / total_games if total_games > 0 else 0.3
        }
    
    def prepare_training_data(self) -> pd.DataFrame:
        """Prepara dados de treinamento"""
        
        print("📊 Preparando dados de treinamento...")
        
        conn = sqlite3.connect(self.db_path)
        
        # Buscar partidas finalizadas
        query = '''
            SELECT 
                f.id as fixture_id,
                f.home_team_id,
                f.away_team_id,
                f.date,
                f.home_goals,
                f.away_goals,
                ht.name as home_team_name,
                at.name as away_team_name
            FROM fixtures f
            JOIN teams ht ON f.home_team_id = ht.id
            JOIN teams at ON f.away_team_id = at.id
            WHERE f.status_short = 'FT'
            ORDER BY f.date
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            print("❌ Nenhum dado encontrado")
            return pd.DataFrame()
        
        print(f"⚽ Partidas encontradas: {len(df)}")
        
        # Criar features
        features_df = self.create_basic_features(df)
        
        return features_df
    
    def train_models(self, df: pd.DataFrame) -> Dict:
        """Treina modelos de ML"""
        
        if df.empty:
            print("❌ Nenhum dado para treinamento")
            return {}
        
        print("🤖 Treinando modelos de machine learning...")
        
        # Separar features e targets
        feature_cols = [col for col in df.columns if not col.startswith('target_')]
        X = df[feature_cols].fillna(0)
        
        # Targets de classificação
        classification_targets = {
            'home_win': 'target_home_win',
            'draw': 'target_draw', 
            'away_win': 'target_away_win',
            'over_2_5': 'target_over_2_5',
            'btts': 'target_btts'
        }
        
        # Targets de regressão
        regression_targets = {
            'total_goals': 'target_total_goals',
            'home_goals': 'target_home_goals',
            'away_goals': 'target_away_goals'
        }
        
        results = {'classification': {}, 'regression': {}}
        
        # Split temporal
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        
        # Treinar modelos de classificação
        print("\n📊 Modelos de Classificação:")
        for target_name, target_col in classification_targets.items():
            if target_col not in df.columns:
                continue
                
            y = df[target_col]
            y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
            
            print(f"\n🎯 Treinando {target_name}...")
            
            # Normalização
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            self.scalers[target_name] = scaler
            
            # Modelos
            models = {
                'logistic': LogisticRegression(random_state=42, max_iter=1000),
                'random_forest': RandomForestClassifier(n_estimators=100, random_state=42)
            }
            
            if XGBOOST_AVAILABLE:
                models['xgboost'] = xgb.XGBClassifier(n_estimators=100, random_state=42, eval_metric='logloss')
            
            target_results = {}
            
            for model_name, model in models.items():
                try:
                    # Treinar
                    if model_name == 'logistic':
                        model.fit(X_train_scaled, y_train)
                        y_pred = model.predict(X_test_scaled)
                        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
                    else:
                        model.fit(X_train, y_train)
                        y_pred = model.predict(X_test)
                        y_pred_proba = model.predict_proba(X_test)[:, 1]
                    
                    # Métricas
                    metrics = {
                        'accuracy': accuracy_score(y_test, y_pred),
                        'precision': precision_score(y_test, y_pred, zero_division=0),
                        'recall': recall_score(y_test, y_pred, zero_division=0),
                        'f1': f1_score(y_test, y_pred, zero_division=0),
                        'auc': roc_auc_score(y_test, y_pred_proba) if len(np.unique(y_test)) > 1 else 0
                    }
                    
                    target_results[model_name] = {
                        'model': model,
                        'metrics': metrics
                    }
                    
                    print(f"   {model_name}: Accuracy={metrics['accuracy']:.3f}, AUC={metrics['auc']:.3f}")
                    
                except Exception as e:
                    print(f"   ❌ Erro {model_name}: {str(e)}")
            
            results['classification'][target_name] = target_results
        
        # Treinar modelos de regressão
        print(f"\n📈 Modelos de Regressão:")
        for target_name, target_col in regression_targets.items():
            if target_col not in df.columns:
                continue
                
            y = df[target_col]
            y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
            
            print(f"\n🎯 Treinando {target_name}...")
            
            # Modelos
            models = {
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42)
            }
            
            if XGBOOST_AVAILABLE:
                models['xgboost'] = xgb.XGBRegressor(n_estimators=100, random_state=42)
            
            target_results = {}
            
            for model_name, model in models.items():
                try:
                    # Treinar
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    
                    # Métricas
                    metrics = {
                        'mse': mean_squared_error(y_test, y_pred),
                        'mae': mean_absolute_error(y_test, y_pred),
                        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                        'r2': r2_score(y_test, y_pred)
                    }
                    
                    target_results[model_name] = {
                        'model': model,
                        'metrics': metrics
                    }
                    
                    print(f"   {model_name}: RMSE={metrics['rmse']:.3f}, R²={metrics['r2']:.3f}")
                    
                except Exception as e:
                    print(f"   ❌ Erro {model_name}: {str(e)}")
            
            results['regression'][target_name] = target_results
        
        self.models = results
        return results
    
    def save_models(self, save_dir: str = "models/") -> None:
        """Salva modelos treinados"""
        
        os.makedirs(save_dir, exist_ok=True)
        print(f"\n💾 Salvando modelos em {save_dir}...")
        
        # Salvar modelos de classificação
        if 'classification' in self.models:
            for target in self.models['classification']:
                for model_name, model_data in self.models['classification'][target].items():
                    filename = f"{save_dir}{target}_{model_name}_classifier.joblib"
                    joblib.dump(model_data['model'], filename)
                    print(f"   ✅ {filename}")
        
        # Salvar modelos de regressão
        if 'regression' in self.models:
            for target in self.models['regression']:
                for model_name, model_data in self.models['regression'][target].items():
                    filename = f"{save_dir}{target}_{model_name}_regressor.joblib"
                    joblib.dump(model_data['model'], filename)
                    print(f"   ✅ {filename}")
        
        # Salvar scalers
        for target, scaler in self.scalers.items():
            filename = f"{save_dir}{target}_scaler.joblib"
            joblib.dump(scaler, filename)
            print(f"   ✅ {filename}")
    
    def generate_report(self) -> str:
        """Gera relatório dos modelos"""
        
        report = "# RELATÓRIO DE MODELOS DE MACHINE LEARNING\n\n"
        report += f"**Data de treinamento:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Modelos de classificação
        if 'classification' in self.models:
            report += "## 🎯 MODELOS DE CLASSIFICAÇÃO\n\n"
            
            for target in self.models['classification']:
                report += f"### {target.upper()}\n\n"
                
                for model_name, model_data in self.models['classification'][target].items():
                    metrics = model_data['metrics']
                    report += f"**{model_name}:**\n"
                    report += f"- Accuracy: {metrics['accuracy']:.3f}\n"
                    report += f"- Precision: {metrics['precision']:.3f}\n"
                    report += f"- Recall: {metrics['recall']:.3f}\n"
                    report += f"- F1-Score: {metrics['f1']:.3f}\n"
                    report += f"- AUC: {metrics['auc']:.3f}\n\n"
        
        # Modelos de regressão
        if 'regression' in self.models:
            report += "## 📈 MODELOS DE REGRESSÃO\n\n"
            
            for target in self.models['regression']:
                report += f"### {target.upper()}\n\n"
                
                for model_name, model_data in self.models['regression'][target].items():
                    metrics = model_data['metrics']
                    report += f"**{model_name}:**\n"
                    report += f"- RMSE: {metrics['rmse']:.3f}\n"
                    report += f"- MAE: {metrics['mae']:.3f}\n"
                    report += f"- R²: {metrics['r2']:.3f}\n\n"
        
        # Recomendações
        report += "## 💡 RECOMENDAÇÕES\n\n"
        
        if 'classification' in self.models:
            for target in self.models['classification']:
                best_model = None
                best_auc = 0
                
                for model_name, model_data in self.models['classification'][target].items():
                    auc = model_data['metrics']['auc']
                    if auc > best_auc:
                        best_auc = auc
                        best_model = model_name
                
                if best_model:
                    report += f"- **{target}**: Usar {best_model} (AUC: {best_auc:.3f})\n"
        
        report += "\n## 🚀 PRÓXIMOS PASSOS\n\n"
        report += "1. Implementar sistema de predição em tempo real\n"
        report += "2. Criar interface web para visualização\n"
        report += "3. Monitorar performance em produção\n"
        report += "4. Retreinar modelos periodicamente\n"
        
        return report
    
    def predict_match(self, home_team_id: int, away_team_id: int, match_date: str = None) -> Dict:
        """Faz predição para uma partida específica"""
        
        if not self.models:
            return {"error": "Modelos não treinados"}
        
        if match_date is None:
            match_date = datetime.now().strftime('%Y-%m-%d')
        
        # Criar features para a partida
        features = {}
        features['home_team_id'] = home_team_id
        features['away_team_id'] = away_team_id
        
        # Features temporais
        try:
            date_obj = datetime.strptime(match_date, '%Y-%m-%d')
            features['day_of_week'] = date_obj.weekday()
            features['month'] = date_obj.month
            features['is_weekend'] = 1 if date_obj.weekday() >= 5 else 0
        except:
            features['day_of_week'] = 0
            features['month'] = 1
            features['is_weekend'] = 0
        
        # Estatísticas dos times
        home_stats = self._get_team_historical_stats(home_team_id, match_date)
        away_stats = self._get_team_historical_stats(away_team_id, match_date)
        
        features.update({f'home_{k}': v for k, v in home_stats.items()})
        features.update({f'away_{k}': v for k, v in away_stats.items()})
        
        # Features de interação
        features['goal_difference_avg'] = home_stats['avg_goals_for'] - away_stats['avg_goals_for']
        features['defense_difference'] = away_stats['avg_goals_against'] - home_stats['avg_goals_against']
        features['win_rate_difference'] = home_stats['win_rate'] - away_stats['win_rate']
        
        # Converter para DataFrame
        X = pd.DataFrame([features])
        
        predictions = {}
        
        # Predições de classificação
        if 'classification' in self.models:
            for target in self.models['classification']:
                if self.models['classification'][target]:
                    # Usar o primeiro modelo disponível
                    model_name = list(self.models['classification'][target].keys())[0]
                    model = self.models['classification'][target][model_name]['model']
                    
                    try:
                        if target in self.scalers:
                            X_scaled = self.scalers[target].transform(X)
                            prob = model.predict_proba(X_scaled)[0, 1]
                        else:
                            prob = model.predict_proba(X)[0, 1]
                        
                        predictions[target] = {
                            'probability': prob,
                            'prediction': 1 if prob > 0.5 else 0,
                            'model_used': model_name
                        }
                    except Exception as e:
                        predictions[target] = {'error': str(e)}
        
        # Predições de regressão
        if 'regression' in self.models:
            for target in self.models['regression']:
                if self.models['regression'][target]:
                    # Usar o primeiro modelo disponível
                    model_name = list(self.models['regression'][target].keys())[0]
                    model = self.models['regression'][target][model_name]['model']
                    
                    try:
                        value = model.predict(X)[0]
                        predictions[target] = {
                            'value': value,
                            'model_used': model_name
                        }
                    except Exception as e:
                        predictions[target] = {'error': str(e)}
        
        return predictions

def demo_simplified_training():
    """Demonstração do treinamento simplificado"""
    print("🤖 DEMONSTRAÇÃO DE TREINAMENTO SIMPLIFICADO")
    print("=" * 70)
    
    # Inicializar trainer
    trainer = SimplifiedFootballMLTrainer()
    
    # Preparar dados
    df = trainer.prepare_training_data()
    
    if df.empty:
        print("❌ Nenhum dado disponível")
        return
    
    # Treinar modelos
    results = trainer.train_models(df)
    
    # Salvar modelos
    trainer.save_models()
    
    # Gerar relatório
    report = trainer.generate_report()
    with open('ml_models_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Teste de predição
    print(f"\n🔮 Teste de Predição:")
    prediction = trainer.predict_match(131, 124)  # Flamengo vs Palmeiras
    
    for target, result in prediction.items():
        if 'error' not in result:
            if 'probability' in result:
                print(f"   {target}: {result['probability']:.3f} ({result['model_used']})")
            else:
                print(f"   {target}: {result['value']:.2f} ({result['model_used']})")
    
    print(f"\n✅ Treinamento concluído!")
    print(f"📄 Relatório: ml_models_report.md")
    print(f"💾 Modelos salvos em: models/")
    
    return trainer

if __name__ == "__main__":
    demo_simplified_training()

