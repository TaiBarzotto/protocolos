from logging import basicConfig
from logging import FileHandler, StreamHandler
from logging import Formatter, Filter, critical, info, debug, warning, error, DEBUG, INFO


# definição de filtros do que não deve ser ecoado
class MeuFiltro(Filter):
    def filter(self, record):
        if record.msg.lower().startswith('senha'):
            return False
        return True


# formtação da conteúdo do Log
formater_file_handler = Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')
# Arquivo do Log
file_handler = FileHandler("meus_logs.txt", "a")
# Configuração das saídas do log (arquivo, tela, e-mail, msg)
file_handler.setLevel(INFO)
file_handler.setFormatter(formater_file_handler)
file_handler.addFilter(MeuFiltro())

strem_handler = StreamHandler()
strem_handler.addFilter(MeuFiltro())

logger = basicConfig(
    level=DEBUG,
    encoding='utf-8',
    format='%(levelname)s:%(asctime)s:%(message)s',
    handlers=[file_handler, strem_handler]
)

# recebe o conteúdo a ser gravado e grava
def logger(level, mensagem):
    if level == 'I':
        info(mensagem)
    elif level == 'D':
        debug(mensagem)
    elif level == 'W':
        warning(mensagem)
    elif level == 'E':
        error(mensagem)
    else:
        critical(mensagem)

# recebe o intervalo de período, l~e o log e retorna o resultado
def listar(hrinicial, hrfim):
    pass
