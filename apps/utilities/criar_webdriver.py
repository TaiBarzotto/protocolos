from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.core.os_manager import ChromeType


def novo_driver():
    try:
        try:
            # abre o navegador
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        except:
            driver = webdriver.Chrome(
                service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()))
    except:
        driver = webdriver.Chrome()
    return driver
