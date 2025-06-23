import pyautogui
# recebe usuário e senha e se loga no SIPAC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from apps.utilities.get_credenciais import get_credenciais
from apps.utilities.interagir import WebDriver_Interagir

def logar_no_sipac(driver, cfg, servico, username):
    # Recupera qual ambiente de trabalho deve ser utilizado para o SIPAC
    ambiente = cfg["Ambiente"]["SIPAC"]
    aplicacao = cfg[ambiente]["APLICACAO"]
    url = cfg[ambiente]["URL"]
    cripto = cfg[ambiente]["CRIPTO"]
    presenha = cfg[ambiente]["PWD"]
    selogarcomo = cfg[servico]["LOGARCOMO"]
    usuario = cfg[servico]["USUARIO"]
    resol_h = int(cfg[ambiente]["RESOLUCAO_H"])
    resol_v = int(cfg[ambiente]["RESOLUCAO_V"])
    cofre_url = cfg["COFRE_SENHA"]["API_URL"]
    # Decifra a senha se necessário
    if cripto == 'Sim':
        passwd = presenha[4] + presenha[18] + presenha[1] + presenha[13] + presenha[26] + presenha[7] + presenha[15] + \
                 presenha[23] + presenha[17] + presenha[27]
    elif cripto == 'Cofre':
        # Recupera a senha criptografada
        passwd = get_credenciais(cofre_url, aplicacao, ambiente, username)
        if passwd == 'NãoAutorizado':
            erro = 'Usuário não cadastrado no cofre'
            return 'erro', errod                              
    else:
        passwd = presenha

    # Abre o navegador e passa usuário e senha
    driver.set_window_size(resol_h, resol_v)
    driver.get(url)

    try:
        # Espera até que os campos de login estejam presentes
        login = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="conteudo"]/div[3]/form/table/tbody/tr[1]/td/input'))
        )
        senha = driver.find_element(By.XPATH, '//*[@id="conteudo"]/div[3]/form/table/tbody/tr[2]/td/input')
        botao = driver.find_element(By.XPATH, '//*[@id="conteudo"]/div[3]/form/table/tfoot/tr/td/input')
    except:
        login = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="conteudo"]/div[4]/form/table/tbody/tr[1]/td/input'))
        )
        senha = driver.find_element(By.XPATH, '//*[@id="conteudo"]/div[4]/form/table/tbody/tr[2]/td/input')
        botao = driver.find_element(By.XPATH, '//*[@id="conteudo"]/div[4]/form/table/tfoot/tr/td/input')

    # Enviar login e senha
    login.send_keys(username)
    senha.send_keys(passwd)
    botao.click()

    # Espera até que a URL mude para verificar o login
    WebDriverWait(driver, 10).until(lambda d: d.current_url != url)

    # Verifica se a página de pendências está presente
    if 'bloqueio_unidade_docs_pendentes.jsf' in driver.current_url:
        try:
            continuar_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="formAssinatura:btnNaoResponderContinuar"]'))
            )
            continuar_button.click()
        except:
            pass  # Tratar qualquer exceção que ocorra ao tentar clicar no botão

    # Verifica se o login adicional como outro usuário é necessário
    if selogarcomo == 'S':
        try:
            menu1 = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="combobox"]/select'))
            )
            menu1.send_keys('Logar como outro Usuário' + Keys.RETURN)

            login_setor = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="conteudo"]/form/table/tbody/tr/td/input'))
            )
            botao_setor = driver.find_element(By.XPATH, '//*[@id="conteudo"]/form/table/tfoot/tr/td/input[3]')

            login_setor.send_keys(usuario)
            botao_setor.click()

            time.sleep(2)
            pyautogui.hotkey("ctrl", "end")

            botao_logar = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="conteudo"]/table/tbody/tr/td/table/tfoot/tr/td/input[1]'))
            )
            botao_logar.click()

            # Navega até a página principal do SIPAC após o login
            url_menu_principal = url + '/portal_administrativo/index.jsf'
            driver.get(url_menu_principal)
        except:
            pass  # Tratar qualquer exceção que ocorra ao tentar logar como outro usuário

    return 'logado'

def logoff_sipac(driver):
    logof = driver.find_element(By.XPATH, '/html/body/div[4]/div[1]/div[1]/span[3]/a')
    logof.click()

def logar_no_sigaa(driver, url, username, passwd):
    try:
        Navegador = WebDriver_Interagir(driver)
        Navegador.navegar_para(url)

        try:
            # Espera até que os campos de login estejam presentes
            Navegador.encontrar_elemento((By.CSS_SELECTOR, 'input[name="user.login"]'), wait=10)
        except:
            Navegador.encontrar_elemento((By.CSS_SELECTOR, 'input[name="user.login"]'), wait=10)

        # Enviar login e senha
        Navegador.escrever_em((By.CSS_SELECTOR, 'input[name="user.login"]'), username, wait=10) #Login
        Navegador.escrever_em((By.CSS_SELECTOR, 'input[name="user.senha"]'), passwd, wait=10) #Senha
        Navegador.clicar_em((By.CSS_SELECTOR, 'input[value="Entrar"]'), wait=10) #Botão Entrar

        # Verifica se o login foi feito com sucesso(tempo de sessão presente na página)
        logado = Navegador.encontrar_elemento((By.CSS_SELECTOR, '#info-sistema #tempoSessao'), wait=30)
        if logado:
            print("Login feito")
            return True
        else:
            return False
    except Exception as e:
        print(f"Erro ao fazer login no SIGAA: {str(e)}")
        raise Exception("Erro ao fazer login no SIGAA")


def logoff_sigaa(driver):
    logof = driver.find_element(By.XPATH, '/html/body/div[4]/div[1]/div[1]/span[3]/a')
    logof.click()

def logar_no_pergamum(driver, cfg, servico, username):
    # Recupera qual ambiente de trabalho deve ser utilizado para o S
    pass