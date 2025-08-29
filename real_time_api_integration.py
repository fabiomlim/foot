#!/usr/bin/env python3
"""
Sistema de integração com APIs de dados de futebol em tempo real
"""

import requests
import json
import time
import threading
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

# Imports do sistema de predição
def minha_funcao():
    from real_time_api_integration import RealTimePredictionSystem, MatchPrediction
from simplified_ml_training import SimplifiedFootballMLTrainer

@dataclass
class APIConfig:
    """Configuração das APIs"""
    name: str
    base_url: str
    headers: Dict[str, str]
    endpoints: Dict[str, str]
    rate_limit: int  # requests per minute
    free_tier_limit: int  # requests per day

class RealTimeAPIManager:
    """Gerenciador de APIs em tempo real"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.apis = self._setup_apis()
        self.current_api = None
        self.request_counts = {}
        self.last_request_time = {}
        
        # Configurações
        self.update_interval = 30  # segundos
        self.max_retries = 3
        self.timeout = 10
        
        # Cache
        self.cache = {}
        self.cache_duration = 300  # 5 minutos
        
        # Selecionar API principal
        self._select_primary_api()
    
    def _setup_apis(self) -> Dict[str, APIConfig]:
        """Configura APIs disponíveis"""
        
        apis = {}
        
        # API-Football (Principal)
        if self.api_key:
            apis['api_football'] = APIConfig(
                name="API-Football",
                base_url="https://v3.football.api-sports.io",
                headers={
                    'x-apisports-key': self.api_key,
                    'x-apisports-host': 'v3.football.api-sports.io'
                },
                endpoints={
                    'live_fixtures': '/fixtures?live=all',
                    'fixture_statistics': '/fixtures/statistics?fixture={fixture_id}',
                    'fixture_events': '/fixtures/events?fixture={fixture_id}',
                    'odds': '/odds?fixture={fixture_id}',
                    'predictions': '/predictions?fixture={fixture_id}',
                    'teams': '/teams?id={team_id}',
                    'leagues': '/leagues'
                },
                rate_limit=10,  # 10 requests per minute
                free_tier_limit=100  # 100 requests per day
            )
        
        # Football-Data.org (Backup)
        apis['football_data'] = APIConfig(
            name="Football-Data.org",
            base_url="https://api.football-data.org/v4",
            headers={
                'X-Auth-Token': 'YOUR_TOKEN_HERE'  # Usuário deve configurar
            },
            endpoints={
                'live_matches': '/matches?status=LIVE',
                'match_details': '/matches/{match_id}',
                'competitions': '/competitions'
            },
            rate_limit=10,
            free_tier_limit=10  # Muito limitado
        )
        
        # Sportmonks (Alternativa)
        apis['sportmonks'] = APIConfig(
            name="Sportmonks",
            base_url="https://api.sportmonks.com/v3/football",
            headers={
                'Authorization': 'Bearer YOUR_TOKEN_HERE'
            },
            endpoints={
                'live_fixtures': '/livescores',
                'fixture_details': '/fixtures/{fixture_id}',
                'statistics': '/fixtures/{fixture_id}/statistics'
            },
            rate_limit=60,
            free_tier_limit=180  # 180 requests per hour
        )
        
        return apis
    
    def _select_primary_api(self):
        """Seleciona API principal baseada na disponibilidade"""
        
        if 'api_football' in self.apis and self.api_key:
            self.current_api = 'api_football'
            print(f"✅ API principal: {self.apis[self.current_api].name}")
        else:
            # Usar modo simulado se não há API configurada
            self.current_api = None
            print("⚠️  Nenhuma API configurada - usando modo simulado")
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Faz requisição para API com rate limiting e cache"""
        
        if not self.current_api:
            return None
        
        api_config = self.apis[self.current_api]
        
        # Verificar rate limiting
        now = time.time()
        api_name = self.current_api
        
        if api_name not in self.request_counts:
            self.request_counts[api_name] = 0
            self.last_request_time[api_name] = now
        
        # Reset contador a cada minuto
        if now - self.last_request_time[api_name] > 60:
            self.request_counts[api_name] = 0
            self.last_request_time[api_name] = now
        
        # Verificar limite
        if self.request_counts[api_name] >= api_config.rate_limit:
            print(f"⚠️  Rate limit atingido para {api_config.name}")
            return None
        
        # Verificar cache
        cache_key = f"{api_name}_{endpoint}_{str(params)}"
        if cache_key in self.cache:
            cache_time, cache_data = self.cache[cache_key]
            if now - cache_time < self.cache_duration:
                return cache_data
        
        # Fazer requisição
        url = api_config.base_url + endpoint
        
        try:
            response = requests.get(
                url,
                headers=api_config.headers,
                params=params,
                timeout=self.timeout
            )
            
            self.request_counts[api_name] += 1
            
            if response.status_code == 200:
                data = response.json()
                
                # Salvar no cache
                self.cache[cache_key] = (now, data)
                
                return data
            else:
                print(f"❌ Erro na API {api_config.name}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            return None
    
    def get_live_fixtures(self) -> List[Dict]:
        """Busca partidas ao vivo"""
        
        if not self.current_api:
            return self._get_simulated_fixtures()
        
        api_config = self.apis[self.current_api]
        endpoint = api_config.endpoints['live_fixtures']
        
        data = self._make_request(endpoint)
        
        if data and 'response' in data:
            return data['response']
        else:
            print("⚠️  Falha na API - usando dados simulados")
            return self._get_simulated_fixtures()
    
    def get_fixture_statistics(self, fixture_id: int) -> Optional[Dict]:
        """Busca estatísticas de uma partida"""
        
        if not self.current_api:
            return self._get_simulated_statistics(fixture_id)
        
        api_config = self.apis[self.current_api]
        endpoint = api_config.endpoints['fixture_statistics'].format(fixture_id=fixture_id)
        
        data = self._make_request(endpoint)
        
        if data and 'response' in data:
            return data['response']
        else:
            return self._get_simulated_statistics(fixture_id)
    
    def get_fixture_odds(self, fixture_id: int) -> Optional[Dict]:
        """Busca odds de uma partida"""
        
        if not self.current_api:
            return self._get_simulated_odds(fixture_id)
        
        api_config = self.apis[self.current_api]
        
        if 'odds' in api_config.endpoints:
            endpoint = api_config.endpoints['odds'].format(fixture_id=fixture_id)
            data = self._make_request(endpoint)
            
            if data and 'response' in data:
                return data['response']
        
        return self._get_simulated_odds(fixture_id)
    
    def _get_simulated_fixtures(self) -> List[Dict]:
        """Gera partidas simuladas para demonstração"""
        
        current_time = datetime.now()
        
        fixtures = [
            {
                'fixture': {
                    'id': 12345,
                    'date': current_time.isoformat(),
                    'status': {'short': '1H', 'elapsed': 35},
                    'venue': {'name': 'Maracanã', 'city': 'Rio de Janeiro'}
                },
                'league': {
                    'id': 71,
                    'name': 'Brasileirão Série A',
                    'country': 'Brazil'
                },
                'teams': {
                    'home': {'id': 131, 'name': 'Flamengo', 'logo': 'flamengo.png'},
                    'away': {'id': 124, 'name': 'Palmeiras', 'logo': 'palmeiras.png'}
                },
                'goals': {'home': 1, 'away': 0},
                'score': {
                    'halftime': {'home': 1, 'away': 0},
                    'fulltime': {'home': None, 'away': None}
                }
            },
            {
                'fixture': {
                    'id': 12346,
                    'date': current_time.isoformat(),
                    'status': {'short': '2H', 'elapsed': 67},
                    'venue': {'name': 'Neo Química Arena', 'city': 'São Paulo'}
                },
                'league': {
                    'id': 71,
                    'name': 'Brasileirão Série A',
                    'country': 'Brazil'
                },
                'teams': {
                    'home': {'id': 132, 'name': 'Corinthians', 'logo': 'corinthians.png'},
                    'away': {'id': 133, 'name': 'São Paulo', 'logo': 'saopaulo.png'}
                },
                'goals': {'home': 2, 'away': 1},
                'score': {
                    'halftime': {'home': 1, 'away': 0},
                    'fulltime': {'home': None, 'away': None}
                }
            },
            {
                'fixture': {
                    'id': 12347,
                    'date': current_time.isoformat(),
                    'status': {'short': '1H', 'elapsed': 25},
                    'venue': {'name': 'Allianz Parque', 'city': 'São Paulo'}
                },
                'league': {
                    'id': 71,
                    'name': 'Brasileirão Série A',
                    'country': 'Brazil'
                },
                'teams': {
                    'home': {'id': 124, 'name': 'Palmeiras', 'logo': 'palmeiras.png'},
                    'away': {'id': 134, 'name': 'Santos', 'logo': 'santos.png'}
                },
                'goals': {'home': 0, 'away': 0},
                'score': {
                    'halftime': {'home': 0, 'away': 0},
                    'fulltime': {'home': None, 'away': None}
                }
            }
        ]
        
        return fixtures
    
    def _get_simulated_statistics(self, fixture_id: int) -> List[Dict]:
        """Gera estatísticas simuladas"""
        
        # Estatísticas baseadas no fixture_id para consistência
        np.random.seed(fixture_id)
        
        home_possession = np.random.randint(40, 70)
        away_possession = 100 - home_possession
        
        home_shots = np.random.randint(5, 20)
        away_shots = np.random.randint(5, 20)
        
        home_shots_on_target = int(home_shots * np.random.uniform(0.3, 0.6))
        away_shots_on_target = int(away_shots * np.random.uniform(0.3, 0.6))
        
        home_corners = np.random.randint(2, 12)
        away_corners = np.random.randint(2, 12)
        
        statistics = [
            {
                'team': {'id': 131, 'name': 'Home Team'},
                'statistics': [
                    {'type': 'Ball Possession', 'value': f'{home_possession}%'},
                    {'type': 'Total Shots', 'value': home_shots},
                    {'type': 'Shots on Goal', 'value': home_shots_on_target},
                    {'type': 'Corner Kicks', 'value': home_corners},
                    {'type': 'Fouls', 'value': np.random.randint(5, 20)},
                    {'type': 'Yellow Cards', 'value': np.random.randint(0, 4)},
                    {'type': 'Red Cards', 'value': np.random.randint(0, 1)},
                    {'type': 'Passes %', 'value': f'{np.random.randint(70, 95)}%'}
                ]
            },
            {
                'team': {'id': 124, 'name': 'Away Team'},
                'statistics': [
                    {'type': 'Ball Possession', 'value': f'{away_possession}%'},
                    {'type': 'Total Shots', 'value': away_shots},
                    {'type': 'Shots on Goal', 'value': away_shots_on_target},
                    {'type': 'Corner Kicks', 'value': away_corners},
                    {'type': 'Fouls', 'value': np.random.randint(5, 20)},
                    {'type': 'Yellow Cards', 'value': np.random.randint(0, 4)},
                    {'type': 'Red Cards', 'value': np.random.randint(0, 1)},
                    {'type': 'Passes %', 'value': f'{np.random.randint(70, 95)}%'}
                ]
            }
        ]
        
        return statistics
    
    def _get_simulated_odds(self, fixture_id: int) -> List[Dict]:
        """Gera odds simuladas"""
        
        np.random.seed(fixture_id + 1000)  # Seed diferente para odds
        
        # Gerar odds realistas
        home_odds = np.random.uniform(1.5, 4.0)
        draw_odds = np.random.uniform(2.8, 4.5)
        away_odds = np.random.uniform(1.5, 4.0)
        
        over_2_5_odds = np.random.uniform(1.6, 2.5)
        under_2_5_odds = np.random.uniform(1.4, 2.2)
        
        btts_yes_odds = np.random.uniform(1.7, 2.3)
        btts_no_odds = np.random.uniform(1.5, 2.1)
        
        odds = [
            {
                'bookmaker': {'id': 1, 'name': 'Bet365'},
                'bets': [
                    {
                        'id': 1,
                        'name': 'Match Winner',
                        'values': [
                            {'value': 'Home', 'odd': f'{home_odds:.2f}'},
                            {'value': 'Draw', 'odd': f'{draw_odds:.2f}'},
                            {'value': 'Away', 'odd': f'{away_odds:.2f}'}
                        ]
                    },
                    {
                        'id': 2,
                        'name': 'Goals Over/Under',
                        'values': [
                            {'value': 'Over 2.5', 'odd': f'{over_2_5_odds:.2f}'},
                            {'value': 'Under 2.5', 'odd': f'{under_2_5_odds:.2f}'}
                        ]
                    },
                    {
                        'id': 3,
                        'name': 'Both Teams Score',
                        'values': [
                            {'value': 'Yes', 'odd': f'{btts_yes_odds:.2f}'},
                            {'value': 'No', 'odd': f'{btts_no_odds:.2f}'}
                        ]
                    }
                ]
            }
        ]
        
        return odds

class EnhancedRealTimePredictionSystem(RealTimePredictionSystem):
    """Sistema de predição aprimorado com integração de API"""
    
    def __init__(self, models_dir: str = "models/", api_key: str = None):
        super().__init__(models_dir, api_key)
        
        # Gerenciador de API
        self.api_manager = RealTimeAPIManager(api_key)
        
        # Banco de dados para histórico
        self.db_path = "real_time_predictions.db"
        self._setup_database()
        
        # Configurações aprimoradas
        self.prediction_history_limit = 1000
        self.auto_save_interval = 300  # 5 minutos
        
    def _setup_database(self):
        """Configura banco de dados para histórico"""
        
        conn = sqlite3.connect(self.db_path)
        
        # Tabela de predições em tempo real
        conn.execute('''
            CREATE TABLE IF NOT EXISTS real_time_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fixture_id INTEGER,
                timestamp TEXT,
                elapsed_time INTEGER,
                home_team TEXT,
                away_team TEXT,
                current_score TEXT,
                home_win_prob REAL,
                draw_prob REAL,
                away_win_prob REAL,
                over_2_5_prob REAL,
                btts_prob REAL,
                expected_total_goals REAL,
                confidence_score REAL,
                value_bets_json TEXT,
                live_stats_json TEXT
            )
        ''')
        
        # Tabela de estatísticas ao vivo
        conn.execute('''
            CREATE TABLE IF NOT EXISTS live_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fixture_id INTEGER,
                timestamp TEXT,
                elapsed_time INTEGER,
                statistics_json TEXT
            )
        ''')
        
        # Tabela de odds
        conn.execute('''
            CREATE TABLE IF NOT EXISTS live_odds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fixture_id INTEGER,
                timestamp TEXT,
                bookmaker TEXT,
                odds_json TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Banco de dados configurado")
    
    def get_live_matches(self) -> List[Dict]:
        """Busca partidas ao vivo via API"""
        
        fixtures = self.api_manager.get_live_fixtures()
        
        # Enriquecer com estatísticas e odds
        enriched_fixtures = []
        
        for fixture in fixtures:
            fixture_id = fixture['fixture']['id']
            
            # Buscar estatísticas
            statistics = self.api_manager.get_fixture_statistics(fixture_id)
            if statistics:
                fixture['statistics'] = statistics
            
            # Buscar odds
            odds = self.api_manager.get_fixture_odds(fixture_id)
            if odds:
                fixture['odds'] = odds
            
            enriched_fixtures.append(fixture)
            
            # Salvar no banco
            self._save_live_data(fixture_id, statistics, odds)
        
        return enriched_fixtures
    
    def _save_live_data(self, fixture_id: int, statistics: List[Dict], odds: List[Dict]):
        """Salva dados ao vivo no banco"""
        
        conn = sqlite3.connect(self.db_path)
        timestamp = datetime.now().isoformat()
        
        # Salvar estatísticas
        if statistics:
            conn.execute('''
                INSERT INTO live_statistics 
                (fixture_id, timestamp, elapsed_time, statistics_json)
                VALUES (?, ?, ?, ?)
            ''', (fixture_id, timestamp, 0, json.dumps(statistics)))
        
        # Salvar odds
        if odds:
            for bookmaker_data in odds:
                conn.execute('''
                    INSERT INTO live_odds 
                    (fixture_id, timestamp, bookmaker, odds_json)
                    VALUES (?, ?, ?, ?)
                ''', (fixture_id, timestamp, 
                     bookmaker_data.get('bookmaker', {}).get('name', 'Unknown'),
                     json.dumps(bookmaker_data)))
        
        conn.commit()
        conn.close()
    
    def predict_match_enhanced(self, match_data: Dict) -> MatchPrediction:
        """Predição aprimorada com dados de API"""
        
        # Fazer predição base
        prediction = self.predict_match(match_data)
        
        # Aprimorar com dados de odds reais
        if 'odds' in match_data and match_data['odds']:
            prediction = self._enhance_prediction_with_odds(prediction, match_data['odds'])
        
        # Salvar no banco
        self._save_prediction_to_db(prediction)
        
        return prediction
    
    def _enhance_prediction_with_odds(self, prediction: MatchPrediction, odds_data: List[Dict]) -> MatchPrediction:
        """Aprimora predição com odds reais"""
        
        if not odds_data:
            return prediction
        
        # Extrair odds do primeiro bookmaker
        bookmaker = odds_data[0]
        bets = bookmaker.get('bets', [])
        
        real_odds = {}
        
        for bet in bets:
            bet_name = bet.get('name', '')
            values = bet.get('values', [])
            
            if 'Match Winner' in bet_name or 'Winner' in bet_name:
                for value in values:
                    if value['value'] == 'Home':
                        real_odds['home_win'] = float(value['odd'])
                    elif value['value'] == 'Draw':
                        real_odds['draw'] = float(value['odd'])
                    elif value['value'] == 'Away':
                        real_odds['away_win'] = float(value['odd'])
            
            elif 'Over/Under' in bet_name or 'Goals' in bet_name:
                for value in values:
                    if 'Over 2.5' in value['value']:
                        real_odds['over_2_5'] = float(value['odd'])
            
            elif 'Both Teams Score' in bet_name or 'BTTS' in bet_name:
                for value in values:
                    if value['value'] == 'Yes':
                        real_odds['btts'] = float(value['odd'])
        
        # Recalcular value bets com odds reais
        if real_odds:
            prediction.value_bets = self._calculate_value_bets_with_real_odds(prediction, real_odds)
        
        return prediction
    
    def _calculate_value_bets_with_real_odds(self, prediction: MatchPrediction, real_odds: Dict) -> List[Dict]:
        """Calcula value bets com odds reais"""
        
        value_bets = []
        
        # Mapear predições para odds
        prediction_mapping = {
            'home_win': prediction.home_win_prob,
            'draw': prediction.draw_prob,
            'away_win': prediction.away_win_prob,
            'over_2_5': prediction.over_2_5_prob,
            'btts': prediction.btts_prob
        }
        
        for market, predicted_prob in prediction_mapping.items():
            if market in real_odds:
                odds = real_odds[market]
                implied_prob = 1 / odds
                
                # Calcular value
                value = (predicted_prob * odds) - 1
                
                if value > self.value_threshold:
                    kelly_fraction = self._calculate_kelly(predicted_prob, odds)
                    
                    value_bets.append({
                        'market': market,
                        'predicted_prob': predicted_prob,
                        'odds': odds,
                        'implied_prob': implied_prob,
                        'value': value,
                        'kelly_fraction': kelly_fraction,
                        'recommendation': self._get_bet_recommendation(value),
                        'source': 'real_odds'
                    })
        
        return sorted(value_bets, key=lambda x: x['value'], reverse=True)
    
    def _save_prediction_to_db(self, prediction: MatchPrediction):
        """Salva predição no banco de dados"""
        
        conn = sqlite3.connect(self.db_path)
        
        conn.execute('''
            INSERT INTO real_time_predictions 
            (fixture_id, timestamp, elapsed_time, home_team, away_team, 
             current_score, home_win_prob, draw_prob, away_win_prob,
             over_2_5_prob, btts_prob, expected_total_goals, confidence_score,
             value_bets_json, live_stats_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prediction.fixture_id,
            prediction.last_updated,
            prediction.elapsed_time,
            prediction.home_team,
            prediction.away_team,
            f"{prediction.current_score[0]}-{prediction.current_score[1]}",
            prediction.home_win_prob,
            prediction.draw_prob,
            prediction.away_win_prob,
            prediction.over_2_5_prob,
            prediction.btts_prob,
            prediction.expected_total_goals,
            prediction.confidence_score,
            json.dumps(prediction.value_bets),
            json.dumps(prediction.live_stats)
        ))
        
        conn.commit()
        conn.close()
    
    def get_prediction_history(self, fixture_id: int = None, limit: int = 100) -> List[Dict]:
        """Busca histórico de predições"""
        
        conn = sqlite3.connect(self.db_path)
        
        if fixture_id:
            query = '''
                SELECT * FROM real_time_predictions 
                WHERE fixture_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            '''
            cursor = conn.execute(query, (fixture_id, limit))
        else:
            query = '''
                SELECT * FROM real_time_predictions 
                ORDER BY timestamp DESC 
                LIMIT ?
            '''
            cursor = conn.execute(query, (limit,))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        
        return results
    
    def start_enhanced_monitoring(self):
        """Inicia monitoramento aprimorado"""
        
        print("🚀 Iniciando monitoramento aprimorado com API...")
        self.is_running = True
        
        def enhanced_monitoring_loop():
            while self.is_running:
                try:
                    print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Atualizando dados...")
                    
                    # Buscar partidas ao vivo
                    live_matches = self.get_live_matches()
                    
                    if live_matches:
                        print(f"⚽ {len(live_matches)} partidas ao vivo encontradas")
                        
                        for match in live_matches:
                            fixture_id = match['fixture']['id']
                            
                            # Fazer predição aprimorada
                            prediction = self.predict_match_enhanced(match)
                            
                            # Armazenar predição
                            self.active_matches[fixture_id] = prediction
                            self.prediction_history.append(prediction)
                            
                            # Exibir predição
                            self._display_enhanced_prediction(prediction, match)
                            
                            # Verificar alertas
                            self._check_alerts(prediction)
                    
                    else:
                        print("📭 Nenhuma partida ao vivo encontrada")
                    
                    # Limpeza periódica
                    self._cleanup_old_data()
                    
                    # Aguardar próxima atualização
                    time.sleep(self.update_interval)
                    
                except Exception as e:
                    print(f"❌ Erro no monitoramento: {e}")
                    time.sleep(5)
        
        # Iniciar thread de monitoramento
        monitoring_thread = threading.Thread(target=enhanced_monitoring_loop)
        monitoring_thread.daemon = True
        monitoring_thread.start()
        
        return monitoring_thread
    
    def _display_enhanced_prediction(self, prediction: MatchPrediction, match_data: Dict):
        """Exibe predição aprimorada"""
        
        print(f"\n🔮 PREDIÇÃO APRIMORADA: {prediction.home_team} vs {prediction.away_team}")
        print(f"🏟️  {match_data['fixture']['venue']['name']} - {match_data['league']['name']}")
        print(f"⏱️  {prediction.elapsed_time}' - Placar: {prediction.current_score[0]}-{prediction.current_score[1]}")
        
        print(f"\n📊 Probabilidades:")
        print(f"   🏠 Casa: {prediction.home_win_prob:.1%}")
        print(f"   🤝 Empate: {prediction.draw_prob:.1%}")
        print(f"   ✈️  Fora: {prediction.away_win_prob:.1%}")
        print(f"   ⚽ Over 2.5: {prediction.over_2_5_prob:.1%}")
        print(f"   🎯 BTTS: {prediction.btts_prob:.1%}")
        
        print(f"\n🎯 Confiança: {prediction.confidence_score:.1%}")
        
        if prediction.value_bets:
            print(f"\n💰 Value Bets (Odds Reais):")
            for bet in prediction.value_bets[:3]:
                source = bet.get('source', 'simulado')
                print(f"   {bet['market']}: {bet['value']:.1%} value - Odds {bet['odds']:.2f} ({bet['recommendation']}) [{source}]")
        
        # Estatísticas ao vivo
        if 'statistics' in match_data and match_data['statistics']:
            stats = match_data['statistics']
            if len(stats) >= 2:
                home_stats = stats[0]['statistics']
                away_stats = stats[1]['statistics']
                
                print(f"\n📈 Estatísticas Ao Vivo:")
                for stat in home_stats:
                    if stat['type'] == 'Ball Possession':
                        home_poss = stat['value']
                        away_poss = next((s['value'] for s in away_stats if s['type'] == 'Ball Possession'), 'N/A')
                        print(f"   Posse: {home_poss} x {away_poss}")
                        break
    
    def _check_alerts(self, prediction: MatchPrediction):
        """Verifica alertas para value bets"""
        
        for bet in prediction.value_bets:
            if bet['recommendation'] == 'STRONG_BET':
                print(f"🚨 ALERTA: {bet['market']} com {bet['value']:.1%} value - STRONG BET!")
    
    def _cleanup_old_data(self):
        """Limpa dados antigos"""
        
        # Limitar histórico em memória
        if len(self.prediction_history) > self.prediction_history_limit:
            self.prediction_history = self.prediction_history[-self.prediction_history_limit:]
        
        # Limpar cache da API
        now = time.time()
        expired_keys = []
        
        for key, (cache_time, _) in self.api_manager.cache.items():
            if now - cache_time > self.api_manager.cache_duration:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.api_manager.cache[key]
    
    def generate_api_status_report(self) -> Dict:
        """Gera relatório de status da API"""
        
        api_manager = self.api_manager
        
        report = {
            'current_api': api_manager.current_api,
            'api_configured': api_manager.current_api is not None,
            'request_counts': api_manager.request_counts.copy(),
            'cache_size': len(api_manager.cache),
            'available_apis': list(api_manager.apis.keys()),
            'last_update': datetime.now().isoformat()
        }
        
        if api_manager.current_api:
            api_config = api_manager.apis[api_manager.current_api]
            report['current_api_info'] = {
                'name': api_config.name,
                'rate_limit': api_config.rate_limit,
                'free_tier_limit': api_config.free_tier_limit
            }
        
        return report

def demo_real_time_api_integration():
    """Demonstração da integração com API"""
    print("🚀 DEMONSTRAÇÃO DE INTEGRAÇÃO COM API EM TEMPO REAL")
    print("=" * 70)
    
    # Configurar API key (usuário deve fornecer)
    api_key = None  # Substitua pela sua chave da API-Football
    
    if not api_key:
        print("⚠️  API Key não configurada - usando modo simulado")
        print("💡 Para usar dados reais, configure API_KEY na linha 45")
    
    # Inicializar sistema aprimorado
    system = EnhancedRealTimePredictionSystem(api_key=api_key)
    
    # Gerar relatório de status da API
    api_status = system.generate_api_status_report()
    print(f"\n📡 Status da API:")
    print(f"   API Atual: {api_status['current_api'] or 'Simulado'}")
    print(f"   APIs Disponíveis: {len(api_status['available_apis'])}")
    print(f"   Cache: {api_status['cache_size']} entradas")
    
    # Buscar partidas ao vivo
    print(f"\n⚽ Buscando partidas ao vivo...")
    live_matches = system.get_live_matches()
    
    if live_matches:
        print(f"✅ {len(live_matches)} partidas encontradas")
        
        for match in live_matches[:2]:  # Processar apenas 2 para demonstração
            # Fazer predição aprimorada
            prediction = system.predict_match_enhanced(match)
            
            # Exibir predição
            system._display_enhanced_prediction(prediction, match)
            
            # Armazenar
            system.active_matches[prediction.fixture_id] = prediction
            system.prediction_history.append(prediction)
    
    # Mostrar histórico do banco
    print(f"\n📊 Histórico no banco de dados:")
    history = system.get_prediction_history(limit=5)
    print(f"   {len(history)} predições salvas")
    
    # Salvar dados
    system.save_predictions_history("enhanced_predictions_history.json")
    
    print(f"\n✅ Demonstração concluída!")
    print(f"📊 Predições ativas: {len(system.active_matches)}")
    print(f"📈 Histórico: {len(system.prediction_history)} predições")
    print(f"💾 Banco de dados: {system.db_path}")
    
    return system

if __name__ == "__main__":
    demo_real_time_api_integration()

