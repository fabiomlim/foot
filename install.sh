#!/bin/bash
# Instalador de uma linha para Hostinger
# Execute: curl -sSL https://seu-dominio.com/install.sh | bash

echo "🚀 FOOTBALL PREDICTION SYSTEM - INSTALADOR HOSTINGER"
echo "=" * 60

# Verificar ambiente
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Certifique-se de ter VPS/Cloud Hostinger."
    exit 1
fi

echo "✅ Python3 encontrado: $(python3 --version)"

# Verificar se arquivos existem
if [ ! -f "hostinger_quick_setup.py" ]; then
    echo "❌ Arquivos não encontrados. Faça upload do pacote primeiro."
    exit 1
fi

echo "✅ Arquivos encontrados"

# Executar instalação
echo "🔧 Iniciando instalação automática..."
python3 hostinger_quick_setup.py

# Verificar resultado
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 INSTALAÇÃO CONCLUÍDA!"
    echo ""
    echo "🚀 Para iniciar o sistema:"
    echo "   ./start_system.sh"
    echo ""
    echo "🌐 Dashboard estará disponível em:"
    echo "   http://seu-dominio.com"
    echo ""
    echo "📊 API disponível em:"
    echo "   http://seu-dominio.com/api/status"
    echo ""
else
    echo ""
    echo "❌ Instalação falhou. Verifique os logs acima."
    echo "📄 Consulte: INSTALACAO_HOSTINGER.md"
    echo ""
fi
