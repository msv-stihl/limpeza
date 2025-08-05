#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script principal para execução do coletor de dados de limpeza
Compatível com Linux e agendamento via cron
"""

import os
import sys
import time
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.append(str(Path(__file__).parent.absolute()))

from coletor_linux import ProManservCollector
from git_manager import GitManager
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
def setup_logging(log_level='INFO'):
    """Configura o sistema de logging"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configurar nível de log
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configurar handlers
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('limpeza_coletor.log', encoding='utf-8')
    ]
    
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers
    )
    
    return logging.getLogger(__name__)

class LimpezaManager:
    """Gerenciador principal do sistema de limpeza"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.collector = ProManservCollector()
        self.git_manager = GitManager()
        
    def run_collection(self):
        """Executa a coleta de dados"""
        self.logger.info("=== INICIANDO COLETA DE DADOS ===")
        
        try:
            success = self.collector.run()
            
            if success:
                self.logger.info("Coleta de dados concluída com sucesso")
                return True
            else:
                self.logger.error("Falha na coleta de dados")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro durante a coleta: {e}")
            return False
    
    def sync_git(self):
        """Sincroniza com o repositório Git"""
        self.logger.info("=== SINCRONIZANDO COM GIT ===")
        
        try:
            # Verificar se o arquivo JSON foi gerado
            json_file = Path(__file__).parent / "frontend" / "faltando.json"
            
            if not json_file.exists():
                self.logger.warning("Arquivo faltando.json não encontrado, pulando sincronização")
                return True
            
            # Sincronizar repositório
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"Atualização automática dos dados de limpeza - {timestamp}"
            
            success = self.git_manager.sync_repository(
                commit_message=commit_message
            )
            
            if success:
                self.logger.info("Sincronização Git concluída com sucesso")
                return True
            else:
                self.logger.error("Falha na sincronização Git")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro durante sincronização Git: {e}")
            return False
    
    def run_full_process(self):
        """Executa o processo completo: coleta + sincronização"""
        self.logger.info("=== INICIANDO PROCESSO COMPLETO ===")
        
        start_time = datetime.now()
        
        try:
            # Executar coleta
            collection_success = self.run_collection()
            
            if not collection_success:
                self.logger.error("Processo interrompido devido a falha na coleta")
                return False
            
            # Sincronizar com Git
            git_success = self.sync_git()
            
            if not git_success:
                self.logger.warning("Coleta bem-sucedida, mas falha na sincronização Git")
            
            # Calcular tempo de execução
            end_time = datetime.now()
            duration = end_time - start_time
            
            self.logger.info(f"=== PROCESSO CONCLUÍDO EM {duration} ===")
            
            return collection_success and git_success
            
        except Exception as e:
            self.logger.error(f"Erro durante processo completo: {e}")
            return False
    
    def check_system_status(self):
        """Verifica o status do sistema"""
        self.logger.info("=== VERIFICANDO STATUS DO SISTEMA ===")
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'files': {},
            'git': None
        }
        
        # Verificar arquivos importantes
        important_files = [
            'exportacao.xlsx',
            'cronograma_lc.xlsx',
            'frontend/faltando.json',
            'frontend/index.html',
            'cronograma-lc.db'
        ]
        
        base_path = Path(__file__).parent
        
        for file_path in important_files:
            full_path = base_path / file_path
            status['files'][file_path] = {
                'exists': full_path.exists(),
                'size': full_path.stat().st_size if full_path.exists() else 0,
                'modified': full_path.stat().st_mtime if full_path.exists() else None
            }
        
        # Verificar status do Git
        try:
            git_status = self.git_manager.get_status()
            status['git'] = git_status
        except Exception as e:
            status['git'] = f"Erro: {e}"
        
        # Log do status
        self.logger.info("Status dos arquivos:")
        for file_path, file_info in status['files'].items():
            if file_info['exists']:
                modified = datetime.fromtimestamp(file_info['modified']).strftime('%Y-%m-%d %H:%M:%S')
                self.logger.info(f"  {file_path}: OK ({file_info['size']} bytes, modificado em {modified})")
            else:
                self.logger.warning(f"  {file_path}: AUSENTE")
        
        if status['git']:
            self.logger.info(f"Status Git: {status['git']}")
        
        return status

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Coletor de dados de limpeza')
    parser.add_argument('--action', choices=['collect', 'sync', 'full', 'status'], 
                       default='full', help='Ação a ser executada')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Nível de log')
    parser.add_argument('--no-git', action='store_true', 
                       help='Não sincronizar com Git')
    
    args = parser.parse_args()
    
    # Configurar logging
    logger = setup_logging(args.log_level)
    
    # Criar gerenciador
    manager = LimpezaManager()
    
    try:
        if args.action == 'collect':
            success = manager.run_collection()
        elif args.action == 'sync':
            success = manager.sync_git()
        elif args.action == 'status':
            manager.check_system_status()
            success = True
        else:  # full
            if args.no_git:
                success = manager.run_collection()
            else:
                success = manager.run_full_process()
        
        if success:
            logger.info("Execução concluída com sucesso")
            sys.exit(0)
        else:
            logger.error("Execução falhou")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Execução interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()