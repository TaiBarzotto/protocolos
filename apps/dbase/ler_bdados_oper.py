import pandas as pd
import pyodbc
from apps.utilities.carregar_cfg_ambiente import ler_configuracao


# Função para ler os dados no PostgreSQL e jogar para um dataframe
def ler_bdoperacionais(cnx_oper, sql):
    tmp_df = pd.read_sql(sql, cnx_oper)
    return tmp_df


# Função para recuperar qual banco de dados deve ser lido para pegar os dados operacionais do SIG
def ler_settings_oper(ambiente):
    # Recuperar config de acesso ao banco do arquivo .ini
    cfg = ler_configuracao()
    origem_dados = cfg.get(ambiente, "DB")
    driver = cfg.get(origem_dados,"DRIVER")
    server = cfg.get(origem_dados,"SERVER")
    porta = cfg.get(origem_dados,"PORT")
    dbase = cfg.get(origem_dados,"DATABASE")
    usuario = cfg.get(origem_dados,"UID")
    prsen = cfg.get(origem_dados,"PWD")
    if origem_dados == 'BDados_SISPG':
        senha = prsen[5] + prsen[16] + prsen[13] + prsen[11] + prsen[2] + prsen[9] + prsen[12] + prsen[10]+ prsen[10]+ prsen[1]
    elif origem_dados == 'BDados_Redmine':
        senha = prsen[5] + prsen[16] + prsen[13] + prsen[11] + prsen[2] + prsen[9] + prsen[12] + prsen[10]+ prsen[10]+ prsen[1]
    elif origem_dados == 'BDados_hom':
        senha = 'NFoYhUqZ56'
    else:
        senha = prsen[1]+ prsen[13]+prsen[5]+prsen[2]+prsen[9]+prsen[4]+prsen[0]+prsen[8]
    dados_cnx = (
        "DRIVER=" + driver + ";" +
        "SERVER=" + server + ";" +
        "PORT=" + porta + ";" +
        "DATABASE=" + dbase + ";" +
        "UID=" + usuario + ";" +
        "PWD=" + senha + ";"
        )
    return dados_cnx


# Funçõa para conectar ao banco e retornar um cursor e uma conexão
def cnx_bdoperacional(dados_cnx):
    # Conecta ao banco de dados operacional
    cnx_oper = pyodbc.connect(dados_cnx)
    cursor = cnx_oper.cursor()
    return cnx_oper, cursor
