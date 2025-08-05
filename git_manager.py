#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Git para automatizar push do arquivo faltando.json
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from git import Repo, GitCommandError
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logger = logging.getLogger(__name__)

class GitManager:
    def __init__(self, repo_path=None):
        self.repo_path = Path(repo_path) if repo_path else Path(__file__).parent.absolute()
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repo = os.getenv('GITHUB_REPO', 'msv-stihl/limpeza')
        
        try:
            self.repo = Repo(self.repo_path)
        except Exception as e:
            logger.error(f"Erro ao inicializar repositório Git: {e}")
            self.repo = None
    
    def init_repo(self):
        """Inicializa um repositório Git se não existir"""
        try:
            if not (self.repo_path / '.git').exists():
                logger.info("Inicializando repositório Git...")
                self.repo = Repo.init(self.repo_path)
                
                # Configurar remote se token estiver disponível
                if self.github_token and self.github_repo:
                    remote_url = f"https://{self.github_token}@github.com/{self.github_repo}.git"
                    self.repo.create_remote('origin', remote_url)
                    logger.info("Remote origin configurado")
                
                return True
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inicializar repositório: {e}")
            return False
    
    def add_files(self, files=None):
        """Adiciona arquivos ao staging"""
        try:
            if not self.repo:
                logger.error("Repositório não inicializado")
                return False
            
            if files is None:
                # Adicionar apenas arquivos específicos por padrão
                files = [
                    'frontend/faltando.json',
                    'frontend/index.html',
                    'frontend/faltando.html',
                    'frontend/main.js',
                    'frontend/styles.css'
                ]
            
            for file in files:
                file_path = self.repo_path / file
                if file_path.exists():
                    self.repo.index.add([file])
                    logger.info(f"Arquivo adicionado: {file}")
                else:
                    logger.warning(f"Arquivo não encontrado: {file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar arquivos: {e}")
            return False
    
    def commit_changes(self, message=None):
        """Faz commit das mudanças"""
        try:
            if not self.repo:
                logger.error("Repositório não inicializado")
                return False
            
            # Verificar se há mudanças para commit
            if not self.repo.index.diff("HEAD") and not self.repo.untracked_files:
                logger.info("Nenhuma mudança para commit")
                return True
            
            if message is None:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = f"Atualização automática dos dados de limpeza - {timestamp}"
            
            # Configurar usuário se não estiver configurado
            try:
                self.repo.config_reader().get_value("user", "name")
            except:
                with self.repo.config_writer() as git_config:
                    git_config.set_value("user", "name", "Coletor Automático")
                    git_config.set_value("user", "email", "coletor@manserv.com.br")
            
            commit = self.repo.index.commit(message)
            logger.info(f"Commit realizado: {commit.hexsha[:8]} - {message}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao fazer commit: {e}")
            return False
    
    def push_changes(self, branch='main'):
        """Faz push das mudanças para o repositório remoto"""
        try:
            if not self.repo:
                logger.error("Repositório não inicializado")
                return False
            
            if not self.github_token:
                logger.warning("Token do GitHub não configurado, pulando push")
                return True
            
            # Verificar se o remote existe
            if 'origin' not in [remote.name for remote in self.repo.remotes]:
                logger.warning("Remote 'origin' não encontrado")
                return False
            
            origin = self.repo.remote('origin')
            
            # Fazer push
            logger.info(f"Fazendo push para branch {branch}...")
            origin.push(refspec=f'{branch}:{branch}')
            logger.info("Push realizado com sucesso")
            return True
            
        except GitCommandError as e:
            logger.error(f"Erro no comando Git durante push: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro ao fazer push: {e}")
            return False
    
    def pull_changes(self, branch='main'):
        """Faz pull das mudanças do repositório remoto"""
        try:
            if not self.repo:
                logger.error("Repositório não inicializado")
                return False
            
            if 'origin' not in [remote.name for remote in self.repo.remotes]:
                logger.warning("Remote 'origin' não encontrado")
                return False
            
            origin = self.repo.remote('origin')
            
            logger.info(f"Fazendo pull da branch {branch}...")
            origin.pull(branch)
            logger.info("Pull realizado com sucesso")
            return True
            
        except GitCommandError as e:
            logger.error(f"Erro no comando Git durante pull: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro ao fazer pull: {e}")
            return False
    
    def sync_repository(self, files=None, commit_message=None):
        """Sincroniza o repositório: add, commit e push"""
        try:
            logger.info("Iniciando sincronização do repositório...")
            
            # Inicializar repo se necessário
            if not self.init_repo():
                return False
            
            # Fazer pull primeiro (se possível)
            self.pull_changes()
            
            # Adicionar arquivos
            if not self.add_files(files):
                return False
            
            # Fazer commit
            if not self.commit_changes(commit_message):
                return False
            
            # Fazer push
            if not self.push_changes():
                return False
            
            logger.info("Sincronização concluída com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro durante sincronização: {e}")
            return False
    
    def get_status(self):
        """Retorna o status do repositório"""
        try:
            if not self.repo:
                return "Repositório não inicializado"
            
            status = {
                'branch': self.repo.active_branch.name,
                'modified': [item.a_path for item in self.repo.index.diff(None)],
                'staged': [item.a_path for item in self.repo.index.diff("HEAD")],
                'untracked': self.repo.untracked_files,
                'last_commit': str(self.repo.head.commit.hexsha[:8]) if self.repo.head.commit else None
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Erro ao obter status: {e}")
            return None

def main():
    """Função principal para teste"""
    logging.basicConfig(level=logging.INFO)
    
    git_manager = GitManager()
    
    # Mostrar status
    status = git_manager.get_status()
    if status:
        logger.info(f"Status do repositório: {status}")
    
    # Sincronizar
    success = git_manager.sync_repository()
    
    if success:
        logger.info("Sincronização bem-sucedida")
    else:
        logger.error("Falha na sincronização")

if __name__ == '__main__':
    main()