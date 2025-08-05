#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coletor de dados usando Selenium para simular comportamento real do usuário
Compatível com cron e sem dependências do Windows
"""

import os
import time
import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
import calendar
import shutil
import logging
from pathlib import Path
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import glob

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('coletor_selenium.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- CONFIGURAÇÃO E SEGURANÇA ---
PRO_URL = "https://pro.manserv.com.br"
PRO_LOGIN_URL = f"{PRO_URL}/login"
PRO_CHECKLIST_URL = f"{PRO_URL}/operational/checklist-results-history"
PRO_EXPORT_URL = f"{PRO_URL}/operational/checklist-results-export"

# Credenciais (usar variáveis de ambiente em produção)
PRO_USER = os.getenv('PRO_USER', 'wesley.luz@manserv.com.br')
PRO_PASS = os.getenv('PRO_PASS', '028885')

# Diretórios
DIRETORIO_ATUAL = Path(__file__).parent.absolute()
PASTA_DOWNLOAD = DIRETORIO_ATUAL / "downloads"
PASTA_DOWNLOAD.mkdir(exist_ok=True)

# Configuração do Chrome para downloads
CHROME_DOWNLOAD_PATH = str(PASTA_DOWNLOAD.absolute())

class ColetorSelenium:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Configura o driver do Chrome com opções para download"""
        chrome_options = Options()
        
        # Configurações para ambiente headless (servidor)
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        )
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        # Configurações de download
        prefs = {
            "download.default_directory": CHROME_DOWNLOAD_PATH,
            "download.prompt_for_download": False,
            "directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Remover a detecção do webdriver
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """
            })
            
            self.wait = WebDriverWait(self.driver, 30)
            logger.info("Driver Chrome configurado com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao configurar driver: {e}")
            return False
    
    def login(self):
        """Realiza login no sistema"""
        try:
            logger.info("Acessando página de login...")
            self.driver.get(PRO_LOGIN_URL)
            
            # Aguardar campos de login
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "client-email"))
            )
            password_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "client-password"))
            )
            
            # Preencher credenciais
            email_field.clear()
            email_field.send_keys(PRO_USER)
            password_field.clear()
            password_field.send_keys(PRO_PASS)
            
            # Submeter formulário
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "client-submit"))
            )
            login_button.click()
            
            logger.info("Login realizado com sucesso!")
            
            # Aguardar e selecionar empresa
            logger.info("Selecionando empresa...")
            wait_short = WebDriverWait(self.driver, 10)
            dropdown_container = wait_short.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".selectize-control.form-control.single.plugin-restore_on_backspace")
            ))
            dropdown_container.click()
            
            dropdown_opcoes = wait_short.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".selectize-dropdown")
            ))
            opcao = dropdown_opcoes.find_element(By.XPATH, ".//div[contains(text(),'MF - STIHL SERVIÇOS')]")
            opcao.click()
            
            logger.info("Empresa selecionada com sucesso!")
            
            logger.info("Login realizado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro no login: {e}")
            return False
    
    def navigate_to_reports(self):
        """Navega para a página de relatórios"""
        try:
            logger.info("Navegando para página de relatórios...")
            self.driver.get(PRO_CHECKLIST_URL)
            
            # Aguardar página carregar
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            logger.info("Página de relatórios carregada")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao navegar para relatórios: {e}")
            return False
    
    def apply_filters(self, data_inicio, data_fim):
        """Aplica filtros de data na página"""
        try:
            logger.info(f"Aplicando filtros: {data_inicio} até {data_fim}")
            
            # Usar JavaScript para definir as datas (mais confiável)
            script = f'''
            document.getElementById("beginDate").value = "{data_inicio}";
            document.getElementById("beginDate").dispatchEvent(new Event('change'));
            
            document.getElementById("endDate").value = "{data_fim}";
            document.getElementById("endDate").dispatchEvent(new Event('change'));
            '''
            self.driver.execute_script(script)
            
            # Aguardar um pouco para o JavaScript processar
            time.sleep(1)
            
            # Clicar no botão de filtrar
            wait_short = WebDriverWait(self.driver, 10)
            botao_filtrar = wait_short.until(EC.element_to_be_clickable((By.ID, "button-filter")))
            botao_filtrar.click()
            
            # Aguardar resultados carregarem
            time.sleep(3)
            
            logger.info("Filtros aplicados com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao aplicar filtros: {e}")
            return False
    
    def export_data(self):
        """Realiza a exportação dos dados"""
        try:
            logger.info("Iniciando exportação...")
            
            # Limpar pasta de downloads antes da exportação
            for file in glob.glob(os.path.join(CHROME_DOWNLOAD_PATH, "*.xls")):
                os.remove(file)
                
            for file in glob.glob(os.path.join(CHROME_DOWNLOAD_PATH, "*.xlsx")):
                os.remove(file)
            
            # Clicar no botão de exportar Excel
            wait_short = WebDriverWait(self.driver, 10)
            botao_export = wait_short.until(EC.element_to_be_clickable((By.ID, "button-export-excel")))
            botao_export.click()
            
            logger.info("Aguardando o download do arquivo...")
            
            # Aguardar download completar (lógica otimizada do código fornecido)
            tempo_espera = 0
            arquivo_baixado = None
            
            while tempo_espera < 600:  # Espera por no máximo 600 segundos (10 minutos)
                # Verificar se há arquivos .crdownload (download em progresso)
                if any(f.endswith('.crdownload') for f in os.listdir(CHROME_DOWNLOAD_PATH)):
                    time.sleep(1)
                    tempo_espera += 1
                    continue
                
                # Procurar arquivos Excel baixados
                lista_arquivos = [
                    f for f in os.listdir(CHROME_DOWNLOAD_PATH)
                    if f.endswith(('.xls', '.xlsx')) and not f.startswith('~$')
                ]
                
                if lista_arquivos:
                    arquivo_baixado = os.path.join(CHROME_DOWNLOAD_PATH, lista_arquivos[0])
                    logger.info(f"Download concluído: {arquivo_baixado}")
                    break
                    
                time.sleep(1)
                tempo_espera += 1
            
            if not arquivo_baixado:
                raise Exception("O download do arquivo demorou muito ou falhou.")
            
            return arquivo_baixado
                
        except Exception as e:
            logger.error(f"Erro na exportação: {e}")
            return None
    
    def process_excel_file(self, file_path):
        """Processa o arquivo Excel baixado"""
        try:
            if not file_path or not os.path.exists(file_path):
                logger.error("Arquivo não encontrado")
                return False
            
            logger.info(f"Processando arquivo: {file_path}")
            
            # Verificar tamanho do arquivo
            file_size = os.path.getsize(file_path)
            logger.info(f"Tamanho do arquivo: {file_size} bytes")
            
            if file_size == 0:
                logger.error("Arquivo está vazio")
                return False
            
            # Determinar o engine baseado na extensão
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.xls':
                # Para arquivos .xls, tentar múltiplas abordagens
                df = None
                
                # Tentativa 1: pyxlsb (mais robusto)
                try:
                    df = pd.read_excel(file_path, engine='pyxlsb')
                    logger.info(f"Arquivo .xls lido com pyxlsb. Linhas: {len(df)}")
                except Exception as e:
                    logger.warning(f"Falha ao ler com pyxlsb: {e}")
                    
                    # Tentativa 2: xlrd com ignore_workbook_corruption
                    try:
                        import xlrd
                        workbook = xlrd.open_workbook(file_path, ignore_workbook_corruption=True)
                        sheet = workbook.sheet_by_index(0)
                        
                        # Converter para DataFrame
                        data = []
                        headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
                        
                        for row in range(1, sheet.nrows):
                            row_data = [sheet.cell_value(row, col) for col in range(sheet.ncols)]
                            data.append(row_data)
                        
                        df = pd.DataFrame(data, columns=headers)
                        logger.info(f"Arquivo .xls lido com xlrd (ignore corruption). Linhas: {len(df)}")
                    except Exception as e2:
                        logger.error(f"Erro ao ler arquivo .xls com xlrd: {e2}")
                        return False
                
                if df is None:
                    logger.error("Não foi possível ler o arquivo .xls com nenhum método")
                    return False
            else:
                # Para arquivos .xlsx, usar openpyxl
                try:
                    df = pd.read_excel(file_path, engine='openpyxl')
                    logger.info(f"Arquivo .xlsx lido com openpyxl. Linhas: {len(df)}")
                except Exception as e:
                    logger.error(f"Erro ao ler arquivo .xlsx: {e}")
                    return False
            
            if len(df) == 0:
                logger.warning("Arquivo Excel não contém dados")
                return False
            
            # Salvar como arquivo final
            arquivo_final = os.path.join(os.path.dirname(file_path), '..', 'exportacao.xlsx')
            df.to_excel(arquivo_final, index=False, engine='openpyxl')
            logger.info(f"Dados salvos em: {arquivo_final}")
            
            logger.info("Dados processados com sucesso")
            return True
                
        except Exception as e:
            logger.error(f"Erro ao processar arquivo: {e}")
            return False
    
    def run(self):
        """Executa o processo completo de coleta"""
        try:
            # Configurar driver
            if not self.setup_driver():
                return False
            
            # Fazer login
            if not self.login():
                return False
            
            # Navegar para relatórios
            if not self.navigate_to_reports():
                return False
            
            # Aplicar filtros para o mês atual
            hoje = datetime.today()
            primeiro_dia = hoje.replace(day=1).strftime("%d/%m/%Y")
            ultimo_dia = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1]).strftime("%d/%m/%Y")
            
            data_inicio = primeiro_dia
            data_fim = ultimo_dia
            
            logger.info(f"Coletando dados do período: {data_inicio} até {data_fim}")
            
            if not self.apply_filters(data_inicio, data_fim):
                return False
            
            # Exportar dados
            downloaded_file = self.export_data()
            if not downloaded_file:
                return False
            
            # Processar arquivo
            if not self.process_excel_file(downloaded_file):
                return False
            
            logger.info("Coleta realizada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro durante a coleta: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Driver fechado")

def main():
    """Função principal"""
    logger.info("Iniciando coletor com Selenium")
    
    max_tentativas = 3
    for tentativa in range(1, max_tentativas + 1):
        logger.info(f"Tentativa {tentativa}/{max_tentativas}")
        
        coletor = ColetorSelenium()
        
        if coletor.run():
            logger.info("Coleta concluída com sucesso")
            return 0
        else:
            logger.error(f"Tentativa {tentativa} falhou")
            if tentativa < max_tentativas:
                logger.info("Aguardando 30 segundos antes da próxima tentativa...")
                time.sleep(30)
    
    logger.error("Todas as tentativas falharam")
    return 1

if __name__ == "__main__":
    exit(main())