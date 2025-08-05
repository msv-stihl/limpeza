#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para processar dados já coletados do arquivo exportacao.xlsx
Atualiza cronograma_lc.xlsx, gera faltando.json e sincroniza com GitHub
"""

import pandas as pd
import logging
from pathlib import Path
import sys
import os

# Adicionar o diretório atual ao path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from coletor_linux import ProManservCollector
from main import LimpezaManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('processar_dados.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def processar_dados_existentes():
    """Processa dados do arquivo exportacao.xlsx existente"""
    try:
        # Verificar se o arquivo exportacao.xlsx existe
        arquivo_exportacao = Path("exportacao.xlsx")
        if not arquivo_exportacao.exists():
            logger.error("Arquivo exportacao.xlsx não encontrado")
            return False
        
        logger.info("Iniciando processamento dos dados existentes...")
        
        # Ler dados do arquivo exportacao.xlsx
        logger.info("Lendo dados do arquivo exportacao.xlsx...")
        df_dados = pd.read_excel(arquivo_exportacao)
        logger.info(f"Carregados {len(df_dados)} registros do arquivo")
        
        # Criar instância do coletor para usar suas funções
        coletor = ProManservCollector()
        
        # Salvar no banco de dados
        logger.info("Salvando dados no banco de dados...")
        coletor.save_to_database(df_dados)
        
        # Atualizar cronograma
        logger.info("Atualizando cronograma...")
        coletor.update_cronograma(df_dados)
        
        # Gerar arquivo faltando.json
        logger.info("Gerando arquivo faltando.json...")
        coletor.generate_faltando_json()
        
        logger.info("Processamento dos dados concluído com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao processar dados: {e}")
        return False

def sincronizar_github():
    """Sincroniza alterações com GitHub"""
    try:
        logger.info("Iniciando sincronização com GitHub...")
        
        # Criar instância do LimpezaManager para usar a função de sync
        manager = LimpezaManager()
        
        # Executar sincronização
        manager.sync_git()
        
        logger.info("Sincronização com GitHub concluída!")
        return True
        
    except Exception as e:
        logger.error(f"Erro na sincronização com GitHub: {e}")
        return False

def main():
    """Função principal"""
    logger.info("=== Iniciando processamento de dados existentes ===")
    
    # Processar dados
    if not processar_dados_existentes():
        logger.error("Falha no processamento dos dados")
        return 1
    
    # Sincronizar com GitHub
    if not sincronizar_github():
        logger.error("Falha na sincronização com GitHub")
        return 1
    
    logger.info("=== Processamento completo finalizado com sucesso! ===")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)