# Instalação do Coletor de Limpeza na VM

## Arquivos Essenciais

Após a limpeza, os arquivos essenciais para transferir para a VM são:

- `coletor_selenium.py` - Script principal do coletor
- `git_manager.py` - Gerenciador de uploads para GitHub
- `.env` - Variáveis de ambiente (configurar credenciais)
- `install.sh` - Script de instalação automática
- `backend/` - Pasta com arquivos do backend (se necessário)

## Pré-requisitos na VM

- Sistema Linux (Ubuntu/Debian recomendado)
- Acesso root ou sudo
- Conexão com internet

## Instalação

### Método 1: Instalação Automática

1. Transfira todos os arquivos para a VM
2. Execute o script de instalação:
   ```bash
   chmod +x install.sh
   sudo ./install.sh
   ```

### Método 2: Instalação Manual

1. **Instalar dependências:**
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip chromium-browser chromium-chromedriver
   pip3 install selenium pandas openpyxl requests python-dotenv
   ```

2. **Configurar projeto:**
   ```bash
   sudo mkdir -p /opt/limpeza
   sudo cp -r * /opt/limpeza/
   sudo chmod +x /opt/limpeza/coletor_selenium.py
   ```

3. **Configurar cron:**
   ```bash
   sudo crontab -e
   # Adicionar linha:
   */30 * * * * cd /opt/limpeza && python3 coletor_selenium.py >> /var/log/coletor.log 2>&1
   ```

## Configuração do .env

Antes de executar, configure as variáveis no arquivo `.env`:

```
GITHUB_TOKEN=seu_token_aqui
GITHUB_REPO=seu_repositorio
GITHUB_USERNAME=seu_usuario
MSPRO_URL=url_do_mspro
MSPRO_USERNAME=usuario_mspro
MSPRO_PASSWORD=senha_mspro
```

## Verificação

- **Logs do cron:** `tail -f /var/log/coletor.log`
- **Logs do aplicativo:** `tail -f /opt/limpeza/coletor_selenium.log`
- **Status do cron:** `sudo crontab -l`

## Funcionalidades

- ✅ Coleta automática de dados a cada 30 minutos
- ✅ Validação de horários por turno
- ✅ Geração de faltando.json com colunas corretas
- ✅ Upload automático para GitHub
- ✅ Limpeza de arquivos temporários
- ✅ Logs detalhados

## Troubleshooting

- Se o Chrome não funcionar, instale: `sudo apt install google-chrome-stable`
- Para problemas de permissão: `sudo chown -R root:root /opt/limpeza`
- Para verificar se o cron está rodando: `sudo systemctl status cron`