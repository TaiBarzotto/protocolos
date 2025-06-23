from sqlite3 import Date
from typing import Optional, Dict, List, Union
from pydantic import BaseModel


class Processos_arquivar(BaseModel):
    processo: Optional[List[str]]
    acao: Optional[int] # 1 para arquivar, 0 para desarquivar
    observacao: Optional[str]

class StatusRetorno(BaseModel):
    status: Optional[str]

class StatusRetornoDetalhado(BaseModel):
    status: Optional[str]
    detalhes: Optional[Dict[str, str]] 
