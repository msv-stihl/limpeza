#!/bin/bash
# Script para limpar VM e configurar o sistema de limpeza
# Execute este script diretamente na VM Linux da OCI

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Verificar se está rodando como usuário normal (não root)
if [ "$EUID" -eq 0 ]; then
    log_error "Não execute este script como root. Use um usuário normal com sudo."
    exit 1
fi

# Banner
echo -e "${GREEN}"
echo "================================================"
echo "    LIMPEZA E CONFIGURAÇÃO DA VM OCI"
echo "    Sistema de Coleta de Dados - Versão Linux"
echo "================================================"
echo -e "${NC}"

# Detectar distribuição Linux
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
    VERSION=$VERSION_ID
else
    log_error "Não foi possível detectar a distribuição Linux"
    exit 1
fi

log_info "Distribuição detectada: $DISTRO $VERSION"

# Função para instalar pacotes baseado na distribuição
install_packages() {
    log_step "Instalando dependências do sistema..."
    
    case $DISTRO in
        "ubuntu"|"debian")
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv git curl wget unzip nano htop tree
            ;;
        "centos"|"rhel"|"fedora"|"ol")
            if command -v dnf &> /dev/null; then
                sudo dnf update -y
                sudo dnf install -y python3 python3-pip git curl wget unzip nano htop tree
            else
                sudo yum update -y
                sudo yum install -y python3 python3-pip git curl wget unzip nano htop tree
            fi
            ;;
        *)
            log_warn "Distribuição não reconhecida. Tentando instalação genérica..."
            if command -v apt &> /dev/null; then
                sudo apt update && sudo apt install -y python3 python3-pip python3-venv git curl wget unzip
            elif command -v yum &> /dev/null; then
                sudo yum update -y && sudo yum install -y python3 python3-pip git curl wget unzip
            else
                log_error "Gerenciador de pacotes não suportado"
                exit 1
            fi
            ;;
    esac
}

# Função para limpeza completa
clean_vm() {
    log_step "Limpando VM..."
    
    # Remover diretórios de projetos antigos
    rm -rf ~/limpeza ~/projeto_* ~/coleta_* ~/robot_* 2>/dev/null || true
    
    # Limpar downloads e temporários
    rm -rf ~/Downloads/* ~/downloads/* 2>/dev/null || true
    rm -rf /tmp/* 2>/dev/null || true
    
    # Limpar logs antigos
    sudo rm -rf /var/log/*.log.* 2>/dev/null || true
    
    # Limpar cache do pip
    pip3 cache purge 2>/dev/null || true
    
    # Limpar cache do sistema
    case $DISTRO in
        "ubuntu"|"debian")
            sudo apt autoremove -y
            sudo apt autoclean
            ;;
        "centos"|"rhel"|"fedora"|"ol")
            if command -v dnf &> /dev/null; then
                sudo dnf autoremove -y
                sudo dnf clean all
            else
                sudo yum autoremove -y
                sudo yum clean all
            fi
            ;;
    esac
    
    log_info "Limpeza concluída!"
}

# Função para mostrar informações do sistema
show_system_info() {
    log_step "Informações do Sistema:"
    echo "Hostname: $(hostname)"
    echo "Usuário: $(whoami)"
    echo "Diretório atual: $(pwd)"
    echo "Distribuição: $DISTRO $VERSION"
    echo "Kernel: $(uname -r)"
    echo "Arquitetura: $(uname -m)"
    echo "Memória: $(free -h | grep Mem | awk '{print $2}')"
    echo "Disco: $(df -h / | tail -1 | awk '{print $2" ("$4" livre)"}')"
    echo "Python: $(python3 --version 2>/dev/null || echo 'Não instalado')"
    echo "Git: $(git --version 2>/dev/null || echo 'Não instalado')"
    echo ""
}

# Função para configurar firewall
setup_firewall() {
    log_step "Configurando firewall..."
    
    # Verificar se o firewall está ativo
    if command -v ufw &> /dev/null; then
        # Ubuntu/Debian
        sudo ufw --force enable
        sudo ufw allow ssh
        sudo ufw allow 8000/tcp  # Para servidor web local
        log_info "UFW configurado"
    elif command -v firewall-cmd &> /dev/null; then
        # CentOS/RHEL/Fedora
        sudo systemctl enable firewalld
        sudo systemctl start firewalld
        sudo firewall-cmd --permanent --add-service=ssh
        sudo firewall-cmd --permanent --add-port=8000/tcp
        sudo firewall-cmd --reload
        log_info "Firewalld configurado"
    else
        log_warn "Firewall não configurado automaticamente"
    fi
}

# Função para criar estrutura de diretórios
setup_directories() {
    log_step "Criando estrutura de diretórios..."
    
    mkdir -p ~/limpeza/{downloads,frontend,logs,backup}
    mkdir -p ~/.ssh
    
    # Definir permissões corretas
    chmod 700 ~/.ssh
    chmod 755 ~/limpeza
    
    log_info "Diretórios criados"
}

# Função para configurar SSH (melhorar segurança)
setup_ssh() {
    log_step "Configurando SSH..."
    
    # Backup da configuração atual
    sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
    
    # Configurações de segurança SSH
    sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
    sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
    
    # Reiniciar SSH
    sudo systemctl restart sshd
    
    log_info "SSH configurado com segurança aprimorada"
}

# Função para instalar Docker (opcional)
install_docker() {
    read -p "Deseja instalar Docker? (y/N): " install_docker
    
    if [[ $install_docker =~ ^[Yy]$ ]]; then
        log_step "Instalando Docker..."
        
        case $DISTRO in
            "ubuntu"|"debian")
                curl -fsSL https://get.docker.com -o get-docker.sh
                sudo sh get-docker.sh
                sudo usermod -aG docker $USER
                ;;
            "centos"|"rhel"|"fedora"|"ol")
                curl -fsSL https://get.docker.com -o get-docker.sh
                sudo sh get-docker.sh
                sudo systemctl enable docker
                sudo systemctl start docker
                sudo usermod -aG docker $USER
                ;;
        esac
        
        rm -f get-docker.sh
        log_info "Docker instalado. Faça logout/login para usar sem sudo"
    fi
}

# Função para download do projeto
download_project() {
    log_step "Preparando para download do projeto..."
    
    echo "Opções de download:"
    echo "1. Git clone (se o projeto estiver no GitHub)"
    echo "2. Download manual via SCP"
    echo "3. Upload via interface web"
    echo "4. Pular (fazer manualmente depois)"
    
    read -p "Escolha uma opção (1-4): " download_option
    
    case $download_option in
        1)
            read -p "Digite a URL do repositório Git: " git_url
            if [ ! -z "$git_url" ]; then
                cd ~
                git clone "$git_url" limpeza
                log_info "Projeto clonado via Git"
            fi
            ;;
        2)
            log_info "Para transferir via SCP, execute no Windows:"
            echo "scp -i sua_chave.pem -r ./limpeza opc@$(curl -s ifconfig.me):~/"
            ;;
        3)
            log_info "Você pode usar ferramentas como FileZilla ou WinSCP"
            ;;
        4)
            log_info "Download pulado"
            ;;
    esac
}

# Menu principal
show_menu() {
    echo ""
    echo "Escolha uma opção:"
    echo "1. Limpeza completa + Configuração"
    echo "2. Apenas limpeza"
    echo "3. Apenas instalação de dependências"
    echo "4. Configurar firewall"
    echo "5. Mostrar informações do sistema"
    echo "6. Download do projeto"
    echo "7. Instalar Docker (opcional)"
    echo "8. Sair"
    echo ""
}

# Loop principal
while true; do
    show_system_info
    show_menu
    read -p "Digite sua escolha (1-8): " choice
    
    case $choice in
        1)
            clean_vm
            install_packages
            setup_directories
            setup_firewall
            setup_ssh
            download_project
            log_info "Configuração completa finalizada!"
            ;;
        2)
            clean_vm
            ;;
        3)
            install_packages
            ;;
        4)
            setup_firewall
            ;;
        5)
            show_system_info
            ;;
        6)
            download_project
            ;;
        7)
            install_docker
            ;;
        8)
            log_info "Saindo..."
            break
            ;;
        *)
            log_error "Opção inválida"
            ;;
    esac
    
    echo ""
    read -p "Pressione Enter para continuar..."
    clear
done

echo -e "${GREEN}"
echo "================================================"
echo "           CONFIGURAÇÃO FINALIZADA"
echo "================================================"
echo -e "${NC}"
echo "Próximos passos:"
echo "1. Transfira os arquivos do projeto para ~/limpeza"
echo "2. Execute: cd ~/limpeza && ./install_linux.sh"
echo "3. Configure o arquivo .env"
echo "4. Execute: ./run.sh --action status"
echo "5. Configure o cron: ./setup_cron.sh"
echo ""
echo "Para monitoramento:"
echo "- htop (processos)"
echo "- df -h (disco)"
echo "- free -h (memória)"
echo "- tail -f ~/limpeza/logs/*.log (logs)"
echo ""