import os
import json
import requests
import logging
from packaging import version
import shutil
from tqdm import tqdm
import psutil  # Biblioteca para lidar com processos no sistema
import time

# Configuração de logging
logging.basicConfig(filename='atualizador.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

GITHUB_REPO = "Raos48/encaminha_diligencia"
CONFIG_FILE = "version.json"
UPDATE_INFO_FILE = "update_available.json"
MAIN_EXE = "encaminha_diligencia.exe"

CURRENT_DIR = os.getcwd()  # Diretório do updater.exe (onde ele está sendo executado)
MAIN_EXE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))  # Diretório do executável principal


def get_current_version():
    try:
        config_path = os.path.join(MAIN_EXE_DIR, CONFIG_FILE)
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('version', '1.0.0')
    except Exception as e:
        logging.error(f"Erro ao ler versão atual: {e}")
        return '1.0.0'


def check_for_update():
    try:
        current_version = get_current_version()
        print(f"Versão atual: {current_version}")

        # Verificar última versão no GitHub
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(api_url, timeout=10)

        if response.status_code == 200:
            latest_release = response.json()
            latest_version = latest_release['tag_name'].replace('v', '')

            if version.parse(latest_version) > version.parse(current_version):
                print(f"Nova versão disponível: {latest_version}")

                # Escrever a informação da nova versão em um arquivo
                update_info_path = os.path.join(MAIN_EXE_DIR, UPDATE_INFO_FILE)
                with open(update_info_path, 'w') as update_file:
                    json.dump({"update_available": True, "version": latest_version,
                               "download_url": latest_release['assets'][0]['browser_download_url']},
                              update_file)
                return True
            else:
                print("Nenhuma atualização disponível. Sistema já está na versão mais recente.")
                input("Aperte ENTER para continuar...")
                return False
        else:
            print("Erro ao acessar API do GitHub para verificar atualizações.")
            input("Aperte ENTER para continuar...")
            return False

    except Exception as e:
        logging.error(f"Erro ao verificar atualização: {str(e)}")
        input("Aperte ENTER para continuar...")
        return False


def download_file_with_progress(url, local_filename):
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            block_size = 1024  # Tamanho do bloco de download (1 KB)

            with open(local_filename, 'wb') as f, tqdm(
                desc="Baixando atualização",
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for chunk in r.iter_content(chunk_size=block_size):
                    f.write(chunk)
                    bar.update(len(chunk))

        # Verificar se o arquivo foi baixado
        if os.path.exists(local_filename):
            logging.info(f"Download concluído: {local_filename}")
            return True
        else:
            logging.error(f"Arquivo não encontrado após download: {local_filename}")
            return False

    except Exception as e:
        logging.error(f"Erro ao baixar o arquivo: {e}")
        input("Aperte ENTER para continuar...")
        return False


def close_running_process(process_name):
    """Função para fechar um processo específico pelo nome."""
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] == process_name:
                print(f"Encerrando processo {process_name} (PID: {proc.info['pid']})")
                proc.terminate()  # Tentar encerrar o processo de forma segura
                proc.wait(timeout=5)  # Esperar o processo encerrar
                print(f"Processo {process_name} encerrado com sucesso.")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            logging.error(f"Não foi possível encerrar o processo {process_name}: {e}")
            input("Aperte ENTER para continuar...")


def apply_update():
    try:
        update_info_path = os.path.join(MAIN_EXE_DIR, UPDATE_INFO_FILE)

        if os.path.exists(update_info_path):
            with open(update_info_path, 'r') as f:
                update_info = json.load(f)

            if update_info.get("update_available"):
                print("Iniciando o processo de atualização...")
                download_url = update_info["download_url"]

                # Caminho completo para salvar a nova versão no mesmo diretório do updater.exe
                temp_path = os.path.join(CURRENT_DIR, MAIN_EXE + ".new")

                # Baixar a nova versão com barra de progresso
                if download_file_with_progress(download_url, temp_path):
                    print("Download concluído com sucesso")

                    # Verificar e fechar o executável se estiver rodando
                    close_running_process(MAIN_EXE)

                    # Caminho do executável principal que deve ser substituído
                    main_exe_path = os.path.join(MAIN_EXE_DIR, MAIN_EXE)

                    # Garantir que o arquivo existe antes de mover
                    if not os.path.exists(temp_path):
                        raise FileNotFoundError(f"Arquivo baixado não encontrado: {temp_path}")

                    # Substituir executável antigo
                    if os.path.exists(main_exe_path):
                        os.remove(main_exe_path)  # Remover o executável antigo

                    shutil.move(temp_path, main_exe_path)
                    logging.info(f"Arquivo atualizado movido para: {main_exe_path}")

                    # Atualizar versão no arquivo de configuração
                    save_current_version(update_info["version"])

                    # Remover o arquivo de atualização disponível
                    os.remove(update_info_path)

                    print("Atualização aplicada com sucesso.")

                else:
                    print("Erro ao baixar a nova versão.")
                    input("Aperte ENTER para continuar...")

    except Exception as e:
        logging.error(f"Erro ao aplicar a atualização: {e}")
        input("Aperte ENTER para continuar...")

    input("\nAtualização realizada com sucesso. Aperte ENTER para sair.")


def save_current_version(version_str):
    try:
        config_path = os.path.join(MAIN_EXE_DIR, CONFIG_FILE)
        with open(config_path, 'w') as f:
            json.dump({'version': version_str}, f)
    except Exception as e:
        logging.error(f"Erro ao salvar versão: {e}")
        input("Aperte ENTER para continuar...")


if __name__ == "__main__":
    if check_for_update():
        apply_update()
