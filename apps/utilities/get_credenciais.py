import requests
import sys
from .mac_address import get_mac_address

def get_credenciais(cofre_url, aplicacao, hostname, username):
    # Obtém o MAC Address da máquina
    mac_address = get_mac_address()
    # Faz uma requisição POST para a API para obter as credenciais
    payload = {'aplicacao': aplicacao, 'hostname': hostname, 'username': username, 'mac_address': mac_address}
    # Pega a credencial
    resposta = requests.post(cofre_url, json=payload)
    print(f"Status da API: {resposta.status_code}")
    print(f"Resposta da API: {resposta.text}")
    credencial = resposta.json()
    # Validar a resposta da API
    if credencial.get('status') == 'Autorizado':
        password = {credencial.get('password')}
        password = ', '.join(password)
        print('Autorizou')
    else:
        print('Não autorizou')
        password = 'NãoAutorizada'
        sys.exit(1)  # Encerra a execução com um código de erro

    return password    