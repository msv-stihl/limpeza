#!/bin/bash

# Script de instalação para VM Linux
# Execute este script como root ou com sudo

echo "Instalando dependências..."

# Atualizar sistema
apt update
apt upgrade -y

# Instalar Python e pip
apt install -y python3 python3-pip

# Instalar Chrome/Chromium para Selenium
apt install -y chromium-browser

# Instalar dependências Python
pip3 install selenium pandas openpyxl requests python-dotenv

# Instalar ChromeDriver
apt install -y chromium-chromedriver

# Criar diretório do projeto
mkdir -p /opt/limpeza
cp -r * /opt/limpeza/
cd /opt/limpeza

# Configurar permissões
chmod +x coletor_selenium.py
chown -R root:root /opt/limpeza

# Configurar cron para executar a cada 30 minutos
echo "*/30 * * * * cd /opt/limpeza && python3 coletor_selenium.py >> /var/log/coletor.log 2>&1" > /tmp/cron_limpeza
crontab /tmp/cron_limpeza
rm /tmp/cron_limpeza

echo "Instalação concluída!"
echo "O coletor será executado automaticamente a cada 30 minutos."
echo "Logs disponíveis em: /var/log/coletor.log"
echo "Arquivos do projeto em: /opt/limpeza"