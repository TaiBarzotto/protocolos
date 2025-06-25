from sqlite3 import Date
from typing import Optional, Dict, List, Union
from pydantic import BaseModel


class Processos_arquivar(BaseModel):
    processo: Optional[List[str]]
    acao: Optional[int] # 1 para arquivar, 0 para desarquivar
    observacao: Optional[str]

class Interessado(BaseModel):
    categoria: Optional[str]
    nome: Optional[str]
    notificar: Optional[bool]
    email: Optional[bool]

class Processo(BaseModel):
    tipo_processo: Optional[str]
    processo_eletronico: Optional[bool]
    assunto_detalhado: Optional[str]
    natureza: Optional[str]
    observacao: Optional[str]
    interessados: Optional[Dict[str, Interessado]] # ou List[Interessado]

class StatusRetorno(BaseModel):
    status: Optional[str]

class StatusRetornoDetalhado(BaseModel):
    status: Optional[str]
    detalhes: Optional[Dict[str, str]] 
