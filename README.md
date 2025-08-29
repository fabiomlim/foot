# ⚽ Football Prediction System - Hostinger Deploy

Sistema completo de predições de futebol em tempo real para Hostinger.

## 🚀 Instalação Rápida (1 comando)

```bash
python3 hostinger_quick_setup.py
```

## 📋 Pré-requisitos

- ✅ **Hostinger VPS** ou **Cloud Hosting**
- ✅ **Python 3.8+** (já incluído no VPS/Cloud)
- ✅ **Acesso SSH** (disponível no painel)
- ❌ **Hospedagem Compartilhada** (não suporta Python)

## 📦 Conteúdo do Pacote

### Arquivos Principais
- `hostinger_app.py` - Aplicação Flask principal
- `real_time_api_integration.py` - Sistema de predição
- `simplified_ml_training.py` - Treinamento de modelos
- `hostinger_quick_setup.py` - **Instalador automático**

### Configuração
- `hostinger_config.json` - Configurações do sistema
- `requirements.txt` - Dependências Python
- `.htaccess` - Configuração Apache
- `start.sh` - Script de inicialização

### Documentação
- `INSTALACAO_HOSTINGER.md` - Guia completo
- `README.md` - Este arquivo
- `VERSION.json` - Informações da versão

### Dados (se incluídos)
- `models/` - Modelos de ML treinados
- `football_data.db` - Banco de dados

## ⚡ Instalação Express

### 1. Upload
- Faça upload do ZIP no File Manager
- Extraia na pasta `public_html/football/`

### 2. SSH
```bash
ssh seu-usuario@seu-servidor
cd public_html/football/
```

### 3. Instalação Automática
```bash
python3 hostinger_quick_setup.py
```

### 4. Iniciar Sistema
```bash
./start_system.sh
```

### 5. Acessar
```
http://seu-dominio.com/football/
```

## 🔧 Configuração Manual

Se preferir configurar manualmente, siga o guia completo:
`INSTALACAO_HOSTINGER.md`

## 🔑 API Configuration

### Gratuita (Recomendada)
1. Registre-se: https://www.api-football.com/
2. Copie sua API key
3. Edite: `hostinger_config.json`
4. Substitua: `"api_key": "SUA_CHAVE_AQUI"`

### Sem API
O sistema funciona com dados simulados se não configurar API.

## 📊 Features

- ✅ **Predições em tempo real** (1X2, Over/Under, BTTS)
- ✅ **Value betting** com odds reais
- ✅ **Dashboard web** responsivo
- ✅ **API REST** completa
- ✅ **Monitoramento automático**
- ✅ **Backup automático**
- ✅ **Logs detalhados**

## 🎯 Comandos Úteis

```bash
# Iniciar sistema
./start_system.sh

# Parar sistema
./stop_system.sh

# Ver logs
tail -f app.log

# Status
curl http://localhost:5000/api/status

# Verificar processo
ps aux | grep python
```

## 📞 Suporte

### Hostinger
- **Chat 24/7**: Disponível no painel
- **Documentação**: https://support.hostinger.com/
- **Tutoriais**: YouTube Hostinger

### Sistema
- **Logs**: Verifique `app.log`
- **Status**: `/api/status`
- **Configuração**: `hostinger_config.json`

## 🔄 Atualizações

Para atualizar o sistema:
1. Faça backup dos dados
2. Substitua arquivos Python
3. Execute: `python3 hostinger_quick_setup.py`
4. Reinicie: `./start_system.sh`

## ⚠️ Troubleshooting

### Sistema não inicia
```bash
# Verificar Python
python3 --version

# Verificar dependências
pip3 list

# Reinstalar
python3 hostinger_quick_setup.py
```

### Erro de permissões
```bash
chmod 755 *.py *.sh
chmod 644 *.json *.md
```

### Porta ocupada
```bash
# Verificar processos
netstat -tulpn | grep :5000

# Matar processo
pkill -f hostinger_app.py
```

## 📈 Performance

### Recursos Mínimos
- **RAM**: 512MB
- **CPU**: 1 core
- **Storage**: 1GB
- **Bandwidth**: Ilimitado

### Otimizações
- Cache automático (10 min)
- Compressão Gzip
- Logs rotativos
- Cleanup automático

## 🔒 Segurança

- ✅ HTTPS automático (Hostinger)
- ✅ API keys protegidas
- ✅ Arquivos sensíveis bloqueados
- ✅ Logs de auditoria

---

## 🎉 Pronto para Produção!

Este sistema está otimizado para Hostinger e pronto para uso em produção.

**Tempo de instalação**: ~5 minutos  
**Configuração**: Automática  
**Suporte**: Incluído  

**Boa sorte com suas predições! ⚽💰**
