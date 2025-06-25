from selenium.webdriver.common.by import By
from apps.utilities.formatar_str import normalizar_texto_ascii, substituir_invisiveis_por_espaco
from apps.utilities.interagir import WebDriver_Interagir

def menu_graduacao(Navegador: WebDriver_Interagir):
    """
    Acessar o Menu de graduação através do cabeçalho
    
    Args:
    - Navegador: instancia do WebDriver_Interagir

    Returns:
    - True: se conseguir acessar o menu de graduação
    - False: caso falhe em acessar o menu de graduação
    """
    
    Navegador.clicar_em((By.XPATH, '//div[@id="menu-usuario"]//li[@class="modulos"]//a[@id="show-modulos"]'), wait=10)
    Navegador.clicar_em((By.CSS_SELECTOR, "#modulos li.graduacao.on a"), wait=20) # Graduação 
    menu = Navegador.encontrar_elemento((By.XPATH, '//h2[text()="Menu de Graduação"]'), wait=30)
    if menu is None:
        return False
    else:
        return True
