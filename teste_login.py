#!/usr/bin/env python3
"""
Script de teste para verificar se o login está funcionando com as novas configurações
"""

import sys
import os
from dotenv import load_dotenv

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Carregar variáveis de ambiente
load_dotenv()

from coletor_selenium import ColetorSelenium

def teste_login():
    """Testa apenas o login do sistema"""
    print("🔧 Iniciando teste de login...")
    
    coletor = ColetorSelenium()
    
    try:
        # 1. Configurar driver
        print("📋 Configurando driver Chrome...")
        if not coletor.setup_driver():
            print("❌ Erro ao configurar driver")
            return False
        
        # 2. Tentar fazer login
        print("🔐 Tentando fazer login...")
        if coletor.login():
            print("✅ Login realizado com sucesso!")
            
            # Verificar se chegou na página correta
            current_url = coletor.driver.current_url
            page_title = coletor.driver.title
            
            print(f"📍 URL atual: {current_url}")
            print(f"📄 Título da página: {page_title}")
            
            return True
        else:
            print("❌ Falha no login")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False
    
    finally:
        # Fechar driver
        if coletor.driver:
            print("🔒 Fechando navegador...")
            coletor.driver.quit()

if __name__ == "__main__":
    sucesso = teste_login()
    if sucesso:
        print("\n🎉 Teste de login concluído com sucesso!")
        sys.exit(0)
    else:
        print("\n💥 Teste de login falhou!")
        sys.exit(1)