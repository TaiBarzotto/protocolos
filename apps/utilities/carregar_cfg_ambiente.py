import tomllib  # Python 3.11+, se estiver usando uma versão anterior, use 'import tomli as tomllib'

# Lê os dados de config.toml
def ler_configuracao():
    with open('config.toml', 'rb') as f:
        cfg = tomllib.load(f)
    return cfg

def recupera_ambiente(cfg):
    ambiente = cfg["Ambiente"]["SIPAC"]
    db = cfg["Ambiente"]["DB"]
    return ambiente, db


def recupera_dados_login(cfg):
    ambiente, db = recupera_ambiente(cfg)
    usuario = cfg[ambiente]["LOGIN"]
    pwd = cfg[ambiente]["PWD"]
    usuario_lc = cfg[ambiente]["USUARIO"]
    return usuario, pwd, usuario_lc, ambiente


def dados_email(cfg):
    autoria = cfg["Smtp"]["AUTORIA"]
    ambiente, db = recupera_ambiente(cfg)
    destinatarios = cfg[ambiente]["DESTINATARIOS"]
    return autoria, destinatarios


def settings_email(cfg):
    host = cfg["Smtp"]["SERVIDOR"]
    port = cfg["Smtp"]["PORTA"]
    login = cfg["Smtp"]["CONTA"]
    senha = cfg["Smtp"]["SENHA"]
    smtpsrv = f'{host}: {port}'
    return smtpsrv, login, senha
