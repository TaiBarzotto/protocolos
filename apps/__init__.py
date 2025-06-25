from flask import Flask
from flasgger import Swagger
from flask_pydantic_spec import FlaskPydanticSpec, Response
from apps.config.swagger_config import configure_swagger  # Importa a configuração
from apps.utilities.criar_webdriver import novo_driver
from apps.navegar_no_sig.loggin import logar_no_sigaa
from flask import request

server = Flask(__name__)
specs = FlaskPydanticSpec('ServerAPI', title='API para realizar Operações no SIPAC')
specs.register(server)  # Registrar o specs

swagger = configure_swagger(server)  # Configura o Swagger usando o módulo externo

# Inicializando os módulos
from apps.trabalhar_SIPAC import init_app as init_protocolo
from apps.utilities import init_app as init_util

init_protocolo(server)
init_util(server)

@server.route('/test', methods=['GET'])
@specs.validate(resp=Response(HTTP_200=None))
def test_route():
    return "Teste realizado com successo!"

@server.route('/', methods=['GET'])
def home():
    base_url = request.url_root.rstrip('/')
    
    texto = '<h2> API para trabalhar com protocolos no SIPAC</h2>'
    texto = texto + f'<h4> 1) Para usar o SWAGGER para testar esta API, use a rota <a href="{base_url}/apidocs">/apidocs</a></h4>'
    texto = texto + f'<h4> 2) Para arquivar um processo, use a rota <a href="{base_url}/ccrs/ccr">/ccrs/ccr</a></h4>'
    return texto
