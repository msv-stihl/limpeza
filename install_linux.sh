#!/bin/bash
# Script de instalação para Linux

set -e

echo "=== Instalação do Coletor de Limpeza para Linux ==="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCESSO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

# Verificar se está rodando no Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_error "Este script é destinado apenas para Linux"
    exit 1
fi

# Verificar se está rodando como usuário normal (não root)
if [ "$EUID" -eq 0 ]; then
    print_warning "Executando como root. Recomenda-se executar como usuário normal."
    read -p "Continuar mesmo assim? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
print_info "Diretório do projeto: $PROJECT_DIR"

# Função para verificar se um comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detectar distribuição Linux
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
    else
        DISTRO="unknown"
    fi
    print_info "Distribuição detectada: $DISTRO $VERSION"
}

# Instalar dependências do sistema
install_system_deps() {
    print_info "Instalando dependências do sistema..."
    
    case $DISTRO in
        ubuntu|debian)
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv git curl
            ;;
        centos|rhel|fedora)
            if command_exists dnf; then
                sudo dnf install -y python3 python3-pip git curl
            else
                sudo yum install -y python3 python3-pip git curl
            fi
            ;;
        arch)
            sudo pacman -S --noconfirm python python-pip git curl
            ;;
        *)
            print_warning "Distribuição não reconhecida. Instale manualmente: python3, pip3, git, curl"
            ;;
    esac
}

# Verificar Python
check_python() {
    print_info "Verificando Python..."
    
    if ! command_exists python3; then
        print_error "Python 3 não encontrado"
        return 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION encontrado"
    
    if ! command_exists pip3; then
        print_error "pip3 não encontrado"
        return 1
    fi
    
    print_success "pip3 encontrado"
    return 0
}

# Criar ambiente virtual
setup_venv() {
    print_info "Configurando ambiente virtual..."
    
    cd "$PROJECT_DIR"
    
    if [ -d "venv" ]; then
        print_warning "Ambiente virtual já existe, removendo..."
        rm -rf venv
    fi
    
    python3 -m venv venv
    source venv/bin/activate
    
    print_success "Ambiente virtual criado"
}

# Instalar dependências Python
install_python_deps() {
    print_info "Instalando dependências Python..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    pip install --upgrade pip
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependências instaladas via requirements.txt"
    else
        print_error "Arquivo requirements.txt não encontrado"
        return 1
    fi
}

# Configurar arquivo .env
setup_env() {
    print_info "Configurando arquivo de ambiente..."
    
    cd "$PROJECT_DIR"
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Arquivo .env criado a partir do exemplo"
        else
            print_warning "Arquivo .env.example não encontrado, criando .env básico"
            cat > .env << EOF
# Configurações do sistema Pro Manserv
PRO_USER=seu_usuario@manserv.com.br
PRO_PASS=sua_senha

# Configurações do GitHub (opcional)
GITHUB_TOKEN=seu_token_github
GITHUB_REPO=msv-stihl/limpeza

# Configurações de logging
LOG_LEVEL=INFO
EOF
        fi
        
        print_warning "IMPORTANTE: Edite o arquivo .env com suas credenciais:"
        print_warning "  nano $PROJECT_DIR/.env"
    else
        print_info "Arquivo .env já existe"
    fi
}

# Criar diretórios necessários
setup_directories() {
    print_info "Criando diretórios necessários..."
    
    cd "$PROJECT_DIR"
    
    mkdir -p downloads
    mkdir -p frontend
    mkdir -p logs
    
    print_success "Diretórios criados"
}

# Testar instalação
test_installation() {
    print_info "Testando instalação..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    if python3 main.py --action status; then
        print_success "Teste básico passou"
        return 0
    else
        print_error "Teste básico falhou"
        return 1
    fi
}

# Criar script de execução
create_run_script() {
    print_info "Criando script de execução..."
    
    cd "$PROJECT_DIR"
    
    cat > run.sh << EOF
#!/bin/bash
# Script para executar o coletor

cd "$PROJECT_DIR"
source venv/bin/activate
python3 main.py "\$@"
EOF
    
    chmod +x run.sh
    print_success "Script run.sh criado"
}

# Menu principal
main_menu() {
    echo ""
    print_info "Escolha uma opção:"
    echo "1) Instalação completa (recomendado)"
    echo "2) Apenas instalar dependências do sistema"
    echo "3) Apenas configurar ambiente Python"
    echo "4) Apenas testar instalação"
    echo "5) Configurar cron (após instalação)"
    echo "6) Sair"
    
    read -p "Digite sua escolha (1-6): " choice
    
    case $choice in
        1)
            full_installation
            ;;
        2)
            detect_distro
            install_system_deps
            ;;
        3)
            setup_venv
            install_python_deps
            setup_env
            setup_directories
            create_run_script
            ;;
        4)
            test_installation
            ;;
        5)
            if [ -f "setup_cron.sh" ]; then
                bash setup_cron.sh
            else
                print_error "Arquivo setup_cron.sh não encontrado"
            fi
            ;;
        6)
            print_info "Saindo..."
            exit 0
            ;;
        *)
            print_error "Opção inválida"
            main_menu
            ;;
    esac
}

# Instalação completa
full_installation() {
    print_info "Iniciando instalação completa..."
    
    detect_distro
    
    # Instalar dependências do sistema
    install_system_deps
    
    # Verificar Python
    if ! check_python; then
        print_error "Falha na verificação do Python"
        exit 1
    fi
    
    # Configurar ambiente Python
    setup_venv
    install_python_deps
    setup_env
    setup_directories
    create_run_script
    
    # Testar instalação
    if test_installation; then
        print_success "Instalação concluída com sucesso!"
        echo ""
        print_info "Próximos passos:"
        print_info "1. Edite o arquivo .env com suas credenciais:"
        print_info "   nano $PROJECT_DIR/.env"
        print_info "2. Execute o teste:"
        print_info "   ./run.sh --action status"
        print_info "3. Configure o cron:"
        print_info "   bash setup_cron.sh"
        echo ""
    else
        print_error "Instalação falhou no teste"
        exit 1
    fi
}

# Verificar se é execução direta ou sourcing
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main_menu
fi