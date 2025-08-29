#!/usr/bin/env python3
"""
Script de configuração rápida para Hostinger
Execute este script no seu servidor Hostinger após o upload
"""

import os
import sys
import json
import subprocess
import sqlite3
from datetime import datetime

class HostingerQuickSetup:
    """Configuração rápida para Hostinger"""
    
    def __init__(self):
        self.setup_log = []
        self.errors = []
    
    def log(self, message: str, is_error: bool = False):
        """Log de mensagens"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        
        if is_error:
            self.errors.append(log_message)
            print(f"❌ {log_message}")
        else:
            self.setup_log.append(log_message)
            print(f"✅ {log_message}")
    
    def check_environment(self) -> bool:
        """Verifica ambiente Hostinger"""
        print("🔍 VERIFICANDO AMBIENTE HOSTINGER")
        print("=" * 50)
        
        # Verificar Python
        try:
            python_version = subprocess.check_output([sys.executable, '--version'], 
                                                   stderr=subprocess.STDOUT, 
                                                   text=True).strip()
            self.log(f"Python encontrado: {python_version}")
            
            # Verificar se é versão adequada
            version_parts = python_version.split()[1].split('.')
            major, minor = int(version_parts[0]), int(version_parts[1])
            
            if major >= 3 and minor >= 8:
                self.log("Versão do Python adequada")
            else:
                self.log("Versão do Python pode ser inadequada (requer 3.8+)", True)
                
        except Exception as e:
            self.log(f"Erro ao verificar Python: {e}", True)
            return False
        
        # Verificar pip
        try:
            pip_version = subprocess.check_output([sys.executable, '-m', 'pip', '--version'], 
                                                stderr=subprocess.STDOUT, 
                                                text=True).strip()
            self.log(f"pip encontrado: {pip_version}")
        except Exception as e:
            self.log(f"pip não encontrado: {e}", True)
            return False
        
        # Verificar espaço em disco
        try:
            statvfs = os.statvfs('.')
            free_space_mb = (statvfs.f_frsize * statvfs.f_bavail) / (1024 * 1024)
            self.log(f"Espaço livre: {free_space_mb:.1f} MB")
            
            if free_space_mb < 100:
                self.log("Pouco espaço em disco disponível", True)
        except Exception as e:
            self.log(f"Erro ao verificar espaço: {e}", True)
        
        # Verificar permissões
        try:
            test_file = 'test_permissions.tmp'
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            self.log("Permissões de escrita OK")
        except Exception as e:
            self.log(f"Problema com permissões: {e}", True)
            return False
        
        return len(self.errors) == 0
    
    def install_dependencies(self) -> bool:
        """Instala dependências Python"""
        print(f"\n📦 INSTALANDO DEPENDÊNCIAS")
        print("=" * 50)
        
        try:
            # Ler requirements.txt
            if not os.path.exists('requirements.txt'):
                self.log("requirements.txt não encontrado", True)
                return False
            
            with open('requirements.txt', 'r') as f:
                requirements = f.read().strip().split('\n')
            
            self.log(f"Instalando {len(requirements)} pacotes...")
            
            # Instalar com --user para evitar problemas de permissão
            cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade'] + requirements
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.log("Dependências instaladas com sucesso")
                return True
            else:
                self.log(f"Erro na instalação: {result.stderr}", True)
                
                # Tentar instalação individual
                self.log("Tentando instalação individual...")
                success_count = 0
                
                for package in requirements:
                    if package.strip():
                        try:
                            cmd_single = [sys.executable, '-m', 'pip', 'install', package.strip()]
                            result_single = subprocess.run(cmd_single, capture_output=True, text=True, timeout=60)
                            
                            if result_single.returncode == 0:
                                self.log(f"✓ {package}")
                                success_count += 1
                            else:
                                self.log(f"✗ {package}: {result_single.stderr[:100]}", True)
                        except Exception as e:
                            self.log(f"✗ {package}: {e}", True)
                
                if success_count >= len(requirements) * 0.8:  # 80% sucesso
                    self.log(f"Instalação parcial OK ({success_count}/{len(requirements)})")
                    return True
                else:
                    return False
                    
        except subprocess.TimeoutExpired:
            self.log("Timeout na instalação de dependências", True)
            return False
        except Exception as e:
            self.log(f"Erro inesperado na instalação: {e}", True)
            return False
    
    def setup_database(self) -> bool:
        """Configura banco de dados"""
        print(f"\n💾 CONFIGURANDO BANCO DE DADOS")
        print("=" * 50)
        
        try:
            # Verificar se banco já existe
            if os.path.exists('football_data.db'):
                self.log("Banco de dados já existe")
                
                # Verificar integridade
                conn = sqlite3.connect('football_data.db')
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                conn.close()
                
                if len(tables) >= 3:  # Esperamos pelo menos 3 tabelas
                    self.log(f"Banco válido com {len(tables)} tabelas")
                    return True
                else:
                    self.log("Banco incompleto, recriando...", True)
            
            # Criar/recriar banco
            self.log("Criando banco de dados...")
            
            # Importar e executar treinamento
            sys.path.append('.')
            from simplified_ml_training import SimplifiedFootballMLTrainer
            
            trainer = SimplifiedFootballMLTrainer()
            data = trainer.prepare_training_data()
            
            if not data.empty:
                self.log(f"Dados preparados: {len(data)} registros")
                trainer.train_models(data)
                trainer.save_models()
                self.log("Modelos treinados e salvos")
                return True
            else:
                self.log("Falha ao preparar dados", True)
                return False
                
        except Exception as e:
            self.log(f"Erro na configuração do banco: {e}", True)
            return False
    
    def configure_api(self) -> bool:
        """Configura API"""
        print(f"\n🔑 CONFIGURANDO API")
        print("=" * 50)
        
        try:
            # Carregar configuração
            config_file = 'hostinger_config.json'
            
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                api_key = config.get('api', {}).get('api_key')
                
                if api_key and api_key != 'None' and len(api_key) > 10:
                    self.log("API key configurada")
                    
                    # Testar API
                    try:
                        import requests
                        headers = {
                            'x-apisports-key': api_key,
                            'x-apisports-host': 'v3.football.api-sports.io'
                        }
                        
                        response = requests.get(
                            'https://v3.football.api-sports.io/status',
                            headers=headers,
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            account = data.get('response', {})
                            requests_remaining = account.get('requests', {}).get('current', 0)
                            self.log(f"API funcionando - {requests_remaining} requests restantes")
                            return True
                        else:
                            self.log(f"API retornou erro: {response.status_code}", True)
                            
                    except Exception as e:
                        self.log(f"Erro ao testar API: {e}", True)
                
                else:
                    self.log("API key não configurada - usando modo simulado")
                    print(f"\n💡 Para configurar API real:")
                    print(f"   1. Obtenha chave gratuita em: https://www.api-football.com/")
                    print(f"   2. Edite o arquivo: {config_file}")
                    print(f"   3. Substitua 'api_key': null por 'api_key': 'SUA_CHAVE'")
                    print(f"   4. Reinicie o sistema")
                    
                return True
                
            else:
                self.log("Arquivo de configuração não encontrado", True)
                return False
                
        except Exception as e:
            self.log(f"Erro na configuração da API: {e}", True)
            return False
    
    def test_system(self) -> bool:
        """Testa sistema"""
        print(f"\n🧪 TESTANDO SISTEMA")
        print("=" * 50)
        
        try:
            # Testar imports
            sys.path.append('.')
            
            try:
                from real_time_api_integration import EnhancedRealTimePredictionSystem
                self.log("Import do sistema de predição OK")
            except Exception as e:
                self.log(f"Erro no import: {e}", True)
                return False
            
            # Testar inicialização
            try:
                system = EnhancedRealTimePredictionSystem(api_key=None)
                self.log("Sistema inicializado com sucesso")
            except Exception as e:
                self.log(f"Erro na inicialização: {e}", True)
                return False
            
            # Testar predição simples
            try:
                test_match = {
                    'fixture': {'id': 999999, 'status': {'elapsed': 45}},
                    'teams': {
                        'home': {'name': 'Test Home'},
                        'away': {'name': 'Test Away'}
                    },
                    'goals': {'home': 1, 'away': 0}
                }
                
                prediction = system.predict_match_enhanced(test_match)
                
                if prediction and hasattr(prediction, 'home_win_prob'):
                    self.log("Predição de teste executada com sucesso")
                    return True
                else:
                    self.log("Predição retornou resultado inválido", True)
                    return False
                    
            except Exception as e:
                self.log(f"Erro na predição de teste: {e}", True)
                return False
                
        except Exception as e:
            self.log(f"Erro no teste do sistema: {e}", True)
            return False
    
    def create_startup_service(self):
        """Cria script de inicialização automática"""
        print(f"\n🚀 CRIANDO SERVIÇO DE INICIALIZAÇÃO")
        print("=" * 50)
        
        try:
            # Script de inicialização
            startup_script = f'''#!/bin/bash
# Script de inicialização automática para Hostinger

cd {os.getcwd()}

# Verificar se já está rodando
if pgrep -f "hostinger_app.py" > /dev/null; then
    echo "Sistema já está rodando"
    exit 0
fi

# Iniciar sistema
echo "Iniciando Football Prediction System..."
nohup {sys.executable} hostinger_app.py > app.log 2>&1 &

# Aguardar inicialização
sleep 5

# Verificar se iniciou
if pgrep -f "hostinger_app.py" > /dev/null; then
    echo "Sistema iniciado com sucesso"
    echo "PID: $(pgrep -f 'hostinger_app.py')"
    echo "Log: tail -f app.log"
    echo "Dashboard: http://seu-dominio.com"
else
    echo "Falha ao iniciar sistema"
    echo "Verifique o log: cat app.log"
    exit 1
fi
'''
            
            with open('start_system.sh', 'w', encoding='utf-8') as f:
                f.write(startup_script)
            
            os.chmod('start_system.sh', 0o755)
            self.log("Script de inicialização criado: start_system.sh")
            
            # Script de parada
            stop_script = '''#!/bin/bash
# Script para parar o sistema

echo "Parando Football Prediction System..."

# Encontrar e matar processo
PID=$(pgrep -f "hostinger_app.py")

if [ ! -z "$PID" ]; then
    kill $PID
    echo "Sistema parado (PID: $PID)"
else
    echo "Sistema não estava rodando"
fi
'''
            
            with open('stop_system.sh', 'w', encoding='utf-8') as f:
                f.write(stop_script)
            
            os.chmod('stop_system.sh', 0o755)
            self.log("Script de parada criado: stop_system.sh")
            
        except Exception as e:
            self.log(f"Erro ao criar scripts: {e}", True)
    
    def generate_summary_report(self):
        """Gera relatório final"""
        print(f"\n📊 RELATÓRIO DE CONFIGURAÇÃO")
        print("=" * 50)
        
        # Estatísticas
        total_steps = len(self.setup_log) + len(self.errors)
        success_rate = (len(self.setup_log) / total_steps * 100) if total_steps > 0 else 0
        
        print(f"✅ Passos concluídos: {len(self.setup_log)}")
        print(f"❌ Erros encontrados: {len(self.errors)}")
        print(f"📈 Taxa de sucesso: {success_rate:.1f}%")
        
        # Status geral
        if len(self.errors) == 0:
            status = "🎉 CONFIGURAÇÃO COMPLETA"
            next_steps = [
                "Execute: ./start_system.sh",
                "Acesse: http://seu-dominio.com",
                "Configure API key se necessário",
                "Monitore logs: tail -f app.log"
            ]
        elif len(self.errors) <= 2:
            status = "⚠️  CONFIGURAÇÃO PARCIAL"
            next_steps = [
                "Resolva os erros listados abaixo",
                "Execute novamente este script",
                "Consulte INSTALACAO_HOSTINGER.md"
            ]
        else:
            status = "❌ CONFIGURAÇÃO FALHOU"
            next_steps = [
                "Verifique se tem VPS/Cloud Hostinger",
                "Confirme que Python 3.8+ está disponível",
                "Entre em contato com suporte Hostinger",
                "Consulte documentação completa"
            ]
        
        print(f"\n{status}")
        
        if self.errors:
            print(f"\n❌ ERROS ENCONTRADOS:")
            for error in self.errors:
                print(f"   {error}")
        
        print(f"\n🎯 PRÓXIMOS PASSOS:")
        for i, step in enumerate(next_steps, 1):
            print(f"   {i}. {step}")
        
        # Salvar relatório
        report = {
            'timestamp': datetime.now().isoformat(),
            'success_rate': success_rate,
            'setup_log': self.setup_log,
            'errors': self.errors,
            'status': status,
            'next_steps': next_steps
        }
        
        with open('setup_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório salvo: setup_report.json")

def main():
    """Função principal"""
    print("🔧 HOSTINGER QUICK SETUP")
    print("=" * 70)
    print("Este script configura automaticamente o Football Prediction System")
    print("no seu servidor Hostinger VPS/Cloud")
    print()
    
    setup = HostingerQuickSetup()
    
    # Executar configuração
    steps = [
        ("Verificar ambiente", setup.check_environment),
        ("Instalar dependências", setup.install_dependencies),
        ("Configurar banco de dados", setup.setup_database),
        ("Configurar API", setup.configure_api),
        ("Testar sistema", setup.test_system)
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name.upper()}")
        print("-" * 50)
        
        try:
            success = step_func()
            if not success:
                setup.log(f"Falha em: {step_name}", True)
                break
        except KeyboardInterrupt:
            print(f"\n⏹️  Configuração interrompida pelo usuário")
            break
        except Exception as e:
            setup.log(f"Erro inesperado em {step_name}: {e}", True)
            break
    
    # Criar scripts de inicialização
    setup.create_startup_service()
    
    # Gerar relatório final
    setup.generate_summary_report()

if __name__ == "__main__":
    main()

