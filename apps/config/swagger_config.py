from flasgger import Swagger

def configure_swagger(server):
    swagger = Swagger(server)
    
    if swagger.template is None:
        swagger.template = {}
    
    swagger.template["definitions"] = {
        "Processos_arquivar": {
            "type": "object",
            "properties": {
                "processo": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "acao": {
                    "type": "integer",
                    "description": "1 para arquivar, 0 para desarquivar"
                },
                "observacao": {"type": "string"}
            }
        },
        "Interessado": {
            "type": "object",
            "properties": {
                "categoria": {"type": "string"},
                "nome": {"type": "string"},
                "notificar": {"type": "boolean"},
                "email": {"type": "boolean"}
            }
        },
        "Processo": {
            "type": "object",
            "properties": {
                "tipo_processo": {"type": "string"},
                "processo_eletronico": {"type": "boolean"},
                "assunto_detalhado": {"type": "string"},
                "natureza": {"type": "string"},
                "observacao": {"type": "string"},
                "interessados": {
                    "type": "object",
                    "additionalProperties": {
                        "$ref": "#/definitions/Interessado"
                    }
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
