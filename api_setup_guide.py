#!/usr/bin/env python3
"""
Guia de configuração e teste de APIs de futebol
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import time

class APISetupGuide:
    """Guia para configuração de APIs de futebol"""
    
    def __init__(self):
        self.apis_info = self._get_apis_info()
    
    def _get_apis_info(self) -> Dict:
        """Informações sobre APIs disponíveis"""
        
        return {
            'api_football': {
                'name': 'API-Football (Recomendada)',
                'website': 'https://www.api-football.com/',
                'documentation': 'https://www.api-football.com/documentation-v3',
                'free_tier': {
                    'requests_per_day': 100,
                    'requests_per_minute': 10,
                    'features': ['Live fixtures', 'Statistics', 'Odds', 'Predictions']
                },
                'paid_plans': {
                    'basic': {'price': '$10/month', 'requests': '1000/day'},
                    'pro': {'price': '$25/month', 'requests': '5000/day'},
                    'ultra': {'price': '$50/month', 'requests': '15000/day'}
                },
                'pros': [
                    'Dados mais completos',
                    'Estatísticas detalhadas ao vivo',
                    'Odds de múltiplas casas',
                    'Predições próprias',
                    'Documentação excelente'
                ],
                'cons': [
                    'Limite baixo no plano gratuito',
                    'Requer cadastro'
                ]
            },
            'football_data': {
                'name': 'Football-Data.org',
                'website': 'https://www.football-data.org/',
                'documentation': 'https://www.football-data.org/documentation/quickstart',
                'free_tier': {
                    'requests_per_minute': 10,
                    'requests_per_day': 'Unlimited',
                    'features': ['Basic fixtures', 'Limited leagues']
                },
                'paid_plans': {
                    'basic': {'price': '€0', 'requests': '10/min'},
                    'premium': {'price': 'Contact', 'requests': 'Higher limits'}
                },
                'pros': [
                    'Gratuito para uso básico',
                    'Dados confiáveis',
                    'Fácil de usar'
                ],
                'cons': [
                    'Dados limitados',
                    'Sem estatísticas ao vivo',
                    'Poucas ligas disponíveis'
                ]
            },
            'sportmonks': {
                'name': 'Sportmonks',
                'website': 'https://www.sportmonks.com/',
                'documentation': 'https://docs.sportmonks.com/',
                'free_tier': {
                    'requests_per_hour': 180,
                    'requests_per_day': 'Limited',
                    'features': ['Basic data', 'Limited endpoints']
                },
                'paid_plans': {
                    'starter': {'price': '$15/month', 'requests': '1000/day'},
                    'basic': {'price': '$35/month', 'requests': '3000/day'},
                    'standard': {'price': '$75/month', 'requests': '10000/day'}
                },
                'pros': [
                    'Muitas ligas',
                    'Dados históricos extensos',
                    'Boa documentação'
                ],
                'cons': [
                    'Mais caro',
                    'Interface complexa'
                ]
            }
        }
    
    def display_apis_comparison(self):
        """Exibe comparação das APIs"""
        
        print("🔍 COMPARAÇÃO DE APIs DE FUTEBOL")
        print("=" * 70)
        
        for api_key, api_info in self.apis_info.items():
            print(f"\n📡 {api_info['name']}")
            print(f"🌐 Website: {api_info['website']}")
            
            print(f"\n💰 Plano Gratuito:")
            free = api_info['free_tier']
            if 'requests_per_day' in free:
                print(f"   • {free['requests_per_day']} requests/dia")
            if 'requests_per_minute' in free:
                print(f"   • {free['requests_per_minute']} requests/minuto")
            if 'requests_per_hour' in free:
                print(f"   • {free['requests_per_hour']} requests/hora")
            
            print(f"   • Features: {', '.join(free['features'])}")
            
            print(f"\n✅ Prós:")
            for pro in api_info['pros']:
                print(f"   • {pro}")
            
            print(f"\n❌ Contras:")
            for con in api_info['cons']:
                print(f"   • {con}")
            
            print("-" * 50)
    
    def test_api_football(self, api_key: str) -> Dict:
        """Testa conexão com API-Football"""
        
        print(f"\n🧪 Testando API-Football...")
        
        if not api_key:
            return {'success': False, 'error': 'API key não fornecida'}
        
        headers = {
            'x-apisports-key': api_key,
            'x-apisports-host': 'v3.football.api-sports.io'
        }
        
        tests = []
        
        # Teste 1: Status da API
        try:
            response = requests.get(
                'https://v3.football.api-sports.io/status',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                tests.append({
                    'test': 'Status da API',
                    'success': True,
                    'data': data.get('response', {})
                })
            else:
                tests.append({
                    'test': 'Status da API',
                    'success': False,
                    'error': f'Status code: {response.status_code}'
                })
        except Exception as e:
            tests.append({
                'test': 'Status da API',
                'success': False,
                'error': str(e)
            })
        
        # Teste 2: Ligas disponíveis
        try:
            response = requests.get(
                'https://v3.football.api-sports.io/leagues',
                headers=headers,
                params={'current': 'true'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                leagues = data.get('response', [])
                tests.append({
                    'test': 'Ligas disponíveis',
                    'success': True,
                    'data': f'{len(leagues)} ligas encontradas'
                })
            else:
                tests.append({
                    'test': 'Ligas disponíveis',
                    'success': False,
                    'error': f'Status code: {response.status_code}'
                })
        except Exception as e:
            tests.append({
                'test': 'Ligas disponíveis',
                'success': False,
                'error': str(e)
            })
        
        # Teste 3: Partidas ao vivo
        try:
            response = requests.get(
                'https://v3.football.api-sports.io/fixtures',
                headers=headers,
                params={'live': 'all'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                fixtures = data.get('response', [])
                tests.append({
                    'test': 'Partidas ao vivo',
                    'success': True,
                    'data': f'{len(fixtures)} partidas ao vivo'
                })
            else:
                tests.append({
                    'test': 'Partidas ao vivo',
                    'success': False,
                    'error': f'Status code: {response.status_code}'
                })
        except Exception as e:
            tests.append({
                'test': 'Partidas ao vivo',
                'success': False,
                'error': str(e)
            })
        
        # Exibir resultados
        print(f"\n📊 Resultados dos testes:")
        success_count = 0
        
        for test in tests:
            status = "✅" if test['success'] else "❌"
            print(f"   {status} {test['test']}")
            
            if test['success']:
                success_count += 1
                if 'data' in test:
                    print(f"      {test['data']}")
            else:
                print(f"      Erro: {test['error']}")
        
        overall_success = success_count == len(tests)
        
        return {
            'success': overall_success,
            'tests': tests,
            'success_rate': f"{success_count}/{len(tests)}"
        }
    
    def generate_setup_instructions(self) -> str:
        """Gera instruções de configuração"""
        
        instructions = """# GUIA DE CONFIGURAÇÃO DE APIs

## 🎯 Recomendação: API-Football

### Passo 1: Criar Conta
1. Acesse: https://www.api-football.com/
2. Clique em "Sign Up"
3. Preencha os dados e confirme email
4. Faça login na sua conta

### Passo 2: Obter API Key
1. Acesse o dashboard
2. Vá em "My Account" > "API Key"
3. Copie sua chave (formato: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)

### Passo 3: Configurar no Sistema
```python
# Método 1: Variável de ambiente
export FOOTBALL_API_KEY='sua_chave_aqui'

# Método 2: Direto no código
api_key = 'sua_chave_aqui'
system = EnhancedRealTimePredictionSystem(api_key=api_key)
```

### Passo 4: Testar Conexão
```python
from api_setup_guide import APISetupGuide

guide = APISetupGuide()
result = guide.test_api_football('sua_chave_aqui')
print(result)
```

## 📊 Limites do Plano Gratuito

- **100 requests/dia**
- **10 requests/minuto**
- Acesso a todas as features
- Dados ao vivo incluídos

## 💡 Dicas de Otimização

1. **Cache inteligente**: Sistema já implementado
2. **Rate limiting**: Respeitado automaticamente
3. **Fallback**: Dados simulados quando API falha
4. **Monitoramento**: Acompanhe uso no dashboard

## 🚀 Upgrade para Plano Pago

Se precisar de mais requests:
- **Basic**: $10/mês - 1000 requests/dia
- **Pro**: $25/mês - 5000 requests/dia
- **Ultra**: $50/mês - 15000 requests/dia

## 🔧 APIs Alternativas

### Football-Data.org (Gratuito)
- Mais limitado, mas gratuito
- Bom para testes iniciais
- Configure: `X-Auth-Token: YOUR_TOKEN`

### Sportmonks (Profissional)
- Mais caro, mas muito completo
- Ideal para uso comercial
- Planos a partir de $15/mês

## ⚠️ Troubleshooting

### Erro 401 (Unauthorized)
- Verifique se a API key está correta
- Confirme se a conta está ativa

### Erro 429 (Rate Limit)
- Aguarde 1 minuto antes de tentar novamente
- Considere upgrade do plano

### Erro 403 (Forbidden)
- Endpoint pode não estar disponível no plano gratuito
- Verifique documentação da API

### Sem dados ao vivo
- Nem sempre há partidas acontecendo
- Teste em horários de jogos (fins de semana)

## 📞 Suporte

- Documentação: https://www.api-football.com/documentation-v3
- Suporte: https://www.api-football.com/contact
- Status: https://status.api-football.com/
"""
        
        return instructions
    
    def create_configuration_file(self, api_key: str, filename: str = "api_config.json"):
        """Cria arquivo de configuração"""
        
        config = {
            'api_football': {
                'api_key': api_key,
                'base_url': 'https://v3.football.api-sports.io',
                'enabled': True
            },
            'settings': {
                'update_interval': 30,
                'cache_duration': 300,
                'max_retries': 3,
                'timeout': 10
            },
            'created_at': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Arquivo de configuração criado: {filename}")
        
        return config

def demo_api_setup():
    """Demonstração do guia de configuração"""
    print("🔧 GUIA DE CONFIGURAÇÃO DE APIs")
    print("=" * 70)
    
    guide = APISetupGuide()
    
    # Exibir comparação
    guide.display_apis_comparison()
    
    # Gerar instruções
    instructions = guide.generate_setup_instructions()
    
    with open('api_setup_instructions.md', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"\n📄 Instruções salvas: api_setup_instructions.md")
    
    # Teste com API key (se fornecida)
    api_key = input("\n🔑 Digite sua API key da API-Football (ou Enter para pular): ").strip()
    
    if api_key:
        result = guide.test_api_football(api_key)
        
        if result['success']:
            print(f"\n✅ API configurada com sucesso!")
            
            # Criar arquivo de configuração
            guide.create_configuration_file(api_key)
            
            print(f"\n🚀 Próximos passos:")
            print(f"   1. Use a API key no sistema de predição")
            print(f"   2. Execute: python3 real_time_api_integration.py")
            print(f"   3. Configure monitoramento automático")
        else:
            print(f"\n❌ Problemas na configuração da API")
            print(f"   Taxa de sucesso: {result['success_rate']}")
            print(f"   Verifique as instruções em api_setup_instructions.md")
    else:
        print(f"\n💡 Para configurar a API:")
        print(f"   1. Leia as instruções em api_setup_instructions.md")
        print(f"   2. Obtenha uma API key gratuita")
        print(f"   3. Execute este script novamente")
    
    return guide

if __name__ == "__main__":
    demo_api_setup()

