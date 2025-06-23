from selenium.webdriver.common.by import By
from apps.utilities.interagir import WebDriver_Interagir

# Validar se a interface do SIGAA não abriu com alertas, como por exemplo as notícias cadastradas no SIGADmin
# Clica no botão "ciente do cookies do SIGAA"
def fechar_msg_ciente(driver):
    try:
        Navegador = WebDriver_Interagir(driver)
        # Clicar no botão ciente
        ciente = Navegador.encontrar_elemento((By.XPATH, "//button[text()='Ciente']"), wait=10) 
        ac = Navegador.action_chains()
        ac.move_to_element(ciente).perform()
        ac.click(ciente).perform()
    except:
        pass