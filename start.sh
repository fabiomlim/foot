#!/bin/bash
# Script de inicialização para Hostinger

echo "🚀 Iniciando Football Prediction System no Hostinger..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado"
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado"
    exit 1
fi

echo "✅ pip3 encontrado"

# Instalar dependências
echo "📦 Instalando dependências..."
pip3 install --user -r requirements.txt

# Verificar se modelos existem
if [ ! -d "models" ]; then
    echo "⚠️  Diretório models não encontrado - executando treinamento..."
    python3 simplified_ml_training.py
fi

# Verificar banco de dados
if [ ! -f "football_data.db" ]; then
    echo "⚠️  Banco de dados não encontrado - criando..."
    python3 -c "
from simplified_ml_training import SimplifiedFootballMLTrainer
trainer = SimplifiedFootballMLTrainer()
trainer.prepare_training_data()
"
fi

echo "✅ Sistema pronto!"
echo "🌐 Para iniciar o servidor: python3 hostinger_app.py"
