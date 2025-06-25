from flasgger import Swagger

def configure_swagger(server):
    swagger = Swagger(server)
    
    if swagger.template is None:
        swagger.template = {}
    
    swagger.template["definitions"] = {
        "Ppc": {
            "type": "object",
            "properties": {
                "curso": {"type": "string"},
                "descricao": {"type": "string"},
                "versao": {"type": "string"},
                "status": {"type": "string"},
                "unidade": {"type": "integer"},
                "conteudo": {"type": "string"},
                "dta_criacao": {"type": "string", "format": "date"},
                "ativo": {"type": "string"}
            }
        },
        "QueryPpc": {
            "type": "object",
            "properties": {
                "ppc": {"type": "string"}
            }
        },
        "Ppcs": {
            "type": "object",
            "properties": {
                "ppcs": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Ppc"}
                },
                "count": {"type": "integer"}
            }
        },
        "Referencia": {
            "type": "object",
            "properties": {
                "ccr": {"type": "integer"},
                "dta_criacao": {"type": "string", "format": "date"},
                "referencia": {"type": "string"},
                "ativa": {"type": "boolean"},
                "dta_ativacao": {"type": "string", "format": "date"},
                "dta_desativacao": {"type": "string", "format": "date"},
                "tipo": {"type": "string"}
            }
        },
        "Ccr": {
            "type": "object",
            "properties": {
                "codigo": {"type": "string"},
                "descricao": {"type": "string"},
                "ementa": {"type": "string"},
                "objetivo": {"type": "string"},
                "status": {"type": "string"},
                "dta_atualizacao": {"type": "string", "format": "date"},
                "modalidade": {"type": "integer"},
                "obrigatorio": {"type": "integer"},
                "dominio": {"type": "integer"},
                "carga_horaria_presencial": {"type": "integer"},
                "carga_horaria_ead": {"type": "integer"},
                "hrs_presencial_teorica": {"type": "integer"},
                "hrs_presencial_pratica": {"type": "integer"},
                "hrs_presencial_extensao": {"type": "integer"},
                "hrs_ead_teorica": {"type": "integer"},
                "hrs_ead_pratica": {"type": "integer"},
                "hrs_estagio_extensionista": {"type": "integer"},
                "hrs_estagio_ead": {"type": "integer"},
                "hrs_estagio_presencial": {"type": "integer"},
                "hrs_tcc_discente_orientada": {"type": "integer"},
                "num_avaliacoes": {"type": "integer"},
                "referencias": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Referencia"}
                }
            }
        },
        "StatusRetorno": {
            "type": "object",
            "properties": {
                "status": {"type": "string"}
            }
        },
        "StatusRetornoDetalhado": {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "detalhes": {
                    "type": "object",
                    "additionalProperties": {"type": "string"}
                }
            }
        }
    }
    
    return swagger
