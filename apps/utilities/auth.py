import jwt
import datetime
from functools import wraps
from flask import request, jsonify

# Chave secreta para assinar os tokens (deve ser mantida segura)
SECRET_KEY = "sua_chave_secreta_aqui"  # Em produção, use variáveis de ambiente

def gerar_token(username):
    """
    Gera um token JWT para o usuário
    """
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow(),
        'sub': username
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verificar_token():
    """
    Verifica se o token é válido e retorna o username
    """
    token = None
    
    # Verifica se o token está no cabeçalho Authorization
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
    
    # Verifica se o token está nos parâmetros da URL
    if not token and 'token' in request.args:
        token = request.args.get('token')
    
    # Verifica se o token está no corpo da requisição JSON
    if not token and request.is_json:
        data = request.get_json()
        if 'token' in data:
            token = data.get('token')
    
    if not token:
        return None
    
    try:
        # Decodifica o token
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['sub']  # Retorna o username
    except jwt.ExpiredSignatureError:
        return None  # Token expirado
    except jwt.InvalidTokenError:
        return None  # Token inválido
    
def token_obrigatorio(f):
    """
    Decorator para rotas que exigem autenticação
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        username = verificar_token()
        
        if not username:
            return jsonify({'mensagem': 'Token inválido ou ausente!'}), 401
        
        # Adiciona o username aos argumentos da função
        kwargs['username'] = username
        return f(*args, **kwargs)
    
    return decorated