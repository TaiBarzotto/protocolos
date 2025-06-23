from apps import server

if __name__ == '__main__':
    # Define a porta na configuração do servidor
    porta = 8077
    host = '0.0.0.0'
    server.config['SERVER_PORT'] = porta
    server.config['SERVER_NAME'] = f"{host}:{porta}"
    
    server.run(port=porta, host=host, debug=True)