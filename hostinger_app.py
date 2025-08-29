ERROR: Can not perform a '--user' install. User site-packages are not visible in this virtualenv.#!/usr/bin/env python3
"""
Aplicação Flask otimizada para Hostinger
"""

import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS

# Configurar path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports do sistema
try:
    from real_time_api_integration import EnhancedRealTimePredictionSystem
    from simplified_ml_training import SimplifiedFootballMLTrainer
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)

# Configurar logging para Hostinger
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
CORS(app)

# Carregar configuração
try:
    with open('hostinger_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
except FileNotFoundError:
    config = {
        'hostinger': {'debug': False, 'host': '0.0.0.0', 'port': 5000},
        'api': {'api_key': None}
    }

# Sistema de predição global
prediction_system = None

def initialize_system():
    """Inicializa sistema de predição"""
    global prediction_system
    
    try:
        api_key = config.get('api', {}).get('api_key')
        prediction_system = EnhancedRealTimePredictionSystem(api_key=api_key)
        
        # Verificar se modelos existem
        if not os.path.exists('models'):
            print("⚠️  Modelos não encontrados - treinando...")
            trainer = SimplifiedFootballMLTrainer()
            data = trainer.prepare_training_data()
            if not data.empty:
                trainer.train_models(data)
                trainer.save_models()
        
        print("✅ Sistema inicializado")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inicializar: {e}")
        return False

# Template HTML responsivo
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Football Prediction System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .card { 
            background: white; 
            padding: 25px; 
            margin: 15px 0; 
            border-radius: 15px; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .status-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin: 20px 0;
        }
        .metric { 
            text-align: center; 
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        .metric h3 { 
            font-size: 2.5em; 
            margin-bottom: 10px;
            color: #2c3e50;
        }
        .metric p { 
            color: #7f8c8d; 
            font-weight: 500;
        }
        .status-ok { color: #27ae60; }
        .status-warning { color: #f39c12; }
        .status-error { color: #e74c3c; }
        .btn {
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            margin: 5px;
            transition: all 0.3s ease;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .btn-danger {
            background: linear-gradient(45deg, #e74c3c, #c0392b);
        }
        .api-info {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        .footer {
            text-align: center;
            color: white;
            margin-top: 40px;
            opacity: 0.8;
        }
        @media (max-width: 768px) {
            .container { padding: 10px; }
            .header h1 { font-size: 2em; }
            .status-grid { grid-template-columns: 1fr; }
        }
    </style>
    <script>
        function refreshData() {
            location.reload();
        }
        
        function startSystem() {
            fetch('/api/start', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message || 'Sistema iniciado');
                    setTimeout(refreshData, 2000);
                })
                .catch(err => alert('Erro: ' + err));
        }
        
        function stopSystem() {
            fetch('/api/stop', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message || 'Sistema parado');
                    setTimeout(refreshData, 2000);
                })
                .catch(err => alert('Erro: ' + err));
        }
        
        // Auto refresh a cada 60 segundos
        setInterval(refreshData, 60000);
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚽ Football Prediction System</h1>
            <p>Sistema de Predições de Futebol em Tempo Real</p>
        </div>
        
        <div class="card">
            <h2>📊 Status do Sistema</h2>
            <div class="status-grid">
                <div class="metric">
                    <h3 class="{{ 'status-ok' if system_active else 'status-error' }}">
                        {{ '🟢' if system_active else '🔴' }}
                    </h3>
                    <p>{{ 'Sistema Ativo' if system_active else 'Sistema Inativo' }}</p>
                </div>
                <div class="metric">
                    <h3>{{ active_matches }}</h3>
                    <p>Partidas Ativas</p>
                </div>
                <div class="metric">
                    <h3>{{ total_predictions }}</h3>
                    <p>Predições Feitas</p>
                </div>
                <div class="metric">
                    <h3 class="status-ok">{{ api_status }}</h3>
                    <p>Status da API</p>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 20px;">
                {% if system_active %}
                    <button class="btn btn-danger" onclick="stopSystem()">Parar Sistema</button>
                {% else %}
                    <button class="btn" onclick="startSystem()">Iniciar Sistema</button>
                {% endif %}
                <button class="btn" onclick="refreshData()">Atualizar</button>
            </div>
        </div>
        
        <div class="card">
            <h2>🔧 Configuração da API</h2>
            <div class="api-info">
                <p><strong>Status:</strong> {{ 'Configurada' if api_configured else 'Não configurada' }}</p>
                <p><strong>Modo:</strong> {{ 'Dados reais' if api_configured else 'Dados simulados' }}</p>
                {% if not api_configured %}
                <p><strong>⚠️ Para usar dados reais:</strong></p>
                <ol>
                    <li>Obtenha uma API key gratuita em <a href="https://www.api-football.com/" target="_blank">API-Football</a></li>
                    <li>Edite o arquivo <code>hostinger_config.json</code></li>
                    <li>Adicione sua chave no campo <code>api.api_key</code></li>
                    <li>Reinicie o sistema</li>
                </ol>
                {% endif %}
            </div>
        </div>
        
        <div class="card">
            <h2>📡 Endpoints da API</h2>
            <ul style="list-style-type: none; padding: 0;">
                <li style="margin: 10px 0;"><strong>GET /api/status</strong> - Status do sistema</li>
                <li style="margin: 10px 0;"><strong>GET /api/predictions</strong> - Predições ativas</li>
                <li style="margin: 10px 0;"><strong>GET /api/matches</strong> - Partidas ao vivo</li>
                <li style="margin: 10px 0;"><strong>POST /api/start</strong> - Iniciar sistema</li>
                <li style="margin: 10px 0;"><strong>POST /api/stop</strong> - Parar sistema</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Última atualização: {{ timestamp }}</p>
            <p>Hostinger Deployment - Auto-refresh a cada 60s</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Dashboard principal"""
    try:
        system_active = prediction_system is not None and prediction_system.is_running
        active_matches = len(prediction_system.active_matches) if prediction_system else 0
        total_predictions = len(prediction_system.prediction_history) if prediction_system else 0
        api_configured = config.get('api', {}).get('api_key') is not None
        api_status = 'Configurada' if api_configured else 'Simulada'
        
        return render_template_string(HTML_TEMPLATE,
            system_active=system_active,
            active_matches=active_matches,
            total_predictions=total_predictions,
            api_configured=api_configured,
            api_status=api_status,
            timestamp=datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        )
    except Exception as e:
        return f"Erro: {str(e)}", 500

@app.route('/api/status')
def api_status():
    """Status da API"""
    try:
        return jsonify({
            'system_active': prediction_system is not None,
            'running': prediction_system.is_running if prediction_system else False,
            'active_matches': len(prediction_system.active_matches) if prediction_system else 0,
            'total_predictions': len(prediction_system.prediction_history) if prediction_system else 0,
            'api_configured': config.get('api', {}).get('api_key') is not None,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/start', methods=['POST'])
def start_system():
    """Inicia sistema"""
    global prediction_system
    
    try:
        if not prediction_system:
            if not initialize_system():
                return jsonify({'success': False, 'message': 'Falha ao inicializar sistema'}), 500
        
        if not prediction_system.is_running:
            prediction_system.start_enhanced_monitoring()
            return jsonify({'success': True, 'message': 'Sistema iniciado com sucesso'})
        else:
            return jsonify({'success': False, 'message': 'Sistema já está rodando'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_system():
    """Para sistema"""
    try:
        if prediction_system and prediction_system.is_running:
            prediction_system.stop_monitoring()
            return jsonify({'success': True, 'message': 'Sistema parado'})
        else:
            return jsonify({'success': False, 'message': 'Sistema não está rodando'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/predictions')
def get_predictions():
    """Predições ativas"""
    try:
        if not prediction_system:
            return jsonify({'predictions': {}, 'count': 0})
        
        predictions = {}
        for fixture_id, pred in prediction_system.active_matches.items():
            predictions[str(fixture_id)] = {
                'home_team': pred.home_team,
                'away_team': pred.away_team,
                'elapsed_time': pred.elapsed_time,
                'current_score': pred.current_score,
                'home_win_prob': round(pred.home_win_prob * 100, 1),
                'draw_prob': round(pred.draw_prob * 100, 1),
                'away_win_prob': round(pred.away_win_prob * 100, 1),
                'confidence': round(pred.confidence_score * 100, 1),
                'value_bets': len(pred.value_bets)
            }
        
        return jsonify({
            'predictions': predictions,
            'count': len(predictions),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/matches')
def get_matches():
    """Partidas ao vivo"""
    try:
        if not prediction_system:
            return jsonify({'matches': [], 'count': 0})
        
        matches = prediction_system.get_live_matches()
        
        simplified_matches = []
        for match in matches[:5]:  # Limitar a 5 para performance
            simplified_matches.append({
                'fixture_id': match['fixture']['id'],
                'home_team': match['teams']['home']['name'],
                'away_team': match['teams']['away']['name'],
                'status': match['fixture']['status']['short'],
                'elapsed': match['fixture']['status'].get('elapsed', 0),
                'score_home': match['goals'].get('home', 0),
                'score_away': match['goals'].get('away', 0)
            })
        
        return jsonify({
            'matches': simplified_matches,
            'count': len(simplified_matches),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Iniciando Football Prediction System para Hostinger...")
    
    # Inicializar sistema automaticamente
    initialize_system()
    
    # Configurações do servidor
    host = config.get('hostinger', {}).get('host', '0.0.0.0')
    port = int(os.environ.get('PORT', config.get('hostinger', {}).get('port', 5000)))
    debug = config.get('hostinger', {}).get('debug', False)
    
    print(f"🌐 Servidor rodando em http://{host}:{port}")
    
    # Iniciar servidor
    app.run(host=host, port=port, debug=debug, threaded=True)
