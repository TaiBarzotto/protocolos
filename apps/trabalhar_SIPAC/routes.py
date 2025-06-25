from selenium import webdriver
from flask import Blueprint
from flask import Flask, request, jsonify
from flask_pydantic_spec import Response, Request
from apps import specs  # Importando o specs do apps.__init__.py
from apps.utilities.criar_webdriver import novo_driver
from apps.trabalhar_SIPAC.models import StatusRetornoDetalhado, Processos_arquivar, Processo
from apps.navegar_no_sig.loggin import logar_no_sigaa, logar_no_sipac
from apps.trabalhar_SIPAC.utils import acessar_protocolos
from apps.utilities.carregar_cfg_ambiente import ler_configuracao, recupera_dados_login
from apps.utilities.get_credenciais import get_credenciais
from apps.utilities.auth import verificar_token
from apps.trabalhar_SIPAC.arquivar import arquivar
from apps.trabalhar_SIPAC.criar_processo import criar_processo
from apps.utilities.email_smtp import enviar_email

bp_protocolos = Blueprint('protocolos', __name__, url_prefix='/protocolos')

@bp_protocolos.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Módulo Protocolos!"})


@bp_protocolos.route('/criar_processo', methods=['POST'])
@specs.validate(
    body=Request(Processo),
    resp=Response(HTTP_200=StatusRetornoDetalhado, HTTP_400=StatusRetornoDetalhado)
)
def criar_processo():
    """
    Criar Processo
    ---
    tags:
      - Processo
    description: Endpoint para criar um processo no SIPAC (mesa virtual)
    parameters:
      - name: body
        in: body
        required: true
        description:  Processo
        schema:
          $ref: '#/definitions/Processo'
      - name: Authorization
        in: header
        type: string
        required: false
        description: Token de autenticação (Bearer token)
      - name: token
        in: query
        type: string
        required: false
        description: Token de autenticação (alternativa)
    responses:
      200:
        description: Processo criado com sucesso
        schema:
          type: object
          additionalProperties:
            type: string
      400:
        description: Erro na validação dos dados
      401:
        description: Token inválido ou ausente
      500:
        description: Erro durante o processo de criação
    """
    try:
      retorno = {}
      cfg = ler_configuracao()

    # Verifica se há um token e obtém o username
      username = verificar_token()
      # Se não houver token, usa o username do arquivo de configuração
      if not username:
          usuario, senha, usuario_lc, ambiente = recupera_dados_login(cfg)
      else:
          # Usa o username do token
          ambiente = cfg["Ambiente"]["SIPAC"]
          usuario = username

      # Recupera o corpo da requisição
      protocolo_data = request.context.body.dict()

      # Configura o tipo de dado para passar para o Bot do SIPAC
      dados_protocolo = {
          'processos': protocolo_data.get('processo'),
          'acao': protocolo_data.get('acao'),
          'observacao': protocolo_data.get('observacao')
      }

      # Recupera a senha do usuario do Cofre de Senhas
      api_url = cfg['COFRE_SENHA']['API_URL'].strip("'")
      aplicacao = cfg [ambiente]['APLICACAO'].strip("'")
      sipac_url = cfg [ambiente]['URL'].strip("'")
      print(f"DEBUG - URL API: {api_url} - APLICAÇÃO: {aplicacao} - URL SIPAC: {sipac_url} - USUÁRIO: {usuario}")
      senha = get_credenciais(api_url, aplicacao=aplicacao, hostname = sipac_url, username = usuario)
      
      # Fazer login no SIPAC
      driver = novo_driver()
      retorno = {}
      if logar_no_sipac(driver, cfg, "SIPAC", usuario):
        try:
          acessar_protocolos(driver)
          # Chama a rotina de cadastro de CCR via RPA
          retorno_ccr = criar_processo(driver, dados_protocolo, senha)
          if retorno_ccr['status']  == 'Sucesso':
            retorno['status'] = 'Sucesso'
            retorno['mensagem'] = "Processo criado com sucesso"
            status_code = 200
          else:
            status_code = 400
            retorno['status'] = 'Erro ao criar Processo'
            retorno['mensagem'] = retorno_ccr['mensagem']

        except Exception as e:
            retorno = {'status': 'erro', 'mensagem': str(e)}
            status_code = 500

        finally:
            driver.quit()
        json_retorno = {
          'status': retorno['status'],
          'detalhes': {'mensagem':retorno['mensagem']}
        }
        print(f"DEBUG - RETORNO: {json_retorno}\nSTATUS: {status_code}")
        
        return jsonify(json_retorno), status_code

      else:
        driver.quit()
        return jsonify({'status': 'Falha ao logar no SIPAC.'}), 401

    except Exception as e:
      driver.quit()
      return jsonify({'erro': f'Erro na requisição: {str(e)}'}), 500
 

@bp_protocolos.route('/arquivar', methods=['POST'])
@specs.validate(
    body=Request(Processos_arquivar),
    resp=Response(HTTP_200=StatusRetornoDetalhado, HTTP_400=StatusRetornoDetalhado)
)
def arquivar():
    """
    Arquivar Processo
    ---
    tags:
      - Processo
    description: Endpoint para arquivar um processo no SIPAC (mesa virtual)
    parameters:
      - name: body
        in: body
        required: true
        description:  Processo
        schema:
          $ref: '#/definitions/Processos_arquivar'
      - name: Authorization
        in: header
        type: string
        required: false
        description: Token de autenticação (Bearer token)
      - name: token
        in: query
        type: string
        required: false
        description: Token de autenticação (alternativa)
    responses:
      200:
        description: Processo arquivado com sucesso
        schema:
          type: object
          additionalProperties:
            type: string
      400:
        description: Erro na validação dos dados
      401:
        description: Token inválido ou ausente
      500:
        description: Erro durante o processo de arquivação
    """
    try:
      retorno = {}
      cfg = ler_configuracao()

    # Verifica se há um token e obtém o username
      username = verificar_token()
      # Se não houver token, usa o username do arquivo de configuração
      if not username:
          usuario, senha, usuario_lc, ambiente = recupera_dados_login(cfg)
      else:
          # Usa o username do token
          ambiente = cfg["Ambiente"]["SIGAA"]
          usuario = username

      # Recupera o corpo da requisição
      protocolo_data = request.context.body.dict()

      # Configura o tipo de dado para passar para o Bot do SIGAA
      dados_protocolo = {
          'processos': protocolo_data.get('processo'),
          'acao': protocolo_data.get('acao'),
          'observacao': protocolo_data.get('observacao')
      }

      # Recupera a senha do usuario do Cofre de Senhas
      api_url = cfg['COFRE_SENHA']['API_URL'].strip("'")
      aplicacao = cfg [ambiente]['APLICACAO'].strip("'")
      sipac_url = cfg [ambiente]['URL'].strip("'")
      print(f"DEBUG - URL API: {api_url} - APLICAÇÃO: {aplicacao} - URL SIGAA: {sipac_url} - USUÁRIO: {usuario}")
      senha = get_credenciais(api_url, aplicacao=aplicacao, hostname = sipac_url, username = usuario)
      
      # Fazer login no SIGAA
      driver = novo_driver()
      retorno = {}
      if logar_no_sipac(driver, cfg, "SIPAC", usuario):
        try:
          acessar_protocolos(driver)
          # Chama a rotina de cadastro de CCR via RPA
          retorno_ccr = arquivar(driver, dados_protocolo, senha)
          if retorno_ccr['status']  == 'Sucesso':
            retorno['status'] = 'Sucesso'
            retorno['mensagem'] = "Processo arquivado com sucesso"
            status_code = 200
          else:
            status_code = 400
            retorno['status'] = 'Erro ao arquivar Processo'
            retorno['mensagem'] = retorno_ccr['mensagem']

        except Exception as e:
            retorno = {'status': 'erro', 'mensagem': str(e)}
            status_code = 500

        finally:
            driver.quit()
        json_retorno = {
          'status': retorno['status'],
          'detalhes': {'mensagem':retorno['mensagem']}
        }
        print(f"DEBUG - RETORNO: {json_retorno}\nSTATUS: {status_code}")
        
        enviar_email()
        return jsonify(json_retorno), status_code

      else:
        driver.quit()
        return jsonify({'status': 'Falha ao logar no SIPAC.'}), 401

    except Exception as e:
      driver.quit()
      return jsonify({'erro': f'Erro na requisição: {str(e)}'}), 500
  

@bp_protocolos.route('/auth', methods=['POST'])
def autenticar():
    """
    Autenticar usuário e gerar token
    ---
    tags:
      - Autenticação
    description: Endpoint para autenticar usuário e gerar token JWT.
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
          required:
            - username
    responses:
      200:
        description: Autenticação bem-sucedida
        schema:
          type: object
          properties:
            token:
              type: string
      401:
        description: Credenciais inválidas
    """
    # Recupera os dados de autenticação
    dados = request.get_json()
    
    if not dados or 'username' not in dados:
        return jsonify({'mensagem': 'Dados de autenticação incompletos!'}), 400
    
    username = dados['username']

    if username:
        from apps.utilities.auth import gerar_token
        token = gerar_token(username)
        return jsonify({'token': token})
    
    return jsonify({'mensagem': 'Credenciais inválidas!'}), 401
       