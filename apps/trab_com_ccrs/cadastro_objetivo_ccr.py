from selenium import webdriver
from selenium.webdriver.common.by import By
from apps.utilities.formatar_str import normalizar_texto_ascii, substituir_invisiveis_por_espaco
from apps.utilities.interagir import WebDriver_Interagir
from apps.trab_com_ccrs.geral_sigaa import menu_graduacao

def cadastrar_objetivo_ccr(driver: webdriver, ccr: dict, cadastro:bool = True):
    """
    Cadastra um objetivo de CCR no SIGAA.

    Args:
        driver (webdriver): Instância do webdriver.
        ccr (dict): Dados do CCR, incluindo código e objetivo.
        cadastro (bool): Se vai ser um cadastro ou uma alteração de objetivo
    Returns:
        dict: Resultado do cadastro, incluindo status e mensagem.
    """

    # Loop para que em caso de erro. O sistema tente cadastrar 3 vezes
    try:
        Navegador = WebDriver_Interagir(driver)
        contador = 0
        while contador<=3:
            menu_graduacao(Navegador)
            print("DEBUG: CADASTRANDO OBJETIVO CCR")
            retorno_sigaa = inserir_objetivo_sigaa(Navegador, ccr, cadastro)
            if retorno_sigaa['status'] != 'Erro':
                break
            contador += 1
        return retorno_sigaa
    except Exception as e:
        return {
               'status': 'Erro',
               'mensagem': f"Um erro inesperado ocorreu: {str(e)}"
            }

def inserir_objetivo_sigaa(Navegador: WebDriver_Interagir, ccr: dict, cadastro:bool):
    """
    Interage com o SIGAA para cadastrar um objetivo de CCR.

    Args:
        Navegador (WebDriver_Interagir): Instância do WebDriver_Interagir.
        ccr (dict): Dados do CCR, incluindo código e objetivo.
    Raises:
        Exception: Se ocorrer um erro durante a interação com o SIGAA.
    """
    try:
        # Navegar no menu de graduação
        Navegador.clicar_em((By.CSS_SELECTOR, "td#elgen-35 > a.ytab-right"), wait=10) # DDP
        Navegador.clicar_em((By.XPATH, "//li[.//text()[normalize-space()='Componentes Curriculares']]//a[normalize-space(text())='Cadastrar Programa de Componente']"), wait=10) 
        # Buscar ccr pelo codigo
        Navegador.escrever_em((By.ID, "buscaCC:codigo"), ccr['codigo'], wait=10)
        Navegador.clicar_em((By.ID, "buscaCC:busca"), wait=10)
        # Ver se a pesquisa foi bem sucedida
        pesquisou = Navegador.encontrar_elemento((By.CLASS_NAME, "infoAltRem"), wait=10)
        if pesquisou:
            periodo = Navegador.encontrar_elemento((By.CSS_SELECTOR, ".linhaPar > td:nth-child(1)"))
            # Se o periodo está preenchido é porque já tem objetivo cadastrado. Se está vazio, deve-se cadastrar
            if periodo.text == '':
                # Clicar em cadastrar, e ver se foi para a tela de cadastro
                Navegador.clicar_em((By.CSS_SELECTOR, r"#j_id_jsp_2120012169_1209\:cadastrar > img:nth-child(1)"))
                mudar_tela = Navegador.encontrar_elemento((By.XPATH, "//caption[normalize-space(text())='Dados do Programa']"))
                if mudar_tela:
                    return preencher_campos(Navegador, ccr)
                else:
                    raise Exception(f"Não foi possível acessar o campo de cadastro de Objetivo para o CCR {ccr['codigo']}")
                
            elif not cadastro:
                Navegador.clicar_em((By.CSS_SELECTOR, r"#j_id_jsp_2120012169_1209\:alterar > img:nth-child(1)"))
                mudar_tela = Navegador.encontrar_elemento((By.XPATH, "//caption[normalize-space(text())='Dados do Programa']"))
                if mudar_tela:
                    return preencher_campos(Navegador, ccr)
                else:
                    raise Exception(f"Não foi possível acessar o campo de cadastro de Objetivo para o CCR {ccr['codigo']}")
                
            else:
                print(f"Objetivo do CCR {ccr['codigo']} já cadastrado")
                return {
                    'status': "Sucesso",
                    'mensagem': "Objetivo Cadatrado"
                    }
        else:
            raise Exception(f"SIGAA não encontrou o CCR {ccr['codigo']}")          

    except Exception as e:
        Navegador.clicar_em((By.ID, "buscaCC:cancelar"), wait = 10)
        Navegador.ok_alerta(wait = 10)
        return {'status':"Erro" , 'mensagem': f"{str(e)}" }

def preencher_campos(Navegador: WebDriver_Interagir, ccr: dict):
    # Normalizar o texto do objetivo, e escrever no campo
    objetivo = ccr['objetivo']
    objetivo = substituir_invisiveis_por_espaco(objetivo)
    objetivo = normalizar_texto_ascii(objetivo)
    Navegador.limpar_imput((By.ID, "form:objetivo"), wait=10)
    Navegador.escrever_em((By.ID, "form:objetivo"), objetivo, wait=10)
    # Clicar na aba de conteúdo e verificar se clicou
    Navegador.clicar_em((By.CSS_SELECTOR, "td#elgen-11"))
    clicou_conteudo = Navegador.encontrar_elemento((By.CSS_SELECTOR, "td#elgen-11.on"), wait = 10)
    if clicou_conteudo:
        # Inserir o conteúdo que vai sempre ser o texto padrão 
        texto_padrao = "Conteúdo conforme apresentado no plano de curso do componente."
        Navegador.limpar_imput((By.ID, "form:conteudo"), wait=10)
        Navegador.escrever_em((By.ID, "form:conteudo"), texto_padrao, wait=10)
        if Navegador.clicar_em((By.ID, "form:Cadastrar")):
            return {
                'status': "Sucesso",
                'mensagem': "Objetivo Cadatrado"
                }
        elif Navegador.clicar_em((By.ID, "form:Alterar")):
            return {
                'status': "Sucesso",
                'mensagem': "Objetivo Alterado"
                }
        else:
            raise Exception(f"Erro ao cadastrar objetivo e conteúdo do CCR {ccr['codigo']}")
    else:
        raise Exception(f"Não foi possível acessar o campo de cadastro de Conteudo para o CCR {ccr['codigo']}")