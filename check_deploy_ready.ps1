# Script para verificar se o projeto esta pronto para deploy na OCI
# Execute antes de fazer o deploy para garantir que tudo esta configurado

param(
    [string]$VMIp = "",
    [string]$KeyPath = ""
)

$ErrorActionPreference = "Continue"

# Cores para output
function Write-Success { param($msg) Write-Host $msg -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host $msg -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host $msg -ForegroundColor Red }
function Write-Info { param($msg) Write-Host $msg -ForegroundColor Cyan }

Write-Host "=== VERIFICACAO PRE-DEPLOY OCI ===" -ForegroundColor Green
Write-Host ""

$issues = @()
$warnings = @()
$success = @()

# 1. Verificar arquivos essenciais do projeto
Write-Info "1. Verificando arquivos do projeto..."

$requiredFiles = @(
    "coletor_linux.py",
    "main.py",
    "git_manager.py",
    "requirements.txt",
    "install_linux.sh",
    "setup_cron.sh",
    "test_system.py",
    ".env.example",
    "README.md",
    "deploy_to_oci.ps1",
    "clean_and_setup_vm.sh"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        $success += "OK $file encontrado"
    } else {
        $issues += "ERRO $file nao encontrado"
    }
}

# 2. Verificar diretorio frontend
Write-Info "2. Verificando frontend..."

if (Test-Path "frontend") {
    $frontendFiles = @("index.html", "faltando.html", "main.js", "styles.css")
    foreach ($file in $frontendFiles) {
        $fullPath = "frontend\$file"
        if (Test-Path $fullPath) {
            $success += "OK Frontend: $file encontrado"
        } else {
            $warnings += "AVISO Frontend: $file nao encontrado"
        }
    }
} else {
    $issues += "ERRO Diretorio frontend nao encontrado"
}

# 3. Verificar arquivo .env
Write-Info "3. Verificando configuracao..."

if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "PRO_MANSERV_USER=.+" -and $envContent -match "PRO_MANSERV_PASS=.+") {
        $success += "OK Arquivo .env configurado com credenciais"
    } else {
        $warnings += "AVISO Arquivo .env existe mas pode estar incompleto"
    }
} else {
    $warnings += "AVISO Arquivo .env nao encontrado (sera criado a partir do .env.example)"
}

# 4. Verificar dependencias Python (se Python estiver instalado)
Write-Info "4. Verificando Python..."

try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3") {
        $success += "OK Python 3 encontrado: $pythonVersion"
        
        # Verificar se pip funciona
        $pipVersion = pip --version 2>&1
        if ($pipVersion -match "pip") {
            $success += "OK Pip funcionando"
        } else {
            $warnings += "AVISO Pip pode nao estar funcionando corretamente"
        }
    } else {
        $warnings += "AVISO Python 3 nao encontrado no Windows (OK, sera instalado na VM)"
    }
} catch {
    $warnings += "AVISO Python nao encontrado no Windows (OK, sera instalado na VM)"
}

# 5. Verificar Git
Write-Info "5. Verificando Git..."

try {
    $gitVersion = git --version 2>&1
    if ($gitVersion -match "git version") {
        $success += "OK Git encontrado: $gitVersion"
        
        # Verificar se e um repositorio git
        if (Test-Path ".git") {
            $success += "OK Repositorio Git inicializado"
            
            # Verificar remote
            $remotes = git remote -v 2>&1
            if ($remotes -match "origin") {
                $success += "OK Remote Git configurado"
            } else {
                $warnings += "AVISO Remote Git nao configurado (opcional)"
            }
        } else {
            $warnings += "AVISO Nao e um repositorio Git (opcional)"
        }
    }
} catch {
    $warnings += "AVISO Git nao encontrado (opcional para deploy)"
}

# 6. Verificar SSH e conectividade (se parametros fornecidos)
if ($VMIp -and $KeyPath) {
    Write-Info "6. Verificando conectividade com VM..."
    
    if (Test-Path $KeyPath) {
        $success += "OK Chave SSH encontrada: $KeyPath"
        
        # Testar SSH
        try {
            $sshTest = ssh -i "$KeyPath" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "opc@$VMIp" "echo 'SSH OK'" 2>&1
            if ($sshTest -match "SSH OK") {
                $success += "OK Conectividade SSH com VM funcionando"
            } else {
                $issues += "ERRO Falha na conectividade SSH: $sshTest"
            }
        } catch {
            $issues += "ERRO Erro ao testar SSH: $($_.Exception.Message)"
        }
    } else {
        $issues += "ERRO Chave SSH nao encontrada: $KeyPath"
    }
} else {
    Write-Info "6. Teste de conectividade pulado (parametros nao fornecidos)"
}

# 7. Verificar SCP (para transferencia de arquivos)
Write-Info "7. Verificando SCP..."

try {
    $scpTest = scp 2>&1
    if ($scpTest -match "usage" -or $scpTest -match "scp:") {
        $success += "OK SCP disponivel para transferencia de arquivos"
    } else {
        $issues += "ERRO SCP nao encontrado. Instale OpenSSH Client"
    }
} catch {
    $issues += "ERRO SCP nao encontrado. Instale OpenSSH Client"
}

# 8. Verificar tamanho do projeto
Write-Info "8. Verificando tamanho do projeto..."

$projectSize = (Get-ChildItem -Recurse | Where-Object { !$_.PSIsContainer } | Measure-Object -Property Length -Sum).Sum
$projectSizeMB = [math]::Round($projectSize / 1MB, 2)

if ($projectSizeMB -lt 50) {
    $success += "OK Tamanho do projeto: $projectSizeMB MB (adequado)"
} elseif ($projectSizeMB -lt 100) {
    $warnings += "AVISO Tamanho do projeto: $projectSizeMB MB (um pouco grande)"
} else {
    $warnings += "AVISO Tamanho do projeto: $projectSizeMB MB (considere limpar arquivos desnecessarios)"
}

# Resultados
Write-Host ""
Write-Host "=== RESULTADOS DA VERIFICACAO ===" -ForegroundColor Green
Write-Host ""

if ($success.Count -gt 0) {
    Write-Host "SUCESSOS ($($success.Count)):" -ForegroundColor Green
    foreach ($item in $success) {
        Write-Host "  $item"
    }
    Write-Host ""
}

if ($warnings.Count -gt 0) {
    Write-Host "AVISOS ($($warnings.Count)):" -ForegroundColor Yellow
    foreach ($item in $warnings) {
        Write-Host "  $item"
    }
    Write-Host ""
}

if ($issues.Count -gt 0) {
    Write-Host "PROBLEMAS ($($issues.Count)):" -ForegroundColor Red
    foreach ($item in $issues) {
        Write-Host "  $item"
    }
    Write-Host ""
}

# Recomendacoes
Write-Host "=== RECOMENDACOES ===" -ForegroundColor Blue
Write-Host ""

if ($issues.Count -eq 0) {
    Write-Success "OK Projeto pronto para deploy!"
    Write-Host ""
    Write-Host "Para fazer o deploy, execute:" -ForegroundColor Cyan
    Write-Host ".\deploy_to_oci.ps1 -VMIp \"SEU_IP\" -KeyPath \"CAMINHO_DA_CHAVE.pem\"" -ForegroundColor White
} else {
    Write-Error "ERRO Corrija os problemas antes do deploy"
}

if ($warnings.Count -gt 0) {
    Write-Host "Avisos podem ser ignorados, mas e recomendado corrigi-los." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== PROXIMOS PASSOS ===" -ForegroundColor Blue
Write-Host ""
Write-Host "1. Corrija os problemas listados acima" -ForegroundColor White
Write-Host "2. Execute o deploy: .\deploy_to_oci.ps1 -VMIp \"IP\" -KeyPath \"chave.pem\"" -ForegroundColor White
Write-Host "3. Ou consulte o guia: QUICK_DEPLOY_OCI.md" -ForegroundColor White
Write-Host ""

# Estatisticas finais
$total = $success.Count + $warnings.Count + $issues.Count
Write-Host "Verificacoes: $total | Sucessos: $($success.Count) | Avisos: $($warnings.Count) | Problemas: $($issues.Count)" -ForegroundColor Gray

if ($issues.Count -eq 0) {
    exit 0
} else {
    exit 1
}