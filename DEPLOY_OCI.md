# Guia de Deploy na VM Linux (OCI)

Guia completo para transferir e configurar o sistema de limpeza na sua VM Linux da Oracle Cloud Infrastructure.

## 🚀 Passo a Passo Completo

### 1. Preparação da VM Linux (Limpeza)

```bash
# Conectar na VM
ssh -i sua_chave.pem opc@ip_da_vm

# Atualizar sistema
sudo yum update -y  # Para Oracle Linux/CentOS
# OU
sudo apt update && sudo apt upgrade -y  # Para Ubuntu

# Limpar arquivos desnecessários
sudo yum clean all  # Oracle Linux/CentOS
# OU
sudo apt autoremove && sudo apt autoclean  # Ubuntu

# Remover arquivos temporários
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*

# Limpar logs antigos (opcional)
sudo journalctl --vacuum-time=7d

# Verificar espaço disponível
df -h
```

### 2. Instalação de Dependências na VM

```bash
# Para Oracle Linux/CentOS
sudo yum install -y python3 python3-pip git curl wget

# Para Ubuntu
sudo apt install -y python3 python3-pip python3-venv git curl wget

# Verificar instalação
python3 --version
pip3 --version
git --version
```

### 3. Transferência dos Arquivos

#### Opção A: Via SCP (Recomendado)

```bash
# No seu computador Windows (PowerShell)
# Navegar até a pasta do projeto
cd "C:\Users\manserv\OneDrive - MANSERV\Área de Trabalho\Projetos_Wesley\limpeza"

# Criar arquivo compactado (excluindo arquivos desnecessários)
Compress-Archive -Path @(
    "*.py",
    "*.sh", 
    "*.txt",
    "*.md",
    ".env.example",
    ".gitignore",
    "frontend"
) -DestinationPath "limpeza_deploy.zip"

# Transferir para a VM
scp -i sua_chave.pem limpeza_deploy.zip opc@ip_da_vm:~/
```

#### Opção B: Via Git (Se tiver repositório)

```bash
# Na VM Linux
git clone https://github.com/seu-usuario/limpeza.git
cd limpeza
```

#### Opção C: Via SFTP

```bash
# Usar WinSCP ou FileZilla para transferir os arquivos
# Conectar com:
# Host: ip_da_vm
# Usuário: opc
# Chave privada: sua_chave.pem
```

### 4. Configuração na VM Linux

```bash
# Conectar na VM
ssh -i sua_chave.pem opc@ip_da_vm

# Se usou SCP, extrair arquivos
cd ~
unzip limpeza_deploy.zip -d limpeza
cd limpeza

# Tornar scripts executáveis
chmod +x *.sh

# Executar instalação automática
./install_linux.sh
```

### 5. Configuração do Ambiente

```bash
# Editar arquivo de configuração
nano .env
```

```env
# Configurações do sistema Pro Manserv
PRO_USER=wesley.luz@manserv.com.br
PRO_PASS=028885

# Configurações do GitHub (opcional)
GITHUB_TOKEN=seu_token_github
GITHUB_REPO=msv-stihl/limpeza

# Configurações de logging
LOG_LEVEL=INFO
```

### 6. Transferência de Dados Existentes (Opcional)

```bash
# No Windows, transferir dados existentes
scp -i sua_chave.pem "C:\Users\manserv\OneDrive - MANSERV\Área de Trabalho\Projetos_Wesley\limpeza\backend\exportacao.xlsx" opc@ip_da_vm:~/limpeza/
scp -i sua_chave.pem "C:\Users\manserv\OneDrive - MANSERV\Área de Trabalho\Projetos_Wesley\limpeza\backend\cronograma_lc.xlsx" opc@ip_da_vm:~/limpeza/
```

### 7. Teste do Sistema

```bash
# Na VM, testar o sistema
cd ~/limpeza

# Ativar ambiente virtual
source venv/bin/activate

# Executar testes
python3 test_system.py

# Testar coleta
./run.sh --action status
./run.sh --action collect --no-git
```

### 8. Configuração do Cron

```bash
# Configurar agendamento automático
./setup_cron.sh

# Escolher opção (recomendado: opção 4 - 3x por dia)
# Verificar configuração
crontab -l
```

### 9. Configuração de Firewall (Se necessário)

```bash
# Para servir a interface web (opcional)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# OU para Ubuntu
sudo ufw allow 8000
```

### 10. Monitoramento

```bash
# Verificar logs em tempo real
tail -f ~/limpeza/limpeza_coletor.log

# Verificar logs do cron
tail -f ~/limpeza/cron.log

# Verificar status do sistema
./run.sh --action status
```

## 🔧 Script de Deploy Automatizado

Crie este script para automatizar todo o processo:

```bash
#!/bin/bash
# deploy_oci.sh - Script de deploy automatizado

set -e

echo "=== Deploy do Sistema de Limpeza na OCI ==="

# Variáveis (ajuste conforme necessário)
VM_IP="seu_ip_da_vm"
KEY_PATH="caminho/para/sua_chave.pem"
USER="opc"

# Função para executar comandos na VM
exec_remote() {
    ssh -i "$KEY_PATH" "$USER@$VM_IP" "$1"
}

# 1. Preparar VM
echo "Preparando VM..."
exec_remote "sudo yum update -y && sudo yum install -y python3 python3-pip git curl"

# 2. Transferir arquivos
echo "Transferindo arquivos..."
scp -i "$KEY_PATH" limpeza_deploy.zip "$USER@$VM_IP:~/"

# 3. Configurar sistema
echo "Configurando sistema..."
exec_remote "cd ~ && unzip -o limpeza_deploy.zip -d limpeza && cd limpeza && chmod +x *.sh && ./install_linux.sh"

# 4. Configurar cron (automático)
echo "Configurando cron..."
exec_remote "cd ~/limpeza && echo '4' | ./setup_cron.sh"

echo "Deploy concluído! Acesse a VM para verificar:"
echo "ssh -i $KEY_PATH $USER@$VM_IP"
echo "cd ~/limpeza && ./run.sh --action status"
```

## 📊 Verificação Pós-Deploy

### Checklist de Verificação

```bash
# 1. Sistema funcionando
./run.sh --action status

# 2. Cron configurado
crontab -l

# 3. Logs sendo gerados
ls -la *.log

# 4. Conectividade
curl -I https://pro.manserv.com.br

# 5. Espaço em disco
df -h

# 6. Processos Python
ps aux | grep python
```

### Interface Web (Opcional)

```bash
# Servir interface web
cd ~/limpeza/frontend
python3 -m http.server 8000 &

# Acessar via navegador:
# http://ip_da_vm:8000
```

## 🚨 Solução de Problemas

### Problema: Conexão SSH negada
```bash
# Verificar se a chave tem permissões corretas
chmod 600 sua_chave.pem

# Verificar se o IP está correto
ping ip_da_vm
```

### Problema: Falta de espaço
```bash
# Limpar espaço na VM
sudo rm -rf /tmp/*
sudo journalctl --vacuum-size=100M
docker system prune -a  # Se tiver Docker
```

### Problema: Dependências Python
```bash
# Reinstalar dependências
cd ~/limpeza
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Problema: Firewall bloqueando
```bash
# Oracle Linux
sudo firewall-cmd --list-all
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload

# Ubuntu
sudo ufw status
sudo ufw allow 8000
```

## 📈 Otimizações para OCI

### 1. Configuração de Swap (Se necessário)
```bash
# Criar arquivo de swap de 2GB
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Tornar permanente
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 2. Configuração de Timezone
```bash
# Configurar timezone do Brasil
sudo timedatectl set-timezone America/Sao_Paulo
timedatectl status
```

### 3. Configuração de Logs
```bash
# Configurar rotação de logs
sudo tee /etc/logrotate.d/limpeza << EOF
/home/opc/limpeza/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF
```

## 🎯 Comandos Úteis

```bash
# Verificar status completo
./run.sh --action status

# Executar coleta manual
./run.sh --action full

# Verificar logs
tail -f limpeza_coletor.log

# Verificar cron
crontab -l
sudo tail -f /var/log/cron

# Reiniciar serviços se necessário
sudo systemctl restart crond  # Oracle Linux
sudo systemctl restart cron   # Ubuntu

# Verificar conectividade
curl -v https://pro.manserv.com.br

# Monitorar recursos
top
htop  # Se instalado
df -h
free -h
```

---

**🎉 Seu sistema está pronto para rodar na OCI!**

Após seguir este guia, você terá:
- ✅ Sistema funcionando na VM Linux
- ✅ Coleta automática via cron
- ✅ Logs organizados
- ✅ Sincronização com GitHub
- ✅ Interface web acessível

**Próximo passo**: Monitore os logs e verifique se as coletas estão funcionando corretamente!