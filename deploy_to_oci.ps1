# Script PowerShell para deploy automatico na VM OCI
# Execute este script no Windows para transferir e configurar o sistema na VM Linux

param(
    [Parameter(Mandatory=$true)]
    [string]$VMIp,
    
    [Parameter(Mandatory=$true)]
    [string]$KeyPath,
    
    [string]$User = "opc",
    
    [string]$ProjectPath = $PSScriptRoot
)

# Configuracoes
$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

Write-Host "=== Deploy do Sistema de Limpeza na OCI ===" -ForegroundColor Green
Write-Host "VM IP: $VMIp" -ForegroundColor Cyan
Write-Host "Usuario: $User" -ForegroundColor Cyan
Write-Host "Chave: $KeyPath" -ForegroundColor Cyan
Write-Host "Projeto: $ProjectPath" -ForegroundColor Cyan
Write-Host ""

# Verificar se a chave SSH existe
if (-not (Test-Path $KeyPath)) {
    Write-Error "Chave SSH nao encontrada: $KeyPath"
    exit 1
}

# Verificar se o SCP esta disponivel
try {
    $null = Get-Command scp -ErrorAction Stop
} catch {
    Write-Error "SCP nao encontrado. Instale o OpenSSH Client no Windows."
    exit 1
}

# Funcao para executar comandos SSH
function Invoke-SSHCommand {
    param([string]$Command)
    
    Write-Host "Executando: $Command" -ForegroundColor Yellow
    ssh -i "$KeyPath" -o StrictHostKeyChecking=no "$User@$VMIp" $Command
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Falha ao executar comando SSH: $Command"
        exit 1
    }
}

# Funcao para transferir arquivos
function Copy-ToVM {
    param(
        [string]$LocalPath,
        [string]$RemotePath
    )
    
    Write-Host "Transferindo: $LocalPath -> $RemotePath" -ForegroundColor Yellow
    scp -i "$KeyPath" -o StrictHostKeyChecking=no "$LocalPath" "$User@$VMIp`:$RemotePath"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Falha ao transferir arquivo: $LocalPath"
        exit 1
    }
}

try {
    # 1. Testar conectividade
    Write-Host "1. Testando conectividade com a VM..." -ForegroundColor Green
    Invoke-SSHCommand "echo `"Conexao estabelecida com sucesso`""
    
    # 2. Preparar VM (atualizar e instalar dependencias)
    Write-Host "2. Preparando VM (instalando dependencias)..." -ForegroundColor Green
    
    # Detectar distribuicao
    $distro = ssh -i "$KeyPath" -o StrictHostKeyChecking=no "$User@$VMIp" 'cat /etc/os-release | grep "^ID=" | cut -d"=" -f2 | tr -d "\""'
    Write-Host "Distribuicao detectada: $distro" -ForegroundColor Cyan
    
    if ($distro -match "ubuntu|debian") {
        Invoke-SSHCommand "sudo apt update && sudo apt install -y python3 python3-pip python3-venv git curl wget unzip"
    } else {
        Invoke-SSHCommand "sudo yum update -y && sudo yum install -y python3 python3-pip git curl wget unzip"
    }
    
    # 3. Criar pacote de deploy
    Write-Host "3. Criando pacote de deploy..." -ForegroundColor Green
    
    $deployPath = Join-Path $env:TEMP "limpeza_deploy.zip"
    
    # Arquivos para incluir no deploy
    $filesToInclude = @(
        "*.py",
        "*.sh",
        "*.txt",
        "*.md",
        ".env.example",
        ".gitignore",
        "frontend"
    )
    
    # Criar arquivo ZIP
    Push-Location $ProjectPath
    
    $items = @()
    foreach ($pattern in $filesToInclude) {
        $items += Get-ChildItem -Path $pattern -Recurse -File | Where-Object { $_.FullName -notmatch "__pycache__|.pyc$|.log$" }
    }
    
    if ($items.Count -eq 0) {
        Write-Error "Nenhum arquivo encontrado para deploy"
        exit 1
    }
    
    Write-Host "Compactando $($items.Count) arquivos..." -ForegroundColor Cyan
    Compress-Archive -Path $items.FullName -DestinationPath $deployPath -Force
    
    Pop-Location
    
    # 4. Transferir pacote
    Write-Host "4. Transferindo pacote para VM..." -ForegroundColor Green
    Copy-ToVM $deployPath "~/limpeza_deploy.zip"
    
    # 5. Extrair e configurar
    Write-Host "5. Extraindo e configurando sistema..." -ForegroundColor Green
    
    Invoke-SSHCommand "rm -rf ~/limpeza"
    Invoke-SSHCommand "mkdir -p ~/limpeza"
    Invoke-SSHCommand "cd ~/limpeza && unzip -o ~/limpeza_deploy.zip"
    Invoke-SSHCommand "cd ~/limpeza && chmod +x *.sh"
    
    # 6. Executar instalacao
    Write-Host "6. Executando instalacao automatica..." -ForegroundColor Green
    Invoke-SSHCommand "cd ~/limpeza && echo `"1`" | ./install_linux.sh"
    
    # 7. Configurar arquivo .env
    Write-Host "7. Configurando arquivo .env..." -ForegroundColor Green
    
    # Verificar se existe .env local para copiar
    $localEnvPath = Join-Path $ProjectPath ".env"
    if (Test-Path $localEnvPath) {
        Write-Host "Transferindo arquivo .env local..." -ForegroundColor Cyan
        Copy-ToVM $localEnvPath "~/limpeza/.env"
    } else {
        Write-Host "Criando .env a partir do exemplo..." -ForegroundColor Cyan
        Invoke-SSHCommand "cd ~/limpeza && cp .env.example .env"
        Write-Warning "IMPORTANTE: Edite o arquivo .env na VM com suas credenciais!"
    }
    
    # 8. Testar sistema
    Write-Host "8. Testando sistema..." -ForegroundColor Green
    Invoke-SSHCommand "cd ~/limpeza && python3 test_system.py"
    Invoke-SSHCommand "cd ~/limpeza && ./run.sh --action status"
    
    # 9. Configurar cron (opcional)
    Write-Host "9. Configurando cron..." -ForegroundColor Green
    
    $configureCron = Read-Host "Deseja configurar o cron automaticamente? (y/N)"
    if ($configureCron -eq "y" -or $configureCron -eq "Y") {
        $cronOption = Read-Host "Escolha a opcao de agendamento (1-6, recomendado: 4)"
        if ($cronOption -match "^[1-6]$") {
            $cronCommand = "cd ~/limpeza && echo `"$cronOption`" | ./setup_cron.sh"
            Invoke-SSHCommand $cronCommand
        } else {
            Write-Warning "Opcao invalida. Configure o cron manualmente depois."
        }
    }
    
    # 10. Limpeza
    Write-Host "10. Limpando arquivos temporarios..." -ForegroundColor Green
    Invoke-SSHCommand "rm -f ~/limpeza_deploy.zip"
    Remove-Item $deployPath -Force -ErrorAction SilentlyContinue
    
    # Sucesso!
    Write-Host ""
    Write-Host "=== DEPLOY CONCLUIDO COM SUCESSO! ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Proximos passos:" -ForegroundColor Yellow
    Write-Host "1. Conecte na VM: ssh -i $KeyPath $User@$VMIp" -ForegroundColor White
    Write-Host "2. Va para o diretorio: cd ~/limpeza" -ForegroundColor White
    Write-Host "3. Edite as credenciais: nano .env" -ForegroundColor White
    Write-Host "4. Teste o sistema: ./run.sh --action status" -ForegroundColor White
    Write-Host "5. Configure o cron: ./setup_cron.sh" -ForegroundColor White
    Write-Host ""
    Write-Host "Logs disponiveis na VM:" -ForegroundColor Yellow
    Write-Host "- tail -f ~/limpeza/limpeza_coletor.log" -ForegroundColor White
    Write-Host "- tail -f ~/limpeza/cron.log" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Error "Erro durante o deploy: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "Para debug, conecte manualmente na VM:" -ForegroundColor Yellow
    Write-Host "ssh -i $KeyPath $User@$VMIp" -ForegroundColor White
    exit 1
}

# Perguntar se quer abrir conexao SSH
$openSSH = Read-Host "Deseja abrir uma conexao SSH com a VM agora? (y/N)"
if ($openSSH -eq "y" -or $openSSH -eq "Y") {
    Write-Host "Abrindo conexao SSH..." -ForegroundColor Green
    ssh -i "$KeyPath" "$User@$VMIp"
}

Write-Host "Deploy finalizado!" -ForegroundColor Green