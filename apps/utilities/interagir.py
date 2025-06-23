from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    NoAlertPresentException
    )

class WebDriver_Interagir:
    def __init__(self, driver=None):
        self.driver = driver if driver else webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)

    def navegar_para(self, url):
        """
        Navega para a URL especificada.
        ---
        Args:
        - url (str): A URL para a qual você deseja navegar.
        """

        self.driver.get(url)

    def encontrar_elemento(self, locator, wait=None):
        """
        Encontra um elemento na página com base no locator especificado. 
        ---
        exemplo locator: (By.ID, 'element_id')

        Args:
        - locator (tuple): Uma tupla que representa o locator do elemento.
        - wait (int): O tempo máximo de espera em segundos.

        Returns:
        - O elemento se encontrado, None caso contrário.
        """

        try:
            if wait is not None:
                element = WebDriverWait(self.driver, wait).until(
                    EC.presence_of_element_located(locator)
                )
            else:
                element = self.driver.find_element(*locator)
            return element
        except (TimeoutException, NoSuchElementException):
            print (f"Elemento não encontrado: {locator}")
            return None
        except Exception as e:
            print(f"Erro ao encontrar elemento {locator}: {e}")
            return None

    def encontrar_elementos(self, locator, wait=None):
        """
        Encontra elementos na página com base no locator especificado.
        ---
        exemplo locator: (By.ID, 'element_id')

        Args:
        - locator (tuple): Uma tupla que representa o locator dos elementos.
        - wait (int): O tempo máximo de espera em segundos. 

        Returns:
        - Uma lista de elementos se encontrados, uma lista vazia caso contrário.
        """

        try:
            if wait is not None:
                elements = WebDriverWait(self.driver, wait).until(
                    EC.presence_of_all_elements_located(locator)
                )
            else:
                elements = self.driver.find_elements(*locator)
            return elements
        except (TimeoutException, NoSuchElementException):
            print (f"Elementos não encontrados: {locator}")
            return []
        except Exception as e:
            print(f"Erro ao encontrar elementos {locator}: {e}")
            return []

    def esperar_texto_elemento(self, locator, texto_esperado, wait=None):
        """
        Espera até que o texto de um elemento na página corresponda ao texto esperado.
        ---
        exemplo locator: (By.ID, 'element_id')

        Args:
        - locator (tuple): Uma tupla que representa o locator do elemento.
        - texto_esperado (str): O texto esperado no elemento.
        - wait (int): O tempo máximo de espera em segundos.

        Returns:
        - True se o texto corresponder ao esperado, False caso contrário.
        """

        try:
            if wait is not None:
                WebDriverWait(self.driver, wait).until(
                    EC.text_to_be_present_in_element(locator, texto_esperado)
                )
               
            element = self.driver.find_element(*locator)
            return element.text == texto_esperado
        except (TimeoutException, NoSuchElementException):
            return False
        except Exception as e:
            print(f"Erro ao esperar por texto no elemento {locator}: {e}")
            return False

    def clicar_em(self, locator, wait=None):
        """
        Clica em um elemento na página com base no locator especificado.
        ---
        A função primeiro encontra o elemento e, em seguida, o clica.
        exemplo locator: (By.ID, 'element_id')

        Args:
        - locator (tuple): Uma tupla que representa o locator do elemento.
        - wait (int): O tempo máximo de espera em segundos.

        Returns:
        - True se o elemento for clicado com sucesso, False caso contrário.
        """

        try:
            if wait is not None:
                element = WebDriverWait(self.driver, wait).until(
                    EC.element_to_be_clickable(locator)
                )
            else:
                element = self.driver.find_element(*locator)
        except (TimeoutException, NoSuchElementException):
            return False
        try:
            if element:
                element.click()
                return True
            return False
        except Exception as e:
            print(f"Erro ao clicar no elemento {locator}: {e}")
            return False

    def escrever_em(self, locator, text, wait=None):
        """
        Escreve texto em um elemento na página com base no locator especificado.
        ---
        A função primeiro encontra o elemento e, em seguida, o limpa e escreve o texto fornecido.
        exemplo locator: (By.ID, 'element_id')

        Args:
        - locator (tuple): Uma tupla que representa o locator do elemento.
        - text (str): O texto a ser escrito no elemento.
        - wait (int): O tempo máximo de espera em segundos.

        Returns:
        - True se o texto for escrito com sucesso, False caso contrário.
        """

        try:

            if wait is not None:
                element = WebDriverWait(self.driver, wait).until(
                    EC.element_to_be_clickable(locator)
                )
            else:
                element = self.driver.find_element(*locator)
        except (TimeoutException, NoSuchElementException):
            return False
        try:
            if element:
                element.send_keys(text)
                return True
            return False
        except Exception as e:
            print(f"Erro ao escrever no elemento {locator}: {e}")
            print(element.get_dom_attribute('outerHTML'))
            return False
    def limpar_imput(self, locator, wait=None):
        """
        Limpa o valor de um elemento de entrada na página com base no locator especificado.
        ---
        A função primeiro encontra o elemento e, em seguida, limpa o valor.
        exemplo locator: (By.ID, 'element_id')

        Args:
        - locator (tuple): Uma tupla que representa o locator do elemento.
        - wait (int): O tempo máximo de espera em segundos.

        Returns:
        - True se o valor for limpo com sucesso, False caso contrário.
        """

        try:
            if wait is not None:
                element = WebDriverWait(self.driver, wait).until(
                    EC.element_to_be_clickable(locator)
                )
            else:
                element = self.driver.find_element(*locator)
        except (TimeoutException, NoSuchElementException):
            return False
        try:
            if element:
                element.clear()
                return True
            return False    
        except Exception as e:
            print(f"Erro ao limpar o elemento {locator}: {e}")
            return False
    def extrair_texto_de(self, locator, wait=None):
        """
        Extrai o texto de um elemento na página com base no locator especificado.
        ---
        A função primeiro encontra o elemento e, em seguida, extrai o texto.
        exemplo locator: (By.ID, 'element_id')

        Args:
        - locator (tuple): Uma tupla que representa o locator do elemento.
        - wait (int): O tempo máximo de espera em segundos.

        Returns:    
        - O texto do elemento se encontrado, None caso contrário.   
        """

        try:
            if wait is not None:
                element = WebDriverWait(self.driver, wait).until(
                    EC.presence_of_element_located(locator)
                )
            else:
                element = self.driver.find_element(*locator)
        except (TimeoutException, NoSuchElementException):
            return False

        return element.text if element else None
    
    def mudou_link(self, link_esperado, wait=10):
        """
        Verifica se a URL atual do navegador mudou para o link esperado após uma ação.
        ---
        A função utiliza o WebDriverWait para esperar até que a URL atual corresponda ao link esperado.

        Args:
        - link_esperado (str): A URL esperada após o clique.
        - wait (int): O tempo máximo de espera em segundos.

        Returns:
        - True se a URL mudou e corresponde ao link esperado.
        - False se a URL não mudou ou não corresponde ao esperado no tempo especificado.
        """
        try:
            WebDriverWait(self.driver, wait).until(
                EC.url_to_be(link_esperado)
            )
            return True
        except TimeoutException:
            return False
    
    def select_por_valor(self, locator:tuple, valor:str, wait=10):
        """
        Seleciona uma opção em um elemento <select> com base no locator e valor especificados.
        ---
        A função primeiro encontra o elemento <select> e, em seguida, seleciona a opção com o valor especificado.

        Args:
        - locator (tuple): Uma tupla que representa o locator do elemento <select>.
        - valor (str): O valor da opção a ser selecionada.
        - wait (int): O tempo máximo de espera em segundos.

        Returns:
        - True se a opção for selecionada com sucesso, False caso contrário.
        """
        
        try:
            if wait is not None:
                WebDriverWait(self.driver, wait).until(EC.visibility_of_element_located(locator))
                select_element = WebDriverWait(self.driver, wait).until(EC.element_to_be_clickable(locator))
            else:
                select_element = self.driver.find_element(*locator)

            select = Select(select_element)
            select.select_by_value(valor)
            return True
        except Exception as e:
            print(f"Erro ao selecionar item de valor {valor}: {e}")
            return False

    def select_por_texto(self, locator:tuple, text:str, wait=10):
        """
        Seleciona uma opção em um elemento <select> com base no locator e texto especificados.
        ---
        A função primeiro encontra o elemento <select> e, em seguida, seleciona a opção com o texto especificado.

        Args:
        - locator (tuple): Uma tupla que representa o locator do elemento <select>.
        - text (str): O o da opção a ser selecionada.
        - wait (int): O tempo máximo de espera em segundos.

        Returns:
        - True se a opção for selecionada com sucesso, False caso contrário.
        """
        
        try:
            if wait is not None:
                WebDriverWait(self.driver, wait).until(EC.presence_of_element_located(locator))
                select_element = WebDriverWait(self.driver, wait).until(EC.element_to_be_clickable(locator))
            else:
                select_element = self.driver.find_element(*locator)

            select = Select(select_element)
            select.select_by_visible_text(text)
            return True
        except Exception as e:
            print(f"Erro ao selecionar item de texto {text}: {e}")
            return False

    def select_por_texto_parcial(self, locator: tuple, texto_parcial: str, wait=10):
        """
        Seleciona uma opção em um <select> cujo texto contenha parcialmente o texto especificado.
        ---
        Args:
        - locator (tuple): O locator do <select>.
        - texto_parcial (str): Parte do texto da opção a ser selecionada.
        - wait (int): Tempo de espera.

        Returns:
        - True se a opção for selecionada, False caso contrário.
        """
        try:
            WebDriverWait(self.driver, wait).until(EC.visibility_of_element_located(locator))
            select_element = WebDriverWait(self.driver, wait).until(EC.element_to_be_clickable(locator))
            select = Select(select_element)

            for option in select.options:
                if texto_parcial.lower() in option.text.lower():
                    select.select_by_visible_text(option.text)
                    return True

            print(f"Nenhuma opção encontrada contendo: '{texto_parcial}'")
            return False

        except Exception as e:
            print(f"Erro ao selecionar por texto parcial '{texto_parcial}': {e}")
            return False
    def valor_selecionado_select(self, locator: tuple, wait=10):
        """
        Obtém o valor selecionado em um elemento <select>.
        ---
        Args:
        - locator (tuple): O locator do elemento <select>.
        - wait (int): Tempo de espera.

        Returns:    
        - O valor selecionado ou None se nenhum valor estiver selecionado.
        """
        try:
            select_element = WebDriverWait(self.driver, wait).until(EC.visibility_of_element_located(locator))
            select = Select(select_element)
            selected_option = select.first_selected_option
            return selected_option.get_attribute("value")
        except Exception as e:
            print(f"Erro ao obter o valor selecionado: {e}")
            return None

    def action_chains(self):
        """
        Cria uma instância de ActionChains para interações com o navegador.
        ---
        Returns:
        - Uma instância de ActionChains.
        """
        return webdriver.ActionChains(self.driver)
    
    def ok_alerta(self, wait = None):
        """
        Aceita o alerta exibido no navegador.
        ---
        Args:
        - wait (int): Tempo de espera.
        Returns:
        - True se o alerta for aceito com sucesso, False caso contrário.
        """
        try:
            if wait is not None:
                alerta = WebDriverWait(self.driver, wait).until(EC.alert_is_present())
            else:
                alerta = self.driver.switch_to.alert
            alerta.accept()
            return True
        except NoAlertPresentException:
            print("Nenhum alerta foi encontrado.")
            return False
    def scrool_para_elemento(self, element):
        """
        Faz o scroll até um elemento específico na página.
        ---
        """
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
    def fechar_driver(self):
        """
        Fecha o navegador e encerra o driver.
        """
        if self.driver:
            self.driver.quit()
