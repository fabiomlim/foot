# GUIA DE INSTALAÇÃO NO HOSTINGER

## 🎯 Pré-requisitos

### Tipo de Hospedagem Necessária
- ✅ **VPS Hostinger** (Recomendado)
- ✅ **Cloud Hosting** (Alternativa)
- ❌ **Hospedagem Compartilhada** (Não suporta Python)

### Verificar Suporte Python
1. Acesse o painel Hostinger
2. Vá em "Avançado" > "SSH Access"
3. Se disponível, você tem VPS/Cloud
4. Se não disponível, precisa fazer upgrade

## 📦 Passo 1: Upload dos Arquivos

### Via File Manager (Recomendado)
1. Acesse o painel Hostinger
2. Vá em "File Manager"
3. Navegue até `public_html/`
4. Crie pasta `football_prediction/`
5. Upload do arquivo `hostinger_deployment.zip`
6. Extrair arquivos na pasta

### Via FTP
1. Use FileZilla ou similar
2. Conecte com credenciais FTP
3. Navegue até `/public_html/`
4. Upload dos arquivos

## 🔧 Passo 2: Configuração SSH

### Acessar via SSH
```bash
ssh username@your-server-ip
cd public_html/football_prediction/
```

### Verificar Python
```bash
python3 --version
pip3 --version
```

### Instalar Dependências
```bash
chmod +x start.sh
./start.sh
```

## ⚙️ Passo 3: Configuração da API

### Editar Configuração
```bash
nano hostinger_config.json
```

### Adicionar API Key
```json
{
  "api": {
    "api_key": "SUA_CHAVE_AQUI"
  }
}
```

### Obter API Key Gratuita
1. Acesse: https://www.api-football.com/
2. Registre-se gratuitamente
3. Copie sua API key
4. Cole no arquivo de configuração

## 🚀 Passo 4: Iniciar Sistema

### Método 1: Comando Direto
```bash
python3 hostinger_app.py
```

### Método 2: Background (Recomendado)
```bash
nohup python3 hostinger_app.py > app.log 2>&1 &
```

### Verificar se está Rodando
```bash
ps aux | grep python
```

## 🌐 Passo 5: Configurar Domínio

### Subdomain (Recomendado)
1. Painel Hostinger > "Subdomains"
2. Criar: `predictions.seudominio.com`
3. Apontar para pasta `football_prediction`

### Domain Principal
1. Editar DNS se necessário
2. Configurar SSL (automático no Hostinger)

## 📊 Passo 6: Testar Sistema

### Acessar Dashboard
```
http://predictions.seudominio.com
```

### Testar API
```
http://predictions.seudominio.com/api/status
```

### Verificar Logs
```bash
tail -f app.log
```

## 🔧 Troubleshooting

### Erro: Python não encontrado
```bash
# Verificar versões disponíveis
ls /usr/bin/python*

# Usar versão específica
/usr/bin/python3.8 hostinger_app.py
```

### Erro: Permissões
```bash
chmod 755 *.py
chmod 644 *.json
chmod 644 *.db
```

### Erro: Porta em uso
```bash
# Verificar processos
netstat -tulpn | grep :5000

# Matar processo
kill -9 PID_NUMBER
```

### Erro: Dependências
```bash
# Instalar manualmente
pip3 install --user flask flask-cors requests pandas numpy scikit-learn
```

## 🔄 Manutenção

### Backup Automático
- Sistema faz backup a cada 2 horas
- Arquivos salvos em `backups/`

### Logs
- `app.log` - Log principal
- `logs/` - Logs detalhados

### Atualização
1. Fazer backup dos dados
2. Upload novos arquivos
3. Reiniciar sistema

### Monitoramento
- Dashboard web mostra status
- Health checks automáticos
- Alertas por email (configurar)

## 📞 Suporte

### Hostinger
- Documentação: https://support.hostinger.com/
- Chat: Disponível 24/7
- Ticket: Via painel

### Sistema
- Logs em `app.log`
- Status em `/api/status`
- Configuração em `hostinger_config.json`

## 💡 Dicas de Performance

### Otimização
1. Use cache Redis se disponível
2. Configure CDN no Hostinger
3. Ative compressão Gzip
4. Monitore uso de recursos

### Escalabilidade
1. Upgrade para VPS maior se necessário
2. Use Load Balancer para múltiplas instâncias
3. Configure banco PostgreSQL para produção

## 🔒 Segurança

### Configurações Básicas
1. Mantenha API keys seguras
2. Use HTTPS (SSL automático)
3. Configure firewall se VPS
4. Backup regular dos dados

### Monitoramento
1. Verifique logs regularmente
2. Configure alertas de erro
3. Monitore uso de recursos
4. Atualize dependências

---

## ✅ Checklist Final

- [ ] VPS/Cloud Hostinger configurado
- [ ] Python 3.8+ instalado
- [ ] Dependências instaladas
- [ ] API key configurada
- [ ] Sistema iniciado
- [ ] Dashboard acessível
- [ ] API funcionando
- [ ] SSL configurado
- [ ] Backup funcionando
- [ ] Logs sendo gerados

**🎉 Sistema pronto para produção!**
