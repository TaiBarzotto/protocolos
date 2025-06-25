from selenium import webdriver
from apps.trab_com_ccrs.cadastro_ccr import cadastrar_ccr_sigaa
from apps.trab_com_ccrs.editar_ccr import editar_ccr_sigaa
from apps.trab_com_ccrs.cadastro_objetivo_ccr import cadastrar_objetivo_ccr
from apps.utilities.carregar_cfg_ambiente import dados_email
from apps.utilities.criar_webdriver import novo_driver
from apps.navegar_no_sig.loggin import logar_no_sigaa, logar_no_pergamum
driver = novo_driver()
sigaa_url = "https://sigaasml-tst.uffs.edu.br/"
logar_no_sigaa(driver, sigaa_url, username="tainara.bernardi", passwd = "Tai99572054")
dados_ccr = {
    'id': 8781, 
    'codigo': 'GEX1044', 
    'descricao': 'Atividades Curriculares Complementares', 
    'unidade': 'CAMPUS CHAPECÓ', 
    'carga_horaria_presencial': 60,
    'carga_horaria_ead': 0,
    'hrs_presencial_teorica': 60,
    'hrs_presencial_pratica': 0,
    'hrs_presencial_extensao': 0,
    'hrs_ead_teorica': 0,
    'hrs_ead_pratica': 0,
    'hrs_estagio_presencial': 0,
    'hrs_estagio_ead': 0,
    'hrs_estagio_extensionista': 0,
    'hrs_tcc_discente_orientada': 0,
    'modalidade': 1,
    'dominio': 3,
    'ementa': "Introdução. Tipos de estruturas. Ações. Vínculos. Reações de apoio. Equações de equilíbrio estático. Grau de estaticidade. Vigas: método das seções método direto. Vigas Gerber. Pórticos planos e espaciais. Arcos. Grelhas. Esforços internos em estruturas isostáticas: treliças planas, método dos nós, método de Ritter. Linha de influência em estruturas isostáticas.",
    'num_avaliacoes': 2, 
    'objetivo': 'Fornecer conhecimentos básicos da estática dos corpos rígidos e da análise de estruturas isostáticas lineares para aplicação em problemas práticos da engenharia estrutural.', 
    'optativa': False, 
    'cadastrada': False, 
    'referencias_basicas': {}, 
    'referencias_complementares': {}}
retorno1 = editar_ccr_sigaa(driver, dados_ccr, senha="Tai99572054")
print(retorno1)
retorno = cadastrar_objetivo_ccr(driver, dados_ccr)
print(retorno)