import json
import os
import re
import time
import traceback
import warnings
from datetime import date

import chromedriver_autoinstaller
import urllib3
from colorama import init, Fore, Back
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import openpyxl

warnings.filterwarnings("ignore", category=DeprecationWarning)
urllib3.disable_warnings()
chromedriver_autoinstaller.install()
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')

init()

service = Service(executable_path=chromedriver_autoinstaller.install())
driver = webdriver.Chrome(options=options, service=service)
driver.maximize_window()

timeout = 30

caminho_arquivo = 'protocolos.xlsx'
workbook = openpyxl.load_workbook(caminho_arquivo)
worksheet = workbook['Plan1']

linha = 2

while True:
    try:
        protocolo = worksheet.cell(row=linha, column=2).value
        status_coluna3 = worksheet.cell(row=linha, column=3).value
        id = worksheet.cell(row=linha, column=1).value
        
        if not protocolo:
            input("Finalizado!")
            break

        if status_coluna3:
            print(f"ID {id} já processado, pulando...")
            linha += 1
            continue
        
        print("======================================================================")
        print(f"Iniciando processamento do Protocolo:id Nº{id} - {protocolo}")
        driver.get("https://esisrec.inss.gov.br/esisrec/pages/painel_de_entrada/consultar_painel_de_entrada.xhtml")
        ActionChains(driver).send_keys(Keys.HOME).perform()
        
        print("Busca Processo...")
        campo_busca = driver.find_element(By.ID, "formBuscaRapida:buscaRapida")
        campo_busca.clear()
        campo_busca.send_keys(protocolo)
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        driver.find_element(By.ID, "formBuscaRapida:btBuscaRapida").click()
        time.sleep(2)

        e_nb = driver.find_element(By.ID, "formProcesso:numeroIdentificacao").get_attribute("value")
        unidade = driver.find_element(By.ID, "formProcesso:orgaoAtual").text
        driver.execute_script("window.scrollTo(0, 1000)")
        
        print("Clicar em Analisar...")
        element = driver.find_element(By.ID, "formProcesso:analisarAnexarDocumentos")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", element)
        time.sleep(1)
        element.click()
        time.sleep(2)
        
        print("Lançar Evento...")
        driver.find_element(By.XPATH, "//span[@id='iptEventoLancado']/button").click()
        time.sleep(1)
        
        print("Selecionar Evento Diligencia não cumprida...")
        driver.find_element(By.XPATH, "//span[@id='iptEventoLancado_panel']/ul/li[28]").click()
        
        data_formatada = date.today().strftime("%d/%m/%Y")
        driver.execute_script("scroll(0,500)")
        time.sleep(1)
        
        driver.find_element(By.LINK_TEXT, "Digitar um Documento").click()
        time.sleep(1)
        driver.find_element(By.ID, "anexar_docs:tipoDocDigitarDocumentos_label").click()                  
        time.sleep(1)
        
        print("Selecionar Documento tipo DESPACHO...")
        driver.find_element(By.ID, "anexar_docs:tipoDocDigitarDocumentos_40").click()
        time.sleep(5)
        
        print("Redigir Despacho...")
        editor = driver.find_element(By.XPATH, "//div[@id='anexar_docs:textEditor_editor']/div")
        editor.clear()
        texto_despacho = (
            f'\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t{data_formatada}\n\n\n'
            f'Protocolo: {protocolo}\nRecorrente: INSTITUTO NACIONAL DO SEGURO SOCIAL – INSS\n\n\n'
            f'\tDevolução do processo de recurso conforme solicitação do órgão julgador.'
        )
        editor.send_keys(texto_despacho)
        time.sleep(1)
        
        print("Anexar Documento...")
        driver.find_element(By.ID, 'anexar_docs:digitar_doc_anexar').click()
        time.sleep(1)
        
        driver.execute_script("window.scrollTo(0, 1000)")
        print("Movimentar em Bloco...")
        driver.find_element(By.ID, 'btnMovimentarEmBloco').click()
        time.sleep(1)
        
        print("Aguardar retorno...")
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div/div[2]/div/ul/li/span")))
        time.sleep(1)
        
        mensagem_retorno = driver.find_element(By.XPATH, "/html/body/div[3]/div/div[2]/div/ul/li/span").text
        if mensagem_retorno != "Processo movimentado com sucesso.":
            print("Retorno falhou, tentando movimentar novamente...")
            driver.find_element(By.ID, 'btnMovimentarEmBloco').click()
        time.sleep(1)
        
        print("Encaminhamento bem sucedido, salvando informações na planilha...")
        worksheet.cell(row=linha, column=3).value = mensagem_retorno
        worksheet.cell(row=linha, column=4).value = driver.find_element(By.XPATH, "/html/body/div[3]/div/form/div/div[1]/div[1]/div/div[1]/div[6]/div[1]/div/span").text
        
        elemento1 = mensagem_retorno
        elemento2 = driver.find_element(By.XPATH, '/html/body/div[3]/div/form/div/div[1]/div[1]/div/div[1]/div[6]/div[1]/div/span').text
        print(f"{elemento1} - {elemento2}")
        
        linha += 1
        workbook.save(caminho_arquivo)

    except Exception as e:
        print("\nOcorreu um erro durante a execução:")
        print(f"Erro: {str(e)}")
        print(f"Detalhes do erro:\n{traceback.format_exc()}")
        input("\nPressione ENTER para continuar...")
        
        erro_resumido = str(e).split('\n')[0][:100]
        worksheet.cell(row=linha, column=3).value = f"ERRO: {erro_resumido}"
        workbook.save(caminho_arquivo)
        linha += 1
        continue
