#!/bin/bash
# Script para configurar cron no Linux

set -e

echo "=== Configuração do Cron para Coletor de Limpeza ==="

# Verificar se está rodando como usuário normal (não root)
if [ "$EUID" -eq 0 ]; then
    echo "AVISO: Executando como root. Recomenda-se executar como usuário normal."
fi

# Diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Diretório do projeto: $PROJECT_DIR"

# Verificar se o Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python 3 não encontrado. Instale o Python 3 primeiro."
    exit 1
fi

PYTHON_PATH=$(which python3)
echo "Python encontrado em: $PYTHON_PATH"

# Verificar se o arquivo principal existe
if [ ! -f "$PROJECT_DIR/main.py" ]; then
    echo "ERRO: Arquivo main.py não encontrado em $PROJECT_DIR"
    exit 1
fi

# Criar arquivo .env se não existir
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "Criando arquivo .env..."
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo "IMPORTANTE: Edite o arquivo .env com suas credenciais:"
    echo "  nano $PROJECT_DIR/.env"
fi

# Função para adicionar entrada no cron
add_cron_job() {
    local schedule="$1"
    local description="$2"
    local command="$3"
    
    echo "Configurando: $description"
    echo "Agendamento: $schedule"
    echo "Comando: $command"
    
    # Verificar se a entrada já existe
    if crontab -l 2>/dev/null | grep -q "$command"; then
        echo "Entrada já existe no cron, pulando..."
        return
    fi
    
    # Adicionar nova entrada
    (crontab -l 2>/dev/null; echo "# $description"; echo "$schedule $command") | crontab -
    echo "Entrada adicionada ao cron"
}

# Menu de opções
echo ""
echo "Escolha uma opção de agendamento:"
echo "1) Executar a cada 30 minutos (recomendado para testes)"
echo "2) Executar a cada hora"
echo "3) Executar a cada 2 horas"
echo "4) Executar 3 vezes por dia (8h, 14h, 20h)"
echo "5) Executar 2 vezes por dia (9h, 18h)"
echo "6) Executar 1 vez por dia (9h)"
echo "7) Configuração personalizada"
echo "8) Apenas verificar status (sem agendar)"
echo "9) Remover agendamentos existentes"

read -p "Digite sua escolha (1-9): " choice

case $choice in
    1)
        SCHEDULE="*/30 * * * *"
        DESCRIPTION="Coletor de limpeza - a cada 30 minutos"
        ;;
    2)
        SCHEDULE="0 * * * *"
        DESCRIPTION="Coletor de limpeza - a cada hora"
        ;;
    3)
        SCHEDULE="0 */2 * * *"
        DESCRIPTION="Coletor de limpeza - a cada 2 horas"
        ;;
    4)
        SCHEDULE="0 8,14,20 * * *"
        DESCRIPTION="Coletor de limpeza - 3x por dia"
        ;;
    5)
        SCHEDULE="0 9,18 * * *"
        DESCRIPTION="Coletor de limpeza - 2x por dia"
        ;;
    6)
        SCHEDULE="0 9 * * *"
        DESCRIPTION="Coletor de limpeza - 1x por dia"
        ;;
    7)
        echo "Digite o agendamento no formato cron (ex: '0 */2 * * *'):"
        read -p "Agendamento: " SCHEDULE
        DESCRIPTION="Coletor de limpeza - personalizado"
        ;;
    8)
        echo "Verificando status atual..."
        cd "$PROJECT_DIR"
        $PYTHON_PATH main.py --action status
        echo "Status verificado. Nenhum agendamento foi alterado."
        exit 0
        ;;
    9)
        echo "Removendo agendamentos existentes..."
        crontab -l 2>/dev/null | grep -v "main.py" | crontab -
        echo "Agendamentos removidos."
        exit 0
        ;;
    *)
        echo "Opção inválida"
        exit 1
        ;;
esac

# Comando completo para o cron
COMMAND="cd $PROJECT_DIR && $PYTHON_PATH main.py --action full >> $PROJECT_DIR/cron.log 2>&1"

# Adicionar entrada no cron
add_cron_job "$SCHEDULE" "$DESCRIPTION" "$COMMAND"

# Também adicionar um job de status diário
STATUS_COMMAND="cd $PROJECT_DIR && $PYTHON_PATH main.py --action status >> $PROJECT_DIR/status.log 2>&1"
add_cron_job "0 7 * * *" "Status diário do coletor de limpeza" "$STATUS_COMMAND"

echo ""
echo "=== Configuração Concluída ==="
echo "Agendamento configurado: $SCHEDULE"
echo "Logs serão salvos em:"
echo "  - Execução: $PROJECT_DIR/cron.log"
echo "  - Status: $PROJECT_DIR/status.log"
echo "  - Aplicação: $PROJECT_DIR/limpeza_coletor.log"
echo ""
echo "Para verificar os agendamentos ativos:"
echo "  crontab -l"
echo ""
echo "Para testar manualmente:"
echo "  cd $PROJECT_DIR && python3 main.py --action full"
echo ""
echo "Para monitorar logs em tempo real:"
echo "  tail -f $PROJECT_DIR/cron.log"
echo ""
echo "IMPORTANTE: Certifique-se de que o arquivo .env está configurado corretamente!"