from re import I
import unicodedata
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException  , StaleElementReferenceException
from apps.utilities.formatar_str import normalizar_texto_ascii, substituir_invisiveis_por_espaco
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
        if erro.text.lower().startswith('já existe um componente curricular'):
            return {
              'status': 'Sucesso',
              'mensagem': f"{erro.text}"
            }
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

def cadastrar_ccr_sigaa(driver: webdriver, ccr: dict, senha:str):
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
            print("DEBUG: RECARREGANDO CCR")
            retorno = cadastrar_ccr(Navegador, ccr, tipo, driver)
            # Se deu um pop up de ccr já cadastrado
            if retorno is not None and retorno['status'] == 'Sucesso':
                menu_graduacao(Navegador)
                return {
                    'status': 'Sucesso',
                    'mensagem': 'CCR cadastrada com sucesso'
                }
            # Se não deu erro e as informações cadastradas batem com a do dicionario
            if (verificar_ccr(ccr,Navegador)) and (retorno is None):
                break
            contador += 1
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
                'mensagem': 'Erro inesperado ao preencher a senha e clicar em cadastrar'
            }


    except Exception as e:
        print("Erro ao cadastrar CCR:", retorno)
        return {
           'status': 'Erro',
           'mensagem': f'Erro ao cadastrar CCR: {e}'
        }

def cadastrar_ccr(Navegador: WebDriver_Interagir, ccr: dict, tipo: dict, driver: webdriver):
    retorno = {}
    # Verificar se está no menu de graduação e clicar em cadastrar na parte dos Componentes Curriculares
    Navegador.encontrar_elemento((By.XPATH, '//h2[text()="Menu de Graduação"]'), wait=10)
    Navegador.clicar_em((By.XPATH, "//li[.//text()[normalize-space()='Componentes Curriculares']]//a[normalize-space(text())='Cadastrar']"), wait=10) # Cadastrar

    # Verificar se acessou o formulário de castro de CCR
    aba_cadastro = Navegador.encontrar_elemento((By.XPATH, '//h2[@class="title"][contains(text(), "Cadastro de Componente Curricular")]'), wait=10)
    if not aba_cadastro:
        retorno['status'] = 'Erro'
        retorno['mensagem'] = 'Não foi possível acessar a sessão de cadastro de CCRs'
        return retorno
    
    # Chamar as funções de cadastro, e caso elas retornem algo, retornar o erro
    resposta_selecao = selecionar_tipo_componente(tipo, Navegador)
    if resposta_selecao:
        retorno['status'] = 'Erro'
        retorno['mensagem'] = resposta_selecao
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

    resposta_avaliacao = inserir_avaliacoes_e_ementa(ccr, Navegador)
    if resposta_avaliacao:
        retorno['status'] = 'Erro'
        retorno['mensagem'] = resposta_avaliacao
        return retorno  

    resposta_referencias = inserir_referencias(ccr, Navegador, driver)
    if resposta_referencias:
        retorno['status'] = 'Erro'
        retorno['mensagem'] = resposta_referencias
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

def selecionar_tipo_componente(infos : dict, Navegador : WebDriver_Interagir):
    print("DEBUG: SELECIONANDO TIPO DE COMPONENTE")

    try:
        if infos['componente'] == 'modulo':
            # Selecionar "MODULO" e garantir que o mesmo foi selecionado
            Navegador.select_por_valor((By.ID, "form:tipo"), valor = "3", wait = 10)
            tipo = Navegador.valor_selecionado_select((By.ID, "form:tipo"), wait = 10) 
            while tipo != '3':
                Navegador.select_por_valor((By.ID, "form:tipo"), valor = "3", wait = 10)
                tipo = Navegador.valor_selecionado_select((By.ID, "form:tipo"), wait = 10) 


        elif infos['componente'] == 'atividade':
            # Selecionar "ATIVIDADE" e garantir que o mesmo foi selecionado
            Navegador.select_por_valor((By.ID, "form:tipo"), valor = "1", wait = 10)
            tipo = Navegador.valor_selecionado_select((By.ID, "form:tipo"), wait = 10) 
            while tipo != '1':
                Navegador.select_por_valor((By.ID, "form:tipo"), valor = "1", wait = 10)
                tipo = Navegador.valor_selecionado_select((By.ID, "form:tipo"), wait = 10) 

            if infos['atividade'] == 'estagio':
                # Selecionar "ESTÁGIO" e garantir que o mesmo foi selecionado
                Navegador.select_por_valor((By.ID, "form:tipoAtividade"), valor = "1", wait = 10) # Estágio
                tipo_atividade = Navegador.valor_selecionado_select((By.ID, "form:tipoAtividade"), wait = 10) 
                while tipo_atividade != '1':
                    Navegador.select_por_valor((By.ID,  "form:tipoAtividade"), valor = "1", wait = 10)
                    tipo_atividade = Navegador.valor_selecionado_select((By.ID, "form:tipoAtividade"), wait = 10) 

                if infos['forma_participacao'] == 'internato':
                    # Selecionar "INTERNATO" e garantir que o mesmo foi selecionado
                    Navegador.select_por_valor((By.ID, "form:formaParticipacao"), valor = "4", wait = 10) # Internato
                    forma_participacao = Navegador.valor_selecionado_select((By.ID, "form:formaParticipacao"), wait = 10) 
                    while forma_participacao != '4':
                        Navegador.select_por_valor((By.ID, "form:formaParticipacao"), valor = "4", wait = 10)
                        forma_participacao = Navegador.valor_selecionado_select((By.ID, "form:formaParticipacao"), wait = 10) 
                
                elif infos['forma_participacao'] == 'coletiva':
                    # Selecionar "ATIVIDADE COLETIVA" e garantir que o mesmo foi selecionado
                    Navegador.select_por_valor((By.ID, "form:formaParticipacao"), valor = "3", wait = 10) # Coletiva
                    forma_participacao = Navegador.valor_selecionado_select((By.ID, "form:formaParticipacao"), wait = 10) 
                    while forma_participacao != '3':
                        Navegador.select_por_valor((By.ID, "form:formaParticipacao"), valor = "3", wait = 10)
                        forma_participacao = Navegador.valor_selecionado_select((By.ID, "form:formaParticipacao"), wait = 10) 
                
                else:
                    # Selecionar "ATIVIDADE INDIVIDUAL" e garantir que o mesmo foi selecionado
                    Navegador.select_por_valor((By.ID, "form:formaParticipacao"), valor = "2", wait = 10) # Individual
                    forma_participacao = Navegador.valor_selecionado_select((By.ID, "form:formaParticipacao"), wait = 10) 
                    while forma_participacao != '2':
                        Navegador.select_por_valor((By.ID, "form:formaParticipacao"), valor = "2", wait = 10)
                        forma_participacao = Navegador.valor_selecionado_select((By.ID, "form:formaParticipacao"), wait = 10) 
                
            else:
                if infos['atividade'] == 'integradora':
                    # Selecionar "ATIVIDADE INTEGRADORA" e garantir que o mesmo foi selecionado
                    Navegador.select_por_valor((By.ID, "form:tipoAtividade"), valor = "9", wait = 10) # Integradora
                    tipo_atividade = Navegador.valor_selecionado_select((By.ID, "form:tipoAtividade"), wait = 10) 
                    while tipo_atividade != '9':
                        Navegador.select_por_valor((By.ID,  "form:tipoAtividade"), valor = "9", wait = 10)
                        tipo_atividade = Navegador.valor_selecionado_select((By.ID, "form:tipoAtividade"), wait = 10) 

                    if infos['forma_participacao'] == 'internato':
                       # Selecionar "INTERNATO" e garantir que o mesmo foi selecionado
                        Navegador.select_por_valor((By.ID, "form:formaParticipacao"), valor = "4", wait = 10) # Internato
                        forma_participacao = Navegador.valor_selecionado_select((By.ID, "form:formaParticipacao"), wait = 10) 
                        while forma_participacao != '4':
                            Navegador.select_por_valor((By.ID, "form:formaParticipacao"), valor = "4", wait = 10)
                            forma_participacao = Navegador.valor_selecionado_select((By.ID, "form:formaParticipacao"), wait = 10) 
                
                    else:
                        # Selecionar "ATIVIDADE COLETIVA" e garantir que o mesmo foi selecionado
                        Navegador.select_por_valor((By.ID, "form:formaParticipacao"), valor = "3", wait = 10) # Coletiva
                        forma_participacao = Navegador.valor_selecionado_select((By.ID, "form:formaParticipacao"), wait = 10) 
                        while forma_participacao != '3':
                            Navegador.select_por_valor((By.ID, "form:formaParticipacao"), valor = "3", wait = 10)
                            forma_participacao = Navegador.valor_selecionado_select((By.ID, "form:formaParticipacao"), wait = 10) 
                
                else:
                    # Selecionar "TCC" e garantir que o mesmo foi selecionado
                    Navegador.select_por_valor((By.ID, "form:tipoAtividade"), valor = "3", wait = 10) # TCC
                    tipo_atividade = Navegador.valor_selecionado_select((By.ID, "form:tipoAtividade"), wait = 10) 
                    while tipo_atividade != '3':
                        Navegador.select_por_valor((By.ID,  "form:tipoAtividade"), valor = "3", wait = 10)
                        tipo_atividade = Navegador.valor_selecionado_select((By.ID, "form:tipoAtividade"), wait = 10) 
                    
                    # Selecionar "ATIVIDADE INDIVIDUAL" e garantir que o mesmo foi selecionado
                    Navegador.select_por_valor((By.ID, "form:formaParticipacao"), valor = "2", wait = 10) # Individual
                    forma_participacao = Navegador.valor_selecionado_select((By.ID, "form:formaParticipacao"), wait = 10) 
                    while forma_participacao != '2':
                        Navegador.select_por_valor((By.ID, "form:formaParticipacao"), valor = "2", wait = 10)
                        forma_participacao = Navegador.valor_selecionado_select((By.ID, "form:formaParticipacao"), wait = 10) 
                
        Navegador.select_por_valor((By.ID, "form:modalidadeEducacao"), valor = "1", wait = 10) #Presencial

        # Garantir que a modalidade Presencial foi selecionada
        valor_modalidade = Navegador.valor_selecionado_select((By.ID, "form:modalidadeEducacao"), wait = 10) 
        while valor_modalidade != '1':
            print("DEBUG: MODALIDADE PRESENCIAL NÃO FOI SELECIONADA")
            Navegador.select_por_valor((By.ID, "form:modalidadeEducacao"), valor = "1", wait = 10) #Presencial
            valor_modalidade = Navegador.valor_selecionado_select((By.ID, "form:modalidadeEducacao"), wait = 10) 


        Navegador.clicar_em((By.ID, "form:avancar"), wait=10)

        return None
    except Exception as e:
        return f"Erro ao selecionar tipo de componente: {e}"
        
def inserir_cabecalho_ccr(ccr : dict, Navegador : WebDriver_Interagir):
    print("DEBUG: INSERINDO CABECALHO")
    try:
        # Preencher os campos do cabeçalho com as informações do CCR
        campus = ccr.get('unidade', '')
        campus = campus.replace('CAMPUS', '').strip()
        Navegador.select_por_texto_parcial((By.ID, "form:unidades"), texto_parcial= "COORDENAÇÃO ACADÊMICA - " + campus, wait = 10)
        Navegador.escrever_em((By.ID, "form:codigo"), ccr.get('codigo', ''), wait = 10)
        descricao = ccr.get('descricao', '')
        # SIGAA n aceita UTF-8, por isso precisa normalizar o texto
        utf_desc = normalizar_texto_ascii(descricao)
        utf_desc = substituir_invisiveis_por_espaco(utf_desc)
        Navegador.escrever_em((By.ID, "form:nome"), utf_desc, wait = 10)

    except Exception as e:
        print(f"ERRO: {e}")
        return f"Erro ao selecionar inserir cabecalho: {e}"

def inserir_horas(ccr : dict, Navegador : WebDriver_Interagir, driver : webdriver):
    print("DEBUG: INSERINDO HORAS AULA")
    try:
        wait = WebDriverWait(driver, 10)
        horas = {
            0 : [ccr['hrs_presencial_teorica'], ccr['hrs_ead_teorica']],
            1 : [ccr['hrs_presencial_pratica'], ccr['hrs_ead_pratica']],
            2 : [ccr['hrs_presencial_extensao']]
        }
        wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@id, '0:cargaHoraria') and @onchange]")))
        flag = 'Presencial'
        ac = Navegador.action_chains()
        header = Navegador.encontrar_elemento((By.XPATH, "//h3[text()='Sistema Integrado de Gestão de Atividades Acadêmicas']"), wait=10)
        # Insere um valor das horas por vez
        for i in range(3):
            for j in range(len(horas[i])):
                    try:
                        # Tentar inserir as horas do ccr
                        action_chain_horas(ac, header, Navegador,flag, horas[i][j], i)                        
                    except StaleElementReferenceException:
                        # Caso falhar tenta 3x
                        for k in range(3):
                            try:
                                action_chain_horas(ac, header, Navegador,flag, horas[i][j], i)
                                break
                            except StaleElementReferenceException:
                                if k == 2:
                                    raise Exception(f"Erro ao inserir horas {horas[i][j]}")
                                else:
                                    time.sleep(0.2)
                    flag = 'Distancia' if flag == 'Presencial' else 'Presencial'
                
                        
        return None
    except Exception as e:
        print(f"ERRO: {e}")
        return f"Erro ao inserir horas: {e}"

def action_chain_horas(ac, header, Navegador : WebDriver_Interagir, flag, hora, i):
    try:
        # Digitar a hora da aula no campo especifico
        Navegador.limpar_imput((By.ID, f"form:j_id_jsp_527522820_23:0:j_id_jsp_527522820_26:{i}:cargaHoraria{flag}Valor"), wait=10)
        ac.click(header).perform()
        campo = Navegador.encontrar_elemento((By.ID, f"form:j_id_jsp_527522820_23:0:j_id_jsp_527522820_26:{i}:cargaHoraria{flag}Valor"), wait=10)
        ac.move_to_element(campo).perform()
        ac.click(campo).perform()
        ac.send_keys(hora).perform()
        ac.move_to_element(header).perform()
        ac.click(header).perform()
        ac.click(header).perform()
        Navegador.encontrar_elemento((By.ID, f"form:j_id_jsp_527522820_23:0:j_id_jsp_527522820_26:{i}:cargaHoraria{flag}Valor"), wait=10) # Verifica se o elemento foi atualizado após a inserção da hora
    except Exception as e:
        print(f"Erro ao inserir horas ({hora}) AC: {e}")
        raise StaleElementReferenceException(f"Erro ao inserir horas ({hora}) AC: {e}")

def inserir_discente_orientada(ccr : dict, Navegador : WebDriver_Interagir,driver, incremento_aula : int = 0):
    print("DEBUG: INSERINDO HORAS DISCENTE ORIENTADA")
    try:
        wait = WebDriverWait(driver, 10)
        # dicionario das horas, para tcc e para estágio
        if ccr['hrs_tcc_discente_orientada']!= 0:
            horas = {
                0 : [ccr['hrs_tcc_discente_orientada']]
            }
        else:
            horas = {
                0 : [ccr['hrs_estagio_presencial'], ccr['hrs_estagio_ead']],
                1 : [ccr['hrs_estagio_extensionista']]
            }
        wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@id, '0:cargaHoraria') and @onchange]")))
        flag = 'Presencial'
        ac = Navegador.action_chains()
        header = Navegador.encontrar_elemento((By.XPATH, "//h3[text()='Sistema Integrado de Gestão de Atividades Acadêmicas']"), wait=10)
        for i in range(len(horas)):
            for j in range(len(horas[i])):
                    try:
                        # Inserir o valor das horas
                        action_chain_discente_orientada(ac, header, Navegador,flag, horas[i][j], i, incremento_aula)
                        flag = 'Distancia' if flag == 'Presencial' else 'Presencial'
                    except StaleElementReferenceException:
                        # Caso falhe, tentar 3x
                        for k in range(3):
                            try:
                                action_chain_discente_orientada(ac, header, Navegador,flag, horas[i][j], i, incremento_aula)
                                flag = 'Distancia' if flag == 'Presencial' else 'Presencial'
                                break
                            except StaleElementReferenceException:
                                if k == 2:
                                    raise Exception(f"Erro ao inserir horas {horas[i][j]}")
                                else:
                                    time.sleep(0.2)
                        
        return None
    except Exception as e:
        print(f"ERRO: {e}")
        return f"Erro ao inserir horas: {e}"

def action_chain_discente_orientada(ac, header, Navegador : WebDriver_Interagir, flag, hora, i, incremento_aula):
    try:
        # Inserir as horas de discente orientada
        Navegador.limpar_imput((By.ID, f"form:j_id_jsp_527522820_23:{0+incremento_aula}:j_id_jsp_527522820_26:{i}:cargaHoraria{flag}Valor"), wait=10)
        ac.click(header).perform()
        campo = Navegador.encontrar_elemento((By.ID, f"form:j_id_jsp_527522820_23:{0+incremento_aula}:j_id_jsp_527522820_26:{i}:cargaHoraria{flag}Valor"), wait=10)
        ac.move_to_element(campo).perform()
        ac.click(campo).perform()
        ac.send_keys(hora).perform()
        ac.move_to_element(header).perform()
        ac.click(header).perform()
        ac.click(header).perform()
        Navegador.encontrar_elemento((By.ID, f"form:j_id_jsp_527522820_23:{0+incremento_aula}:j_id_jsp_527522820_26:{i}:cargaHoraria{flag}Valor"), wait=10) 
    except Exception as e:
        print(f"Erro ao inserir horas ({hora}) AC: {e}")
        raise StaleElementReferenceException(f"Erro ao inserir horas ({hora}) AC: {e}")

def inserir_orientacao_docente(ccr : dict, Navegador : WebDriver_Interagir, driver, incremento_aula : int = 0):
    print("DEBUG: INSERINDO HORAS DISCENTE ORIENTADA")
    try:
        wait = WebDriverWait(driver, 10)
        
        wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@id, '0:cargaHoraria') and @onchange]")))
        ac = Navegador.action_chains()
        header = Navegador.encontrar_elemento((By.XPATH, "//h3[text()='Sistema Integrado de Gestão de Atividades Acadêmicas']"), wait=10)
        
        try:
            # Tentar inserir as horas de orientação docente
            action_chain_orientacao(ac, header, Navegador, incremento_aula)
        except StaleElementReferenceException:
            # Caso falhe, tentar 3x
            for k in range(3):
                try:
                    action_chain_orientacao(ac, header, Navegador, incremento_aula)
                    break
                except StaleElementReferenceException:
                    if k == 2:
                        raise Exception(f"Erro ao inserir horas (10) - Orientação Discente")
                    else:
                        time.sleep(0.2)
                        
        return None
    except Exception as e:
        print(f"ERRO: {e}")
        return f"Erro ao inserir horas: {e}"

def action_chain_orientacao(ac, header, Navegador : WebDriver_Interagir, incremento_aula):
    try:
        # Preencher o campo de orientação docente com o valor 10 como padrão
        Navegador.limpar_imput((By.ID, f"form:j_id_jsp_527522820_23:{1+incremento_aula}:j_id_jsp_527522820_26:0:cargaHorariaValor"), wait=10)
        ac.click(header).perform()
        campo = Navegador.encontrar_elemento((By.ID, f"form:j_id_jsp_527522820_23:{1+incremento_aula}:j_id_jsp_527522820_26:0:cargaHorariaValor"), wait=10)
        ac.move_to_element(campo).perform()
        ac.click(campo).perform()
        ac.send_keys('10').perform()
        ac.move_to_element(header).perform()
        ac.click(header).perform()
        ac.click(header).perform()
        Navegador.encontrar_elemento((By.ID, f"form:j_id_jsp_527522820_23:{1+incremento_aula}:j_id_jsp_527522820_26:0:cargaHorariaValor"), wait=10) 
    except Exception as e:
        print(f"Erro ao inserir horas (10) - Orientação Discente AC: {e}")
        raise StaleElementReferenceException(f"Erro ao inserir horas (10) - Orientação Discente AC: {e}")

def inserir_avaliacoes_e_ementa(ccr : dict, Navegador : WebDriver_Interagir):
    print("DEBUG: INSERINDO AVALIAÇÕES")
    try:
        # Inserir num de avaliação e ementa respectivamente
        Navegador.select_por_valor((By.ID, 'form:numunidades'), valor= str(ccr['num_avaliacoes']), wait = 10)  # Insere num de avaliações
        Navegador.escrever_em((By.ID, 'form:ementa'), ccr['ementa'], wait = 10) 
        return None
    except Exception as e:
        print(f"ERRO: {e}")
        return f"Erro ao inserir avaliações: {e}"

def inserir_referencias(ccr : dict, Navegador : WebDriver_Interagir, driver):
    print("DEBUG: INSERINDO REFERÊNCIA")
    referencias_basicas = ccr['referencias_basicas']
    referencias_complementares = ccr['referencias_complementares']
    try:
        insere_refs(referencias_basicas, Navegador, tipo = 'Basicas', driver = driver)
        insere_refs(referencias_complementares, Navegador, tipo = 'Complementares', driver = driver)
        # As vezes eram inseridar referencias vazias do tipo livro
        bug_do_livro = Navegador.encontrar_elementos((By.XPATH, "//tr[td[1][normalize-space(text())='Livro']]"))
        if bug_do_livro:
            for _ in bug_do_livro:
                try:
                    Navegador.clicar_em((By.XPATH, "//tr[td[1][normalize-space(text())='Livro']]//a[@title='Remover Referência']"), wait = 5)
                    Navegador.ok_alerta(wait = 5)
                except:
                    pass
        return None
    
    except Exception as e:
        print(f"ERRO: {e}")
        return f"Erro ao inserir referencias {e}"

def insere_refs(referencias: dict, Navegador : WebDriver_Interagir, tipo : str, driver):
    try:
        radio_id = "form:tipoIR:0" if tipo == 'Basicas' else "form:tipoIR:1"  # Básica ou Complementar
        ac = Navegador.action_chains()

        for i, ref in referencias.items(): 
            # Ver se deu o Bug onde tem um form dentro do outro, pois ele não deixa cadastrar nesses casos
            bug_nova_ref = Navegador.encontrar_elementos((By.XPATH, "//table[caption[contains(text(), 'Nova Referência')]]"), wait = 10)
            if len(bug_nova_ref) > 1:
                Navegador.clicar_em((By.ID, "form:avancar"), wait=10)
                Navegador.clicar_em((By.ID, "form:dadosGerais"), wait=10)
                time.sleep(0.5)
                Navegador.encontrar_elemento((By.CSS_SELECTOR, '#info-sistema #tempoSessao'), wait=10)

            try:
                # Inserir a referencia, e ver se ela foi cadastrada
                ref_inserida = action_chains_referencias(ac, radio_id, ref, Navegador, tipo)
                if not ref_inserida:
                    print(f"DEBUG: CONSIDEROU A REF {ref} COMO NÃO CADASTRADA")
                    raise StaleElementReferenceException
            except StaleElementReferenceException:
                # Se não foi cadastrada a referencia, tentar 3x 
                for j in range(3):
                    try:
                       # Ver se deu o Bug onde tem um form dentro do outro, pois ele não deixa cadastrar nesses casos
                        bug_nova_ref = Navegador.encontrar_elementos((By.XPATH, "//table[caption[contains(text(), 'Nova Referência')]]"), wait = 10)
                        if len(bug_nova_ref) > 1:
                            Navegador.clicar_em((By.ID, "form:avancar"), wait=10)
                            Navegador.clicar_em((By.ID, "form:dadosGerais"), wait=10)
                            time.sleep(0.5)
                            Navegador.encontrar_elemento((By.CSS_SELECTOR, '#info-sistema #tempoSessao'), wait=10)
                        ref_inserida = action_chains_referencias(ac, radio_id, ref, Navegador, tipo)
                        if ref_inserida:
                            break
                    except StaleElementReferenceException:
                        if j == 2:
                            raise Exception(f"{ref}")
                        else:
                            driver.refresh()
                            time.sleep(0.2)

    except Exception as e:
        nome_tipo = 'Básica' if tipo == 'B' else 'Complementar'
        print(f"Erro ao inserir referencias {nome_tipo}: {e}")
        raise Exception(f"{nome_tipo}: {e}")

def action_chains_referencias(ac, radio_id, ref, Navegador, tipo):
    try:
        # Loop para garantir que o radio input "Outros" será selecionado
        radio_input_selected = None
        while radio_input_selected is None:
            radio_input = Navegador.encontrar_elemento((By.CSS_SELECTOR, f"input[name='form:tipo'][value='O']"), wait=10)
            Navegador.scrool_para_elemento(radio_input)
            ac.move_to_element(radio_input).perform()
            ac.click().perform()
            radio_input_selected = Navegador.encontrar_elemento((By.CSS_SELECTOR, f"input[name='form:tipo'][value='O'][checked='checked']"), wait=10)

        # Selecionar Basica ou Complementar
        label = Navegador.encontrar_elemento((By.XPATH, f"//input[@id='{radio_id}']"), wait = 10)
        ac.move_to_element(label).perform()
        ac.click().perform()
        
        # Site do sigaa n aceita UTF-8, por isso deve-se normalizar a referencia antes de escrever
        utf_ref = normalizar_texto_ascii(ref) 
        utf_ref = substituir_invisiveis_por_espaco(utf_ref)
        Navegador.escrever_em((By.ID, "form:descricao"), utf_ref, wait = 10)
        avancar = Navegador.encontrar_elemento((By.ID, "form:adicionarIR"), wait = 10)
        ac.move_to_element(avancar).perform()
        ac.click().perform()

        try:
            # Ver se o campo de texto da referencia está vazio. Ou seja, esperar até q a ref esteja cadastrada
            Navegador.clicar_em((By.ID, "form:descricao"), wait = 10)
            inseriu = Navegador.encontrar_elemento((By.ID, f'form:descricao'), wait = 10)
            while inseriu.get_attribute('value') != '' and inseriu.get_attribute('value')!= utf_ref:
                inseriu = Navegador.encontrar_elemento((By.ID, f'form:descricao'), wait = 10)
        except StaleElementReferenceException as e:
            print("Deu Stale")
            inseriu = Navegador.encontrar_elemento((By.ID, f'form:descricao'), wait = 10)
            while inseriu.get_attribute('value') != '':
                inseriu = Navegador.encontrar_elemento((By.ID, f'form:descricao'), wait = 10)
        except Exception:
            pass
        
        # Ver se a referencia que foi inserida realmente foi inserida (Ser a ultima referencia cadastrada)
        ref_inserida = Navegador.esperar_texto_elemento((By.XPATH, f'//tbody[@id="form:listaIndicacoes{tipo}:tbody_element"]/tr[td[1][normalize-space()="Outros"]][last()]/td[2]'), texto_esperado=utf_ref, wait=10)
        return ref_inserida
    except Exception as e:
        print(f"Erro ao inserir referencia AC {ref}: {e}")
        raise StaleElementReferenceException(f"Erro ao inserir referencia AC {ref}: {e}")
       
def verificar_ccr(ccr : dict, Navegador : WebDriver_Interagir):
    print("DEBUG: VERIFICANDO CCR")
    Navegador.encontrar_elemento((By.ID, "form:senha"), wait=10)

    try:
        # Verificando unidade
        campus = ccr.get('unidade', '')
        campus = campus.replace('CAMPUS', '').strip()
        unidade_ccr = "COORDENAÇÃO ACADÊMICA - " + campus
        unidade_cadastrada = Navegador.extrair_texto_de((By.XPATH, "//tr[th[contains(text(), 'Unidade Responsável')]]/td"))
        assert unidade_cadastrada.startswith(unidade_ccr), f"UNIDADE: Esperado que '{unidade_cadastrada}' comece com '{unidade_ccr}'"

        # Verificando código
        codigo_ccr = ccr.get('codigo', '')
        codigo_cadastrado = Navegador.extrair_texto_de((By.XPATH, "//tr[th[contains(text(), 'Código')]]/td"))
        assert str(codigo_cadastrado) == str(codigo_ccr), f"COD: Esperado que '{codigo_cadastrado}' seja igual a '{codigo_ccr}'"

        # Verificando nome
        nome_ccr_bd = ccr.get('descricao', '')
        nome_ccr = normalizar_texto_ascii(nome_ccr_bd)
        nome_ccr = substituir_invisiveis_por_espaco(nome_ccr)
        nome_cadastrado = Navegador.extrair_texto_de((By.XPATH, "//tr[th[contains(text(), 'Nome')]]/td"))  
        assert str(nome_cadastrado).upper() == str(nome_ccr).upper(), f"NOME: Esperado que '{nome_cadastrado}' seja igual a '{nome_ccr}'"

        # Verificando quantidade de avaliações
        num_avaliacoes_ccr = ccr.get('num_avaliacoes', '')
        num_avaliacoes_cadastrado = Navegador.extrair_texto_de((By.XPATH, "//tr[th[contains(text(), 'Quantidade de Avaliações')]]/td"))
        assert int(num_avaliacoes_cadastrado) == int(num_avaliacoes_ccr), f"NUM_AVALIACOES: Esperado que '{num_avaliacoes_cadastrado}' seja igual a '{num_avaliacoes_ccr}'"

        # Verificando ementa
        ementa_ccr = ccr.get('ementa', '')
        ementa_cadastrado = Navegador.extrair_texto_de((By.XPATH, "//tr[th[contains(text(), 'Ementa/Descrição')]]/td"))
        assert str(ementa_cadastrado) == str(ementa_ccr), f"EMENTA: Esperado que '{ementa_cadastrado}' seja igual a '{ementa_ccr}'"

        # Verificando horas
        carga_horaria_presencial_cadastrada = Navegador.extrair_texto_de((By.XPATH, "//tr[td/b[contains(text(), 'Subtotal de Carga Horária de Aula - Presencial')]]"))
        if carga_horaria_presencial_cadastrada :
            carga_horaria_presencial_ccr = ccr.get('carga_horaria_presencial', '')
            carga_horaria_presencial_cadastrada = carga_horaria_presencial_cadastrada.replace('Subtotal de Carga Horária de Aula - Presencial\n  ','')
            carga_horaria_presencial_cadastrada = carga_horaria_presencial_cadastrada.replace('h','')
            carga_horaria_presencial_cadastrada = carga_horaria_presencial_cadastrada.strip()
            assert int(carga_horaria_presencial_cadastrada) == int(carga_horaria_presencial_ccr), f"HORA_P: Esperado que '{carga_horaria_presencial_cadastrada}' seja igual a '{carga_horaria_presencial_ccr}'"

        carga_horaria_ead_cadastrada = Navegador.extrair_texto_de((By.XPATH, "//tr[td/b[contains(text(), 'Subtotal de Carga Horária de Aula - a distancia')]]"))
        if carga_horaria_ead_cadastrada :
            carga_horaria_ead_ccr = ccr.get('carga_horaria_ead', '')
            carga_horaria_ead_cadastrada = carga_horaria_ead_cadastrada.replace('Subtotal de Carga Horária de Aula - a distancia\n  ','')
            carga_horaria_ead_cadastrada = carga_horaria_ead_cadastrada.replace('h','')
            carga_horaria_ead_cadastrada = carga_horaria_ead_cadastrada.strip()
            assert int(carga_horaria_ead_cadastrada) == int(carga_horaria_ead_ccr), f"HORA_EAD: Esperado que '{carga_horaria_ead_cadastrada}' seja igual a '{carga_horaria_ead_ccr}'"

        discente_orientada_cadastrada_presencial = Navegador.extrair_texto_de((By.XPATH, "//tr[td/b[contains(text(), 'Subtotal de Carga Horária de Discente Orientada - Presencial')]]"))  
        if discente_orientada_cadastrada_presencial:
            discente_orientada_cadastrada_presencial = discente_orientada_cadastrada_presencial.replace('Subtotal de Carga Horária de Discente Orientada - Presencial\n  ','')
            discente_orientada_cadastrada_presencial = discente_orientada_cadastrada_presencial.replace('h','')
            discente_orientada_cadastrada_presencial = discente_orientada_cadastrada_presencial.strip()
            discente_orientada_presencial_ccr = ccr.get('hrs_tcc_discente_orientada', 0) + ccr.get('hrs_estagio_presencial', 0) + ccr.get('hrs_estagio_extensionista', 0)
            assert int(discente_orientada_cadastrada_presencial) == int(discente_orientada_presencial_ccr), f"HORA_D: Esperado que '{discente_orientada_cadastrada_presencial}' seja igual a '{discente_orientada_presencial_ccr}'"

        discente_orientada_cadastrada_ead = Navegador.extrair_texto_de((By.XPATH, "//tr[td/b[contains(text(), 'Subtotal de Carga Horária de Discente Orientada - a distancia')]]"))  
        if discente_orientada_cadastrada_ead:
            discente_orientada_cadastrada_ead = discente_orientada_cadastrada_ead.replace('Subtotal de Carga Horária de Discente Orientada - a distancia\n  ','')
            discente_orientada_cadastrada_ead = discente_orientada_cadastrada_ead.replace('h','')
            discente_orientada_cadastrada_ead = discente_orientada_cadastrada_ead.strip()
            discente_orientada_ead_ccr = ccr.get('hrs_estagio_ead', 0) 
            assert int(discente_orientada_cadastrada_ead) == int(discente_orientada_ead_ccr), f"HORA_D: Esperado que '{discente_orientada_cadastrada_ead}' seja igual a '{discente_orientada_presencial_ccr}'"


        # Verificando referencias
        basica = []
        complementar = []
        grupo_atual = None

        tabela_referencias = Navegador.encontrar_elemento((By.XPATH, "//table[caption[text()='Referências']]"), wait = 5)
        if tabela_referencias:
            linhas_referencias = tabela_referencias.find_elements(By.CSS_SELECTOR, "tr:not(:has(th))")
            for tr in linhas_referencias:
                texto = tr.text.strip()

                if texto.startswith("Básica"):
                    grupo_atual = "basica"
                    continue  # pula o título
                elif texto.startswith("Complementar"):
                    grupo_atual = "complementar"
                    continue  # pula o título

                # Classifica a linha com base no grupo atual
                if grupo_atual == "basica":
                    basica.append(tr)
                elif grupo_atual == "complementar":
                    complementar.append(tr)

        assert len(basica) == len(ccr['referencias_basicas']) and len(ccr['referencias_complementares']) == len(complementar), f"""
                    REFS: Esperado que haja {len(ccr['referencias_basicas']) + len(ccr['referencias_complementares'])} 
                    linhas de referências, mas foram encontradas {len(basica) + len(complementar)} linhas."""

        return True

    # Se der qualquer erro de conferencia. Reinicia o processo de cadastro
    except AssertionError as e:
        print(f"ASSERTION ERRO: {e}")
        if Navegador.clicar_em((By.ID, "form:cancelar"), wait = 3):
            Navegador.ok_alerta(wait=3)
        return False
    except Exception as e:
        print(f"ERRO: {e}")
        if Navegador.clicar_em((By.ID, "form:cancelar"), wait = 3):
            Navegador.ok_alerta(wait=3)
        return False 
