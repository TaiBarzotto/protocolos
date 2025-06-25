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
from apps.trab_com_ccrs import init_app as init_ccrs
from apps.utilities import init_app as init_util

init_ccrs(server)
init_util(server)

@server.route('/test', methods=['GET'])
@specs.validate(resp=Response(HTTP_200=None))
def test_route():
    return "Teste realizado com successo!"

@server.route('/', methods=['GET'])
def home():
    base_url = request.url_root.rstrip('/')
    
    texto = '<h2> API para cadastrar e/ou consultar dados no SIGAA</h2>'
    texto = texto + f'<h4> 1) Para usar o SWAGGER para testar esta API, use a rota <a href="{base_url}/apidocs">/apidocs</a></h4>'
    texto = texto + f'<h4> 2) Para cadastrar um CCR no SIGAA, use a rota <a href="{base_url}/ccrs/ccr">/ccrs/ccr</a></h4>'
    texto = texto + f'<h4> 3) Para manter CCRs e Referências no Pergamum, use a rota <a href="{base_url}/ccrs/pergamum">/ccrs/pergamum</a></h4>'
    return texto
