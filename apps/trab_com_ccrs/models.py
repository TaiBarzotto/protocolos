from sqlite3 import Date
from typing import Optional, Dict, List, Union
from pydantic import BaseModel


class Ppc(BaseModel):
    curso: Optional[str]
    descricao: Optional[str]
    versao: Optional[str]
    status: Optional[str]
    unidade: Optional[int]
    conteudo: str  # Corrigido: removido Text[str] e substituído por str
    dta_criacao: Date
    ativo: Optional[str]

class QueryPpc(BaseModel):
    ppc: Optional[str]

class ListaPpcs(BaseModel):
    ppc: Dict[str, Ppc]

class Ppcs(BaseModel):
    ppcs: list[Ppc]
    count: int

class Referencia(BaseModel):
    ccr: int
    dta_criacao: Date
    referencia: str
    ativa: bool  # Corrigido: Boolean para bool
    dta_ativacao: Date
    dta_desativacao: Date
    tipo: str

class StatusRetorno(BaseModel):
    status: Optional[str]

class StatusRetornoDetalhado(BaseModel):
    status: Optional[str]
    detalhes: Optional[Dict[str, str]] 

class ReferenciasDict(BaseModel):
    referencias: Dict[str, str]

class Ccr(BaseModel):
    id: int
    codigo: str
    descricao: str
    unidade: str
    carga_horaria_presencial: int
    carga_horaria_ead: int
    hrs_presencial_teorica: int
    hrs_presencial_pratica: int
    hrs_presencial_extensao: int
    hrs_ead_teorica: int
    hrs_ead_pratica: int
    hrs_estagio_presencial: int
    hrs_estagio_ead: int
    hrs_estagio_extensionista: int
    hrs_tcc_discente_orientada: int
    modalidade: int
    dominio: Optional[int] = None
    ementa: str
    num_avaliacoes: int
    objetivo: str
    optativa: bool 
    cadastrada: bool 
    referencias_basicas: Dict[str, str]
    referencias_complementares: Dict[str, str]

class Objetivo(BaseModel):
    codigo: str
    objetivo: str