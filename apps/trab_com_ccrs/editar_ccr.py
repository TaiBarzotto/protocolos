from re import I
from tkinter import N
import unicodedata
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from apps.utilities.formatar_str import normalizar_texto_ascii, substituir_invisiveis_por_espaco
from apps.trab_com_ccrs.cadastro_ccr import ( 
    insere_refs,
    inserir_avaliacoes_e_ementa,
    inserir_horas,
    inserir_discente_orientada,
    inserir_orientacao_docente,
    verificar_ccr
    )
from apps.utilities.interagir import WebDriver_Interagir
from apps.trab_com_ccrs.geral_sigaa import menu_graduacao

def verificar_status_ccr(Navegador, wait_time=10):
    """
    Verifica o status no SIGAA esperando por um dos dois elementos:
    - Elemento de erro: 'ul.erros li'
    - Elemento de sucesso: 'ul.info li'

    Retorna:
    - O texto da mensagem de sucesso se o elemento de sucesso for encontrado.
    - O texto da mensagem de erro se o elemento de erro for encontrado.
    - None se nenhum dos dois elementos for encontrado dentro do tempo limite.
    """
    
    erro = Navegador.encontrar_elemento((By.CSS_SELECTOR, 'ul.erros li'), wait=wait_time)
    if erro is not None:
        return {
            'status': 'Erro',
            'mensagem': f"{erro.text}"
        }

    # Tenta encontrar o elemento de sucesso
    info = Navegador.encontrar_elemento((By.CSS_SELECTOR, 'ul.info li'), wait=wait_time)
    if info:
        return {
            'status': 'Sucesso',
            'mensagem': f"{info.text}"
        }

    return None

def editar_ccr_sigaa(driver: webdriver, ccr: dict, senha:str):
    Navegador = WebDriver_Interagir(driver)
    tipo = {}

    # Verificando o tipo do ccr com base no nome e nas horas
    nome = ccr.get('descricao', '')
    hrs_presencial_teorica= ccr.get('hrs_presencial_teorica',0)
    hrs_presencial_pratica= ccr.get('hrs_presencial_pratica',0)
    hrs_presencial_extensao= ccr.get('hrs_presencial_extensao',0)
    hrs_ead_teorica= ccr.get('hrs_ead_teorica',0)
    hrs_ead_pratica= ccr.get('hrs_ead_pratica',0)
    hrs_estagio_extensionista= ccr.get('hrs_estagio_extensionista',0)
    hrs_estagio_ead= ccr.get('hrs_estagio_ead',0)
    hrs_estagio_presencial= ccr.get('hrs_estagio_presencial',0)
    hrs_tcc_discente_orientada= ccr.get('hrs_tcc_discente_orientada')

    aulas = hrs_presencial_teorica + hrs_presencial_pratica + hrs_presencial_extensao + hrs_ead_teorica + hrs_ead_pratica 
    estagio =  hrs_estagio_extensionista + hrs_estagio_ead + hrs_estagio_presencial 
    tcc =  hrs_tcc_discente_orientada

    if estagio != 0 or tcc != 0:
        tipo['componente'] = 'atividade'

        if aulas != 0:
            tipo['aula'] = True
        else:
            tipo['aula'] = False

        if estagio!= 0 and tcc==0:
            tipo['atividade'] = 'estagio'
            if tipo['aula']:
                tipo['forma_participacao'] = 'coletiva'
            elif 'internato' in nome.lower():
                tipo['forma_participacao'] = 'internato'
            else:
                tipo['forma_participacao'] = 'individual'
        elif estagio== 0 and tcc!=0:
            if tipo['aula']:
                tipo['atividade'] = 'integradora'
                if 'internato' in nome.lower():
                    tipo['forma_participacao'] = 'internato'
                else:
                    tipo['forma_participacao'] = 'coletiva'
            else:
                tipo['atividade'] = 'tcc'
                tipo['forma_participacao'] = 'individual'

    else:
        tipo['aula'] = True
        tipo['componente'] = 'modulo'

    try:
        # Clicar no botão ciente
        ciente = Navegador.encontrar_elemento((By.XPATH, "//button[text()='Ciente']"), wait=10) 
        ac = Navegador.action_chains()
        ac.move_to_element(ciente).perform()
        ac.click(ciente).perform()

        # Acessar o menu de graduação e a aba DDP
        Navegador.clicar_em((By.CSS_SELECTOR, "li.graduacao.on > a"), wait=10) # Graduação 
        Navegador.clicar_em((By.CSS_SELECTOR, "td#elgen-35 > a.ytab-right"), wait=10) # DDP
        
        # Inicializar retorno
        retorno = {}
        
        # Loop para executar a função de cadastro, fazer verificação do CCR, e em caso de erro, tentar novamente até 3x
        contador = 0
        while True:
            print("DEBUG: Editando CCR")
            retorno = editar_ccr(Navegador, ccr, tipo, driver)
            print(f"RETORNO:{retorno}\n")
            # Se não deu erro e as informações cadastradas batem com a do dicionario
            if (verificar_ccr(ccr, Navegador)) and (retorno is None):
                break

            contador += 1

            try:
                if Navegador.clicar_em((By.ID, "form:cancelar2"), wait=3):
                    Navegador.ok_alerta(wait=3)
            except Exception as e:
                print(f"Erro ao clicar em cancelar2: {e}")
                pass  # Continua tentando

            if contador >= 3: 
                # Se não consegui cadastrar, voltar para o menu de graduação e retornar o erro
                menu_graduacao(Navegador)
                return retorno

        # Se as informações do CCR estão de acordo, preencher a senha e clicar em cadastrar
        Navegador.escrever_em((By.ID, "form:senha"), senha, wait=10)
        if Navegador.clicar_em((By.ID, "form:cadastrar"), wait=10):
            menu_graduacao(Navegador)
            return {
                'status': 'Sucesso',
                'mensagem': 'CCR cadastrada com sucesso'
            }
        else:
            menu_graduacao(Navegador)
            return {
                'status': 'Erro',
                'mensagem': 'Erro inesperado ao preencher a senha e clicar em editar'
            }


    except Exception as e:
        print("Erro ao editar CCR:", e)
        return {
           'status': 'Erro',
           'mensagem': f'Erro ao editar CCR: {e}'
        }

def editar_ccr(Navegador: WebDriver_Interagir, ccr: dict, tipo: dict, driver: webdriver):
    retorno = {}
    # Verificar se está no menu de graduação e clicar em cadastrar na parte dos Componentes Curriculares
    Navegador.encontrar_elemento((By.XPATH, '//h2[text()="Menu de Graduação"]'), wait=10)
    Navegador.clicar_em((By.XPATH, "//li[.//text()[normalize-space()='Componentes Curriculares']]//a[normalize-space(text())='Listar/Alterar']"), wait=10) # Cadastrar

    Navegador.limpar_imput((By.ID, "formBusca:codigoComponente"), wait=10)
    Navegador.escrever_em((By.ID, "formBusca:codigoComponente"), ccr['codigo'], wait=10)
    Navegador.clicar_em((By.ID, "formBusca:busca"))

    pesquisou = Navegador.encontrar_elemento((By.CLASS_NAME, "infoAltRem"), wait=10)
    if pesquisou:
        Navegador.clicar_em((By.XPATH, "//a[@id = 'detalharComponenteCurricular:Alterar']//img"))

    # Verificar se acessou o formulário de castro de CCR
    aba_cadastro = Navegador.encontrar_elemento((By.XPATH, '//h2[@class="title"][contains(text(), "Cadastro de Componente Curricular")]'), wait=10)
    if not aba_cadastro:
        retorno['status'] = 'Erro'
        retorno['mensagem'] = 'Não foi possível acessar a sessão de edição de CCRs'
        return retorno
    
    # Chamar as funções de cadastro, e caso elas retornem algo, retornar o erro
    resposta_selecao = Navegador.clicar_em((By.ID, "form:avancar"), wait=10)
    if not resposta_selecao:
        retorno['status'] = 'Erro'
        retorno['mensagem'] = 'Erro ao avançar para a tela de edição de CCRs'
        return retorno

    resposta_referencias = analisa_refs(ccr, Navegador, driver)
    if resposta_referencias:
        retorno['status'] = 'Erro'
        retorno['mensagem'] = resposta_referencias
        return retorno

    resposta_insercao = inserir_cabecalho_ccr(ccr, Navegador)
    if resposta_insercao:
        retorno['status'] = 'Erro'
        retorno['mensagem'] = resposta_insercao
        return retorno
    
    if tipo['aula']:
        resposta_horas = inserir_horas(ccr, Navegador, driver)
        if resposta_horas:
            retorno['status'] = 'Erro'
            retorno['mensagem'] = resposta_horas
            return retorno
        if tipo['componente'] == 'atividade':
            resposta_discente_orientada = inserir_discente_orientada(ccr, Navegador, driver,1)
            if resposta_discente_orientada:
                retorno['status'] = 'Erro'
                retorno['mensagem'] = resposta_discente_orientada
                return retorno
            resposta_orientacao_docente = inserir_orientacao_docente(ccr, Navegador,driver, 1 )
            if resposta_orientacao_docente:
                retorno['status'] = 'Erro'
                retorno['mensagem'] = resposta_orientacao_docente
                return retorno
    else:    
        resposta_discente_orientada = inserir_discente_orientada(ccr, Navegador, driver)
        if resposta_discente_orientada:
            retorno['status'] = 'Erro'
            retorno['mensagem'] = resposta_discente_orientada
            return retorno
        resposta_orientacao_docente = inserir_orientacao_docente(ccr, Navegador, driver)
        if resposta_orientacao_docente:
            retorno['status'] = 'Erro'
            retorno['mensagem'] = resposta_orientacao_docente
            return retorno

    ementa= Navegador.encontrar_elemento((By.ID, 'form:ementa'), wait = 10) 
    ementa.clear()
    resposta_avaliacao = inserir_avaliacoes_e_ementa(ccr, Navegador)
    if resposta_avaliacao:
        retorno['status'] = 'Erro'
        retorno['mensagem'] = resposta_avaliacao
        return retorno  
    
    # Se não retornou é pq as partes foram executadas com sucesso
    Navegador.clicar_em((By.ID, "form:avancar"), wait=10)
    # Verificar se tem algum Pop up
    verificacao = verificar_status_ccr(Navegador, 5)
    print(f"DEBUG: VERIFICACAO: {verificacao}")
    if verificacao is None:
        return None
    else:
        return verificacao
       
def inserir_cabecalho_ccr(ccr : dict, Navegador : WebDriver_Interagir):
    print("DEBUG: INSERINDO CABECALHO")
    try:
        # Preencher os campos do cabeçalho com as informações do CCR
        campus = ccr.get('unidade', '')
        campus = campus.replace('CAMPUS', '').strip()
        Navegador.select_por_texto_parcial((By.ID, "form:unidades"), texto_parcial= "COORDENAÇÃO ACADÊMICA - " + campus, wait = 10)
        descricao = ccr.get('descricao', '')
        # SIGAA n aceita UTF-8, por isso precisa normalizar o texto
        utf_desc = normalizar_texto_ascii(descricao)
        utf_desc = substituir_invisiveis_por_espaco(utf_desc)
        nome = Navegador.encontrar_elemento((By.ID, "form:nome"), wait = 10)
        nome.clear()
        Navegador.escrever_em((By.ID, "form:nome"), utf_desc, wait = 10)

    except Exception as e:
        print(f"ERRO: {e}")
        return f"Erro ao selecionar inserir cabecalho: {e}"

def analisa_refs(ccr:dict, Navegador:WebDriver_Interagir, driver):
    print("DEBUG: ANALISANDO CCR")
    Navegador.encontrar_elementos((By.XPATH, "//table[caption[contains(text(), 'Nova Referência')]]"), wait = 15)
    referencias_basicas = ccr['referencias_basicas']
    referencias_complementares = ccr['referencias_complementares']
    try:
        remover_refs_existentes(Navegador, tipo = 'Basicas')
        remover_refs_existentes(Navegador, tipo = 'Complementares')

        print("DEBUG: Inserindo refs")
        insere_refs(referencias_basicas, Navegador, tipo = 'Basicas', driver = driver)
        insere_refs(referencias_complementares, Navegador, tipo = 'Complementares', driver = driver)
        return None
    
    except Exception as e:
        print(f"ERRO: {e}")
        return f"Erro ao inserir referencias {e}"

def remover_refs_existentes(Navegador:WebDriver_Interagir, tipo):
    try:
        print("DEBUG: ANALISANDO CCR-2")
        while Navegador.encontrar_elemento((By.XPATH, f"//table[@id='form:panelIR']//tbody//tr"), wait=5) != None:
            print(Navegador.encontrar_elemento((By.XPATH, f"//table[@id='form:panelIR']"), wait=5))
            bug_nova_ref = Navegador.encontrar_elementos((By.XPATH, "//table[caption[contains(text(), 'Nova Referência')]]"), wait = 3)
            if len(bug_nova_ref) > 1:
                Navegador.clicar_em((By.ID, "form:avancar"), wait=10)
                Navegador.clicar_em((By.ID, "form:dadosGerais"), wait=10)
                time.sleep(0.5)
                Navegador.encontrar_elemento((By.CSS_SELECTOR, '#info-sistema #tempoSessao'), wait=10)

            deleter_ref(Navegador)
    except Exception as e:
        print("ERRO EM remover_refs:", e)
        pass
    
def deleter_ref(Navegador):
    try:
        for i in range(5):
            elemento = Navegador.encontrar_elemento((By.XPATH, "//td/a[@title='Remover Referência']"), wait = 10)
            if elemento:
                Navegador.scrool_para_elemento(elemento)
                ac = Navegador.action_chains()
                ac.move_to_element(elemento).perform()
                ac.click(elemento).perform()
                excluiu = Navegador.ok_alerta(wait = 5)
                if excluiu:
                    break
    except Exception as e:
        print("ERRO EM deletar_ref:", e)
        pass
       