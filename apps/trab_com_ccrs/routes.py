from selenium import webdriver
from flask import Blueprint
from flask import Flask, request, jsonify
from flask_pydantic_spec import Response, Request
from apps import specs  # Importando o specs do apps.__init__.py
from apps.utilities.criar_webdriver import novo_driver
from apps.dbase.ler_bdados_oper import ler_settings_oper, cnx_bdoperacional, ler_bdoperacionais
from apps.trab_com_ccrs.models import Ccr, StatusRetorno, StatusRetornoDetalhado, Referencia, Objetivo
from apps.trab_com_ccrs.cadastro_ccr import cadastrar_ccr_sigaa
from apps.trab_com_ccrs.editar_ccr import editar_ccr_sigaa
from apps.trab_com_ccrs.cadastro_objetivo_ccr import cadastrar_objetivo_ccr
from apps.navegar_no_sig.loggin import logar_no_sigaa, logar_no_pergamum
from apps.navegar_no_sig.alertas import fechar_msg_ciente
from apps.utilities.carregar_cfg_ambiente import ler_configuracao, recupera_dados_login
from apps.utilities.get_credenciais import get_credenciais
from apps.utilities.auth import token_obrigatorio, verificar_token

bp_ccrs = Blueprint('ccrs', __name__, url_prefix='/ccrs')

@bp_ccrs.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Módulo CCRS ativos!!!"})

@bp_ccrs.route('/ccr', methods=['POST'])
@specs.validate(
    body=Request(Ccr),
    resp=Response(HTTP_200=StatusRetornoDetalhado, HTTP_400=StatusRetornoDetalhado)
)
def inserir_ppc():
    """
    Inserir CCR
    ---
    tags:
      - CCR
    description: Endpoint para inserir CCR no SIGAA.
    parameters:
      - name: body
        in: body
        required: true
        description:  CCRs
        schema:
          $ref: '#/definitions/Ccr'
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
        description: CCR inserido com sucesso
        schema:
          type: object
          additionalProperties:
            type: string
      400:
        description: Erro na validação dos dados
      401:
        description: Token inválido ou ausente
      500:
        description: Erro durante o processo de cadastro
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
      ccr_data = request.context.body.dict()

      # Configura o tipo de dado para passar para o Bot do SIGAA
      dados_ccr = {
          'codigo': ccr_data.get('codigo'),
          'descricao': ccr_data.get('descricao'),
          'unidade': ccr_data.get('unidade'),
          'ementa': ccr_data.get('ementa'),
          'objetivo': ccr_data.get('objetivo'),
          'status': ccr_data.get('status'),
          'dta_atualizacao': ccr_data.get('dta_atualizacao'),
          'modalidade': ccr_data.get('modalidade'),
          'obrigatorio': ccr_data.get('obrigatorio'),
          'dominio': ccr_data.get('dominio'),
          'carga_horaria_presencial': ccr_data.get('carga_horaria_presencial'),
          'carga_horaria_ead': ccr_data.get('carga_horaria_ead'),
          'hrs_presencial_teorica': ccr_data.get('hrs_presencial_teorica'),
          'hrs_presencial_pratica': ccr_data.get('hrs_presencial_pratica'),
          'hrs_presencial_extensao': ccr_data.get('hrs_presencial_extensao'),
          'hrs_ead_teorica': ccr_data.get('hrs_ead_teorica'),
          'hrs_ead_pratica': ccr_data.get('hrs_ead_pratica'),
          'hrs_estagio_extensionista': ccr_data.get('hrs_estagio_extensionista'),
          'hrs_estagio_ead': ccr_data.get('hrs_estagio_ead'),
          'hrs_estagio_presencial': ccr_data.get('hrs_estagio_presencial'),
          'hrs_tcc_discente_orientada': ccr_data.get('hrs_tcc_discente_orientada'),
          'num_avaliacoes': ccr_data.get('num_avaliacoes'),
          'referencias_basicas': ccr_data.get('referencias_basicas', {}),
          'referencias_complementares': ccr_data.get('referencias_complementares', {})
      }

      # Recupera a senha do usuario do Cofre de Senhas
      api_url = cfg['COFRE_SENHA']['API_URL'].strip("'")
      aplicacao = cfg [ambiente]['APLICACAO'].strip("'")
      sigaa_url = cfg [ambiente]['URL'].strip("'")
      print(f"DEBUG - URL API: {api_url} - APLICAÇÃO: {aplicacao} - URL SIGAA: {sigaa_url} - USUÁRIO: {usuario}")
      senha = get_credenciais(api_url, aplicacao=aplicacao, hostname = sigaa_url, username = usuario)
      
      # Fazer login no SIGAA
      driver = novo_driver()
      retorno = {}
      if logar_no_sigaa(driver, sigaa_url, username=usuario, passwd = senha):
        try:
          # Chama a rotina de cadastro de CCR via RPA
          retorno_ccr = cadastrar_ccr_sigaa(driver, dados_ccr, senha)
          if retorno_ccr['status']  == 'Sucesso':
            retorno_objetivo = cadastrar_objetivo_ccr(driver, dados_ccr)
            if retorno_objetivo['status'] == 'Sucesso':
              retorno['status'] = 'Sucesso'
              retorno['mensagem'] = "CCR e Objetivo cadastrados com sucesso"
              status_code = 200
            else:
              status_code = 400
              retorno['status'] = 'Erro ao cadastrar Objetivo'
              retorno['mensagem'] = retorno_objetivo['mensagem']
          else:
            status_code = 400
            retorno['status'] = 'Erro ao cadastrar CCR'
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
        return jsonify({'status': 'Falha ao logar no SIGAA.'}), 401

    except Exception as e:
      driver.quit()
      return jsonify({'erro': f'Erro na requisição: {str(e)}'}), 500

@bp_ccrs.route('/edit_ccr', methods=['POST'])
@specs.validate(
    body=Request(Ccr),
    resp=Response(HTTP_200=StatusRetornoDetalhado, HTTP_400=StatusRetornoDetalhado)
)
def editar_ccr():
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
      ccr_data = request.context.body.dict()

      # Configura o tipo de dado para passar para o Bot do SIGAA
      dados_ccr = {
          'codigo': ccr_data.get('codigo'),
          'descricao': ccr_data.get('descricao'),
          'unidade': ccr_data.get('unidade'),
          'ementa': ccr_data.get('ementa'),
          'objetivo': ccr_data.get('objetivo'),
          'status': ccr_data.get('status'),
          'dta_atualizacao': ccr_data.get('dta_atualizacao'),
          'modalidade': ccr_data.get('modalidade'),
          'obrigatorio': ccr_data.get('obrigatorio'),
          'dominio': ccr_data.get('dominio'),
          'carga_horaria_presencial': ccr_data.get('carga_horaria_presencial'),
          'carga_horaria_ead': ccr_data.get('carga_horaria_ead'),
          'hrs_presencial_teorica': ccr_data.get('hrs_presencial_teorica'),
          'hrs_presencial_pratica': ccr_data.get('hrs_presencial_pratica'),
          'hrs_presencial_extensao': ccr_data.get('hrs_presencial_extensao'),
          'hrs_ead_teorica': ccr_data.get('hrs_ead_teorica'),
          'hrs_ead_pratica': ccr_data.get('hrs_ead_pratica'),
          'hrs_estagio_extensionista': ccr_data.get('hrs_estagio_extensionista'),
          'hrs_estagio_ead': ccr_data.get('hrs_estagio_ead'),
          'hrs_estagio_presencial': ccr_data.get('hrs_estagio_presencial'),
          'hrs_tcc_discente_orientada': ccr_data.get('hrs_tcc_discente_orientada'),
          'num_avaliacoes': ccr_data.get('num_avaliacoes'),
          'referencias_basicas': ccr_data.get('referencias_basicas', {}),
          'referencias_complementares': ccr_data.get('referencias_complementares', {})
      }

      # Recupera a senha do usuario do Cofre de Senhas
      api_url = cfg['COFRE_SENHA']['API_URL'].strip("'")
      aplicacao = cfg [ambiente]['APLICACAO'].strip("'")
      sigaa_url = cfg [ambiente]['URL'].strip("'")
      print(f"DEBUG - URL API: {api_url} - APLICAÇÃO: {aplicacao} - URL SIGAA: {sigaa_url} - USUÁRIO: {usuario}")
      senha = get_credenciais(api_url, aplicacao=aplicacao, hostname = sigaa_url, username = usuario)
      
      # Fazer login no SIGAA
      driver = novo_driver()
      retorno = {}
      if logar_no_sigaa(driver, sigaa_url, username=usuario, passwd = senha):
        try:
          retorno_editar = editar_ccr_sigaa(driver, dados_ccr, senha)
          if retorno_editar['status'] == 'Sucesso':
            retorno['status'] = 'Sucesso'
            retorno['mensagem'] = "CCR editado com sucesso"
            status_code = 200
          else:
            status_code = 400
            retorno['status'] = 'Erro ao editar CCR'
            retorno['mensagem'] = retorno_editar['mensagem']

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

    except Exception as e:
      driver.quit()
      return jsonify({'erro': f'Erro na requisição: {str(e)}'}), 500
       
@bp_ccrs.route('/edit_ccr_objetivo', methods=['POST'])
@specs.validate(
    body=Request(Objetivo),
    resp=Response(HTTP_200=StatusRetornoDetalhado, HTTP_400=StatusRetornoDetalhado)
)
def editar_objetivo_ccr():
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
      ccr_data = request.context.body.dict()

      # Configura o tipo de dado para passar para o Bot do SIGAA
      dados_ccr = {
          'codigo': ccr_data.get('codigo'),
          'objetivo': ccr_data.get('objetivo')
      }

      # Recupera a senha do usuario do Cofre de Senhas
      api_url = cfg['COFRE_SENHA']['API_URL'].strip("'")
      aplicacao = cfg [ambiente]['APLICACAO'].strip("'")
      sigaa_url = cfg [ambiente]['URL'].strip("'")
      print(f"DEBUG - URL API: {api_url} - APLICAÇÃO: {aplicacao} - URL SIGAA: {sigaa_url} - USUÁRIO: {usuario}")
      senha = get_credenciais(api_url, aplicacao=aplicacao, hostname = sigaa_url, username = usuario)
      
      # Fazer login no SIGAA
      driver = novo_driver()
      retorno = {}
      if logar_no_sigaa(driver, sigaa_url, username=usuario, passwd = senha):
        try:
          fechar_msg_ciente(driver)
          retorno_editar = cadastrar_objetivo_ccr(driver, dados_ccr, cadastro=False)
          print(f"DEBUG - retorno_editar: {retorno_editar}")
          if retorno_editar['status'] == 'Sucesso':
            retorno['status'] = 'Sucesso'
            retorno['mensagem'] = "CCR editado com sucesso"
            status_code = 200
          else:
            status_code = 400
            retorno['status'] = 'Erro ao editar CCR'
            retorno['mensagem'] = retorno_editar['mensagem']

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

  except Exception as e:
      driver.quit()
      return jsonify({'erro': f'Erro na requisição: {str(e)}'}), 500

@bp_ccrs.route('/auth', methods=['POST'])
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

  
@bp_ccrs.route('/pergamun', methods=['POST'])
@specs.validate(
    body=Request(Referencia),
    resp=Response(HTTP_200=StatusRetornoDetalhado, HTTP_400=StatusRetornoDetalhado)
)
def inserir_pergamum():
    """
    Manter Referência no Pergamum
    ---
    tags:
      - Referência
    description: Endpoint para Manter (inserir e inativar Referências no CCR).
    parameters:
      - name: body
        in: body
        required: true
        description:  PPCs
        schema:
          $ref: '#/definitions/Referencia'
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
        description: Referêcia Mantida com sucesso
        schema:
          type: object
          additionalProperties:
            type: string
      400:
        description: Erro na validação dos dados
      401:
        description: Token inválido ou ausente
    """
    # Verifica se há um token e obtém o username
    username = verificar_token()
    
    # Se não houver token, usa o username do arquivo de configuração
    if not username:
        cfg = ler_configuracao()
        usuario, pwd, usuario_lc, ambiente = recupera_dados_login(cfg)
    else:
        # Usa o username do token
        cfg = ler_configuracao()
        ambiente = cfg["Ambiente"]["PERGAMUM"]
        usuario = username
        pwd = cfg[ambiente]["PWD"]
        usuario_lc = username
    
    # Recupera o corpo da requisição
    body = request.context.body.dict()
    dics = list(body.values())[0]  # Assume que `body` tem apenas um item
    # Extrai os dados do PPC
    ppc = [dados['curso'] for dados in dics.values()]
    # Configura a conexão com o banco de dados do SIGAA
    dados_cnx = ler_settings_oper("Ambiente")
    cnx_oper, cursor = cnx_bdoperacional(dados_cnx)
    # Cria uma string SQL para verificar se os Cursos estão cadastrados
    sql = f"SELECT curso FROM comum.pessoa WHERE cpf_cnpj IN ({','.join(curso)})"
    # Executa a consulta e armazena os resultados
    df_resultados = ler_bdoperacionais(cnx_oper, sql)
    cursos_cadastrados = set(df_resultados['curso'].tolist())
    # Certifique-se de que os cursos são strings
    cursos_cadastrados = {str(curso) for curso in cursos_cadastrados}
    # Preparando o retorno e filtrando os cursos já cadastrados
    retorno = {}
    dics_filtrado = {}
    for curso, dados_ppc in dics.items():
        if curso in cursos_cadastrados:
            retorno[curso] = "Curso já cadastrado"
        else:
            dics_filtrado[curso] = dados_ppc
    if not dics_filtrado:
        # Se todos os cursos já estiverem cadastrados, retorne a resposta imediatamente
        return jsonify(retorno)
    logado_pergamum = False
    for curso, dados_ppc in dics_filtrado.items():
        # Verifica se está logado
        if not logado_pergamum:
            # Cria o driver
            driver = novo_driver()
            # Efetua login no SIGAA
            status = logar_no_pergamum(driver, cfg, ambiente, username)
            if status == 'logado':
                logado_pergamum = True

        # Chama a rotina de cadastro de credor via RPA
        # status = cadastrar_ref_pergamum(driver, ambiente, dados_ppc)
        retorno[curso] = status
    # Fecha a conexão com o banco de dados
    cursor.close()
    cnx_oper.close()
    return jsonify(retorno)
        