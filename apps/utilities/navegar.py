import time

from bs4 import BeautifulSoup as bs
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from apps.utilities.log import logger


def navegar_menu(driver, cmd_menu_dic):
    met_modulo = cmd_menu_dic.get('met_modulo')
    modulo = cmd_menu_dic.get('modulo')
    met_submodulo = cmd_menu_dic.get('met_submodulo')
    submodulo = cmd_menu_dic.get('submodulo')
    met_aba = cmd_menu_dic.get('met_aba')
    aba = cmd_menu_dic.get('aba')
    met_funcionalidade = cmd_menu_dic.get('met_funcionalidade')
    funcionalidade = cmd_menu_dic.get('funcionalidade')
    erro = ''
    status = ''
    retorno = ''
    # Valida se tem que acessa o menu
    if met_modulo == 'get':
        driver.get(modulo)
    elif met_modulo != '':
        cmd_dict = {'metodo': met_modulo, 'componente': f'{modulo}', 'valor': '', 'tipo': 'nenhum',
                    'cmd_antes': '', 'cmd_princ': 'navegar', 'cmd_depois':'', 'espera_antes': 0, 'espera_entre': 0, 'espera_depois': 0,
                    'tentativas': 5, 'resposta_erro': 'Nenhuma', 'campo': 'Comando Buscar' }
        status, erro, retorno = tratar_componente(driver, cmd_dict)
    # Validar se tem que acessar o submódulo
    if erro == '':
        if met_submodulo == 'get':
            driver.get(submodulo)
        elif met_submodulo != '':
            cmd_dict = {'metodo': met_submodulo, 'componente': f'{submodulo}', 'valor': '', 'tipo': 'nenhum',
                        'cmd_antes': '', 'cmd_princ': 'clicar', 'cmd_depois': '', 'espera_antes': 0, 'espera_entre': 0, 'espera_depois': 0,
                        'tentativas': 5, 'resposta_erro': 'Nenhuma', 'campo': 'Comando Buscar'}
            status, erro, retorno = tratar_componente(driver, cmd_dict)
    # Validar se tem que acessar a aba
    if erro == '':
        if met_aba == 'get':
            driver.get(aba)
        elif met_aba != '':
            cmd_dict = {'metodo': met_aba, 'componente': f'{aba}', 'valor': '', 'tipo': 'nenhum',
                        'cmd_antes': '', 'cmd_princ': 'clicar', 'cmd_depois': '', 'espera_antes': 0, 'espera_entre': 0, 'espera_depois': 0,
                        'tentativas': 5, 'resposta_erro': 'Nenhuma', 'campo': 'Comando Buscar'}
            status, erro, retorno = tratar_componente(driver, cmd_dict)
    # Validar se tem que acessar a funcionalidade
    if erro == '':
        if met_funcionalidade == 'get':
            driver.get(funcionalidade)
        elif met_funcionalidade != '':
            cmd_dict = {'metodo': met_funcionalidade, 'componente': f'{funcionalidade}', 'valor': '', 'tipo': 'nenhum',
                        'cmd_antes': '', 'cmd_princ': 'clicar', 'cmd_depois': '', 'espera_antes': 0, 'espera_entre': 0, 'espera_depois': 0,
                        'tentativas': 5, 'resposta_erro': 'Nenhuma', 'campo': 'Comando Buscar'}
            status, erro, retorno = tratar_componente(driver, cmd_dict)
    return status, erro


def tratar_componente(driver, cmd_dict):
    # recupera os comandos do dicionário "alvo"
    metodo = cmd_dict.get('metodo')
    componente = cmd_dict.get('componente')
    valor = cmd_dict.get('valor')
    tipo_dado = cmd_dict.get('tipo')
    cmd_antes = cmd_dict.get('cmd_antes')
    cmd_princ = cmd_dict.get('cmd_princ')
    cmd_depois = cmd_dict.get('cmd_depois')
    espera_antes = int(cmd_dict.get('espera_antes'))
    espera_entre = int(cmd_dict.get('espera_entre'))
    espera_depois = int(cmd_dict.get('espera_depois'))
    tentativas = int(cmd_dict.get('tentativas'))
    resposta_erro = cmd_dict.get('resposta_erro')
    campo = cmd_dict.get('campo')
    nro_loops = 0
    alvo = ''
    status = ''
    erro = ''
    retorno = ''
    # Ver se precisa esperar antes de executar
    if espera_antes > 0:
        time.sleep(espera_antes)
    # Testa se o comando é de navegar, pois desta forma não precisa usar os comandos de interação e sim apenas de get
    if cmd_princ == 'navegar':
        driver.get(componente)
        # após abrir a página desejada, muda o comando para validar tela apra ver se a tela desejada estava disponível
        cmd_princ = 'validar_tela'
    # Loop para achar o objeto
    while nro_loops <= tentativas:
        try:
            # Procuro o alvo pelo método escolhido
            if metodo == 'xpath':
                alvo = driver.find_element(By.XPATH, componente)
                texto = driver.find_element(By.XPATH, componente).text
                nro_loops = (tentativas + 1)
            if metodo == 'name':
                alvo = driver.find_element(By.NAME, componente)
                nro_loops = (tentativas + 1)
            if metodo == 'id':
                alvo = driver.find_element(By.ID, componente)
                nro_loops = (tentativas + 1)
            if metodo == 'selector':
                alvo = driver.find_element(By.CSS_SELECTOR, componente)
                nro_loops = (tentativas + 1)
        except:
            nro_loops = nro_loops + 1
    if alvo:
        # Verifica se é para abrir o editor do javascipt
        if cmd_antes == 'js_iniciar':
            alvo.send_keys(Keys.CONTROL + Keys.SHIFT + 'j')
        #  Verifrica se tem que fazer algo antes do comando principal
        if cmd_antes == 'limpar':
            alvo.send_keys(Keys.CONTROL + Keys.HOME)
            alvo.send_keys(Keys.CONTROL + Keys.SHIFT + Keys.END)
            alvo.send_keys(Keys.DELETE)
        # Executa o comando principal
        # Se for digitar algo no componente
        if cmd_princ == 'digitar':
            # Verifica se precisa trocar o tipo de dado
            if tipo_dado == 'string':
                valor = str(valor)
            elif tipo_dado == 'boolean':
                if valor == 'False':
                    valor = False
                else:
                    valor = True
            alvo.send_keys(valor)
        # Se for dar um click no componente
        elif cmd_princ == 'clicar':
            alvo.click()
        elif cmd_princ == 'colar':
            alvo.send_keys(Keys.CONTROL, 'v')
        # Valida se é um comando de teclas de controle
        elif cmd_princ == 'Ctrl':
            alvo.send_keys(Keys.CONTROL).send_keys(f'{valor}')
        # Pegar o conteúdo do campo
        elif cmd_princ == 'capturar_valor':
            retorno = alvo.text
        # Se for pegar o conteúdo do componente (scrapping)
        elif cmd_princ == 'validar_campo':
            if alvo.text != valor:
                status = 'Não foi possível encontrar o valor procurado no objeto indicado'
                erro = 'valor inválido'
        # se for validar se uma tela abriu
        elif cmd_princ == 'validar_tela':
            if alvo.text == valor:
                status = 'Não foi possível encontrar a interface alvo da aplicação'
                erro = 'janela não encontrada'
        elif cmd_princ == 'capturar_conteudo':
            retorno = bs(driver.page_source, 'html.parser')
        else:
            pass
        # Executa o comando após o principal
        if cmd_depois != '':
            # Valida se tem tempo de espera antes do segundo comando
            if espera_entre > 0:
                time.sleep(espera_entre)
            # Executa o comando TAB
            if cmd_depois == 'ENTER':
                alvo.send_keys(Keys.ENTER)
            # Executa o comando TAB
            if cmd_depois == 'TAB':
                alvo.send_keys(Keys.TAB)
            # Executa o comando arrow-down
            if cmd_depois == 'ARROW_DOWN':
                time.sleep(espera_depois)
                alvo.send.keys(Keys.ARROW_DOWN)
                alvo.click()
            if cmd_depois == 'js_finalizar':
                alvo.send_keys(Keys.CONTROL + Keys.SHIFT + 'j')
        # Testa para ver se precisa dar um tempo de espera
        if espera_depois > 0:
            time.sleep(espera_depois)
        status = ''
    else:
        erro = 'componente inválido'
        if resposta_erro == 'Nenhuma':
            status = status + 'Não encontrou o componente web. '
        else:
            status = status + f'Não encontrou o componente: {campo} : {valor}. '
            registrar_acao('E', status)
    return status, erro, retorno


def registrar_acao(tipo, status):
    logger(tipo, status)
