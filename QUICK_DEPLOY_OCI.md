# 🚀 Deploy Rápido na OCI - Guia Prático

## 📋 Pré-requisitos

- VM Linux rodando na OCI
- Chave SSH configurada
- IP público da VM
- OpenSSH Client instalado no Windows

## 🎯 Opção 1: Deploy Automático (Recomendado)

### No Windows (PowerShell):

```powershell
# Navegar para o diretório do projeto
cd "C:\Users\manserv\OneDrive - MANSERV\Área de Trabalho\Projetos_Wesley\limpeza"

# Executar deploy automático
.\deploy_to_oci.ps1 -VMIp "SEU_IP_DA_VM" -KeyPath "C:\caminho\para\sua\chave.pem"

# Exemplo:
.\deploy_to_oci.ps1 -VMIp "129.159.1.100" -KeyPath "C:\Users\manserv\oci_key.pem"
```

### O script fará automaticamente:
- ✅ Teste de conectividade
- ✅ Instalação de dependências na VM
- ✅ Transferência de todos os arquivos
- ✅ Configuração do ambiente
- ✅ Instalação do sistema
- ✅ Configuração do cron
- ✅ Testes do sistema

---

## 🎯 Opção 2: Deploy Manual

### 1. Conectar na VM:
```bash
ssh -i "sua_chave.pem" opc@SEU_IP_DA_VM
```

### 2. Preparar a VM:
```bash
# Download do script de preparação
wget https://raw.githubusercontent.com/seu-repo/limpeza/main/clean_and_setup_vm.sh
chmod +x clean_and_setup_vm.sh
./clean_and_setup_vm.sh
```

### 3. Transferir arquivos (do Windows):
```powershell
# Compactar projeto
Compress-Archive -Path "*" -DestinationPath "limpeza.zip"

# Transferir
scp -i "sua_chave.pem" "limpeza.zip" opc@SEU_IP_DA_VM:~/
```

### 4. Na VM, extrair e instalar:
```bash
cd ~
unzip limpeza.zip -d limpeza
cd limpeza
chmod +x *.sh
./install_linux.sh
```

---

## 🎯 Opção 3: Deploy via Git

### 1. Fazer push do projeto para GitHub:
```powershell
# No Windows
git add .
git commit -m "Preparação para deploy OCI"
git push origin main
```

### 2. Na VM, clonar:
```bash
ssh -i "sua_chave.pem" opc@SEU_IP_DA_VM
git clone https://github.com/seu-usuario/seu-repo.git limpeza
cd limpeza
./install_linux.sh
```

---

## ⚙️ Configuração Pós-Deploy

### 1. Configurar credenciais:
```bash
cd ~/limpeza
nano .env

# Editar:
PRO_MANSERV_USER=seu_usuario
PRO_MANSERV_PASS=sua_senha
GITHUB_TOKEN=seu_token_opcional
GITHUB_REPO=seu_repo_opcional
```

### 2. Testar sistema:
```bash
./run.sh --action status
python3 test_system.py
```

### 3. Configurar agendamento:
```bash
./setup_cron.sh
# Escolha opção 4 (a cada 2 horas) - recomendado
```

### 4. Verificar logs:
```bash
tail -f logs/limpeza_coletor.log
tail -f cron.log
```

---

## 🔧 Comandos Úteis na VM

### Monitoramento:
```bash
# Status do sistema
./run.sh --action status

# Executar coleta manual
./run.sh --action collect

# Sincronizar com Git
./run.sh --action sync

# Execução completa
./run.sh --action full

# Ver logs em tempo real
tail -f logs/*.log

# Verificar cron jobs
crontab -l

# Status dos processos
htop

# Uso do disco
df -h

# Uso da memória
free -h
```

### Manutenção:
```bash
# Parar todos os processos
pkill -f "python3.*limpeza"

# Limpar logs antigos
find logs/ -name "*.log" -mtime +7 -delete

# Backup da configuração
cp .env .env.backup

# Atualizar sistema
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
sudo yum update -y                       # CentOS/RHEL
```

---

## 🚨 Solução de Problemas

### Erro de conexão SSH:
```bash
# Verificar se a VM está rodando
# Verificar security groups na OCI
# Verificar se a chave SSH está correta
ssh -i "sua_chave.pem" -v opc@SEU_IP_DA_VM
```

### Erro de permissão:
```bash
# Corrigir permissões dos scripts
chmod +x *.sh

# Corrigir permissões da chave SSH (no Windows)
icacls "sua_chave.pem" /inheritance:r /grant:r "%username%:R"
```

### Erro de dependências:
```bash
# Reinstalar dependências
pip3 install -r requirements.txt --force-reinstall

# Ou usar o instalador
./install_linux.sh
```

### Sistema não coleta dados:
```bash
# Verificar credenciais
cat .env

# Testar conectividade
curl -I https://pro.manserv.com.br

# Executar em modo debug
python3 coletor_linux.py
```

---

## 📊 Verificação de Sucesso

✅ **Sistema funcionando se:**
- `./run.sh --action status` não mostra erros críticos
- Arquivo `frontend/faltando.json` é atualizado
- Logs mostram execuções bem-sucedidas
- Cron jobs estão configurados: `crontab -l`

✅ **Arquivos importantes criados:**
- `~/limpeza/exportacao.xlsx`
- `~/limpeza/cronograma_lc.xlsx`
- `~/limpeza/cronograma-lc.db`
- `~/limpeza/frontend/faltando.json`

---

## 🔗 Links Úteis

- **Logs**: `~/limpeza/logs/`
- **Configuração**: `~/limpeza/.env`
- **Frontend**: `~/limpeza/frontend/`
- **Documentação**: `~/limpeza/README.md`

---

## 📞 Suporte

Em caso de problemas:
1. Verificar logs: `tail -f logs/*.log`
2. Executar teste: `python3 test_system.py`
3. Verificar status: `./run.sh --action status`
4. Consultar documentação: `cat README.md`

**Tempo estimado de deploy:** 5-10 minutos
**Recursos necessários:** 1GB RAM, 2GB disco