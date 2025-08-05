# Coletor de Dados de Limpeza - Versão Linux

Sistema automatizado para coleta de dados de limpeza do sistema Pro Manserv, compatível com Linux e agendamento via cron.

## 📋 Funcionalidades

- ✅ **Coleta automatizada** de dados via HTTP requests (sem Selenium)
- ✅ **Compatibilidade total com Linux** (Ubuntu, CentOS, Debian, etc.)
- ✅ **Agendamento via cron** para execução automática
- ✅ **Sincronização automática** com GitHub
- ✅ **Interface web** para visualização dos dados
- ✅ **Logs detalhados** para monitoramento
- ✅ **Configuração segura** via variáveis de ambiente

## 🚀 Instalação Rápida

### 1. Download e Preparação

```bash
# Clone ou baixe o projeto
git clone <seu-repositorio>
cd limpeza

# Torne os scripts executáveis
chmod +x install_linux.sh setup_cron.sh
```

### 2. Instalação Automática

```bash
# Execute o instalador
./install_linux.sh
```

O instalador irá:
- Detectar sua distribuição Linux
- Instalar dependências do sistema (Python 3, pip, git)
- Criar ambiente virtual Python
- Instalar dependências Python
- Configurar arquivos de ambiente
- Testar a instalação

### 3. Configuração

Edite o arquivo `.env` com suas credenciais:

```bash
nano .env
```

```env
# Configurações do sistema Pro Manserv
PRO_USER=seu_usuario@manserv.com.br
PRO_PASS=sua_senha

# Configurações do GitHub (opcional)
GITHUB_TOKEN=seu_token_github
GITHUB_REPO=msv-stihl/limpeza

# Configurações de logging
LOG_LEVEL=INFO
```

### 4. Configuração do Cron

```bash
# Configure o agendamento automático
./setup_cron.sh
```

## 🔧 Uso Manual

### Comandos Disponíveis

```bash
# Executar processo completo (coleta + sincronização)
./run.sh --action full

# Apenas coleta de dados
./run.sh --action collect

# Apenas sincronização Git
./run.sh --action sync

# Verificar status do sistema
./run.sh --action status

# Executar sem sincronização Git
./run.sh --action full --no-git
```

### Exemplos de Uso

```bash
# Teste inicial
./run.sh --action status

# Coleta manual
./run.sh --action collect

# Processo completo com logs detalhados
./run.sh --action full --log-level DEBUG
```

## 📁 Estrutura do Projeto

```
limpeza/
├── main.py                 # Script principal
├── coletor_linux.py        # Coletor de dados (versão Linux)
├── git_manager.py          # Gerenciador Git
├── requirements.txt        # Dependências Python
├── .env.example           # Exemplo de configuração
├── .env                   # Configurações (criar após instalação)
├── install_linux.sh       # Script de instalação
├── setup_cron.sh          # Configuração do cron
├── run.sh                 # Script de execução (criado na instalação)
├── frontend/              # Interface web
│   ├── index.html
│   ├── faltando.html
│   ├── main.js
│   ├── styles.css
│   └── faltando.json      # Dados gerados
├── downloads/             # Arquivos temporários
├── logs/                  # Logs da aplicação
├── exportacao.xlsx        # Dados exportados
├── cronograma_lc.xlsx     # Cronograma de limpeza
└── cronograma-lc.db       # Banco de dados SQLite
```

## 🕐 Configurações de Agendamento

O script `setup_cron.sh` oferece várias opções:

1. **A cada 30 minutos** - Para testes
2. **A cada hora** - Monitoramento frequente
3. **A cada 2 horas** - Balanceado
4. **3x por dia** (8h, 14h, 20h) - Recomendado
5. **2x por dia** (9h, 18h) - Básico
6. **1x por dia** (9h) - Mínimo
7. **Personalizado** - Defina seu próprio horário

### Exemplo de Configuração Cron

```bash
# Executar 3 vezes por dia
0 8,14,20 * * * cd /caminho/para/limpeza && python3 main.py --action full >> cron.log 2>&1

# Status diário
0 7 * * * cd /caminho/para/limpeza && python3 main.py --action status >> status.log 2>&1
```

## 📊 Monitoramento

### Logs Disponíveis

```bash
# Log principal da aplicação
tail -f limpeza_coletor.log

# Log do cron
tail -f cron.log

# Log de status
tail -f status.log
```

### Verificar Status

```bash
# Status completo do sistema
./run.sh --action status

# Verificar agendamentos do cron
crontab -l

# Verificar processos
ps aux | grep python
```

## 🌐 Interface Web

Após a execução, os dados ficam disponíveis em:

- **Página principal**: `frontend/index.html`
- **Ambientes faltantes**: `frontend/faltando.html`
- **Dados JSON**: `frontend/faltando.json`

Para servir a interface web:

```bash
# Servidor simples Python
cd frontend
python3 -m http.server 8000

# Acesse: http://localhost:8000
```

## 🔍 Solução de Problemas

### Problemas Comuns

1. **Erro de login**
   ```bash
   # Verifique as credenciais no .env
   cat .env
   ```

2. **Erro de dependências**
   ```bash
   # Reinstale as dependências
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Erro de permissões**
   ```bash
   # Ajuste permissões
   chmod +x *.sh
   chmod 755 .
   ```

4. **Cron não executa**
   ```bash
   # Verifique o cron
   crontab -l
   
   # Verifique logs
   tail -f /var/log/cron
   ```

### Debug

```bash
# Executar com logs detalhados
./run.sh --action full --log-level DEBUG

# Testar apenas coleta
./run.sh --action collect --log-level DEBUG

# Verificar conectividade
curl -I https://pro.manserv.com.br
```

## 🔒 Segurança

- ✅ Credenciais armazenadas em arquivo `.env` (não versionado)
- ✅ Token GitHub opcional para sincronização
- ✅ Logs não expõem informações sensíveis
- ✅ Conexões HTTPS para todas as requisições

### Configuração do Token GitHub

1. Acesse: https://github.com/settings/tokens
2. Crie um token com permissões de repositório
3. Adicione ao arquivo `.env`:
   ```env
   GITHUB_TOKEN=seu_token_aqui
   GITHUB_REPO=msv-stihl/limpeza
   ```

## 📋 Requisitos do Sistema

### Mínimos
- **SO**: Linux (Ubuntu 18.04+, CentOS 7+, Debian 9+)
- **Python**: 3.6+
- **RAM**: 512MB
- **Disco**: 1GB livre
- **Rede**: Acesso à internet

### Recomendados
- **SO**: Ubuntu 20.04+ ou CentOS 8+
- **Python**: 3.8+
- **RAM**: 1GB
- **Disco**: 2GB livre

## 🆘 Suporte

Para problemas ou dúvidas:

1. Verifique os logs: `tail -f limpeza_coletor.log`
2. Execute o diagnóstico: `./run.sh --action status`
3. Consulte a seção de solução de problemas
4. Entre em contato com a equipe de desenvolvimento

## 📝 Changelog

### v2.0.0 - Versão Linux
- ✅ Migração completa para Linux
- ✅ Substituição do Selenium por HTTP requests
- ✅ Remoção de dependências Windows
- ✅ Adição de agendamento via cron
- ✅ Melhoria no sistema de logs
- ✅ Interface de instalação automatizada

### v1.0.0 - Versão Windows
- ✅ Coleta via Selenium
- ✅ Processamento de planilhas Excel
- ✅ Geração de JSON
- ✅ Interface web básica

---

**Desenvolvido para MANSERV - Sistema de Limpeza Convencional**