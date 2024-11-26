import os
import sys
import requests
import time
from packaging import version
import json
import subprocess
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    filename='atualizador.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

GITHUB_REPO = "Raos48/encaminha_diligencia"
MAIN_EXE = "encaminha_diligencia.exe"
CONFIG_FILE = "version.json"

def get_current_version():
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get('version', '1.0.0')
    except:
        return '1.0.0'

def save_current_version(version_str):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'version': version_str}, f)

def check_and_update():
    try:
        current_version = get_current_version()
        print(f"Versão atual: {current_version}")
        logging.info(f"Verificando atualizações. Versão atual: {current_version}")

        # Verificar última versão no GitHub
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code != 200:
            logging.error(f"Erro ao acessar API do GitHub: {response.status_code}")
            return False

        latest_release = response.json()
        latest_version = latest_release['tag_name'].replace('v', '')

        if version.parse(latest_version) <= version.parse(current_version):
            logging.info("Sistema já está atualizado")
            return True

        print(f"Nova versão disponível: {latest_version}")
        logging.info(f"Nova versão encontrada: {latest_version}")

        # Download da nova versão
        download_url = latest_release['assets'][0]['browser_download_url']
        new_exe = requests.get(download_url)
        
        if new_exe.status_code != 200:
            logging.error("Erro ao baixar nova versão")
            return False

        # Salvar nova versão temporariamente
        temp_path = MAIN_EXE + ".new"
        with open(temp_path, 'wb') as f:
            f.write(new_exe.content)

        # Aguardar o processo principal encerrar
        while True:
            if not any(MAIN_EXE.lower() in p.name().lower() for p in psutil.process_iter()):
                break
            time.sleep(1)

        # Fazer backup do executável atual
        backup_path = f"{MAIN_EXE}.backup"
        if os.path.exists(MAIN_EXE):
            os.rename(MAIN_EXE, backup_path)

        # Substituir pelo novo executável
        os.rename(temp_path, MAIN_EXE)
        
        # Atualizar versão no arquivo de configuração
        save_current_version(latest_version)
        
        logging.info(f"Atualização concluída para versão {latest_version}")
        print("Atualização concluída com sucesso!")
        
        # Iniciar o programa principal
        subprocess.Popen([MAIN_EXE])
        return True

    except Exception as e:
        logging.error(f"Erro durante atualização: {str(e)}")
        print(f"Erro durante a atualização: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        if not check_and_update():
            if os.path.exists(MAIN_EXE):
                subprocess.Popen([MAIN_EXE])
    except Exception as e:
        logging.error(f"Erro crítico: {str(e)}")
        if os.path.exists(MAIN_EXE):
            subprocess.Popen([MAIN_EXE])
