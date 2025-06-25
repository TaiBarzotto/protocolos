# Academico.Bot 🤖

API para automação de operações no SIGAA (Sistema Integrado de Gestão de Atividades Acadêmicas) utilizando RPA (Robotic Process Automation).

## 📋 Descrição

O Academico.Bot é uma API REST desenvolvida em Flask que automatiza operações no sistema SIGAA, permitindo:

- Cadastro e edição de CCRs (Componentes Curriculares)
- Gerenciamento de objetivos de CCRs
- Autenticação via JWT
- Documentação interativa com Swagger

## 🚀 Funcionalidades

### CCR (Componentes Curriculares)
- ✅ **Cadastro de CCR** - Inserção automática de novos componentes curriculares
- ✅ **Edição de CCR** - Atualização de componentes existentes
- ✅ **Edição de Objetivos** - Gerenciamento específico de objetivos de CCRs

### Integração Externa
- 🔐 **Cofre de Senhas** - Integração segura para credenciais
- 🎯 **SIGAA** - Automação completa do sistema acadêmico

### Segurança
- 🛡️ **Autenticação JWT** - Tokens de acesso seguros
- 🔑 **Gestão de Credenciais** - Integração com cofre de senhas
- 📊 **Logs e Auditoria** - Rastreamento de operações

## 🛠️ Tecnologias

- **Python 3.x**
- **Flask** - Framework web
- **Selenium** - Automação web (RPA)
- **Pydantic** - Validação de dados
- **Swagger/Flasgger** - Documentação da API
- **JWT** - Autenticação
- **MySQL/PostgreSQL** - Banco de dados

## 📦 Instalação

### Pré-requisitos

```bash
# Python 3.8+
python --version

# Gerenciador de pacotes pip
pip --version
```

### Clonagem e Configuração

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd academico.bot

# Instale as dependências
pip install -r requirements.txt
```

### Dependências Principais

```txt
flask>=2.0.0
selenium>=4.0.0
pydantic>=1.8.0
flasgger>=0.9.0
flask-pydantic-spec
PyJWT>=2.0.0
mysql-connector-python
python-dotenv
```

## 🚀 Execução

### Desenvolvimento

```bash
py main.py
```

## 📚 Uso da API

### Endpoints Principais

#### 🏠 Home
```http
GET /
```
Página inicial com links para documentação.

#### 🔐 Autenticação
```http
POST /ccrs/auth
Content-Type: application/json

{
  "username": "seu_usuario"
}
```

**Resposta:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 📝 Cadastrar CCR
```http
POST /ccrs/ccr
Authorization: Bearer {token}
Content-Type: application/json

{
  "id": 1,
  "codigo": "GEX001",
  "descricao": "Introdução à Programação",
  "unidade": "Departamento de Computação",
  "carga_horaria_presencial": 60,
  "carga_horaria_ead": 0,
  "hrs_presencial_teorica": 40,
  "hrs_presencial_pratica": 20,
  "hrs_presencial_extensao": 0,
  "hrs_ead_teorica": 0,
  "hrs_ead_pratica": 0,
  "hrs_estagio_presencial": 0,
  "hrs_estagio_ead": 0,
  "hrs_estagio_extensionista": 0,
  "hrs_tcc_discente_orientada": 0,
  "modalidade": 1,
  "dominio": 1,
  "ementa": "Fundamentos de programação...",
  "num_avaliacoes": 3,
  "objetivo": "Capacitar o aluno...",
  "optativa": false,
  "cadastrada": false,
  "referencias_basicas": {
    "ref1": "Autor, A. Título do Livro. Editora, 2023."
  },
  "referencias_complementares": {
    "ref1": "Autor, B. Outro Título. Editora, 2022."
  }
}
```

#### ✏️ Editar CCR
```http
POST /ccrs/edit_ccr
Authorization: Bearer {token}
Content-Type: application/json

{
  "codigo": "CCR001",
  "descricao": "Nova descrição",
  // ... outros campos
}
```

#### 🎯 Editar Objetivo do CCR
```http
POST /ccrs/edit_ccr_objetivo
Authorization: Bearer {token}
Content-Type: application/json

{
  "codigo": "CCR001",
  "objetivo": "Novo objetivo do componente curricular..."
}
```

### Códigos de Resposta

| Código | Descrição |
|--------|-----------|
| 200 | ✅ Operação realizada com sucesso |
| 400 | ❌ Erro na validação dos dados |
| 401 | 🔒 Token inválido ou ausente |
| 500 | 💥 Erro interno do servidor |

### Exemplo de Resposta de Sucesso

```json
{
  "status": "Sucesso",
  "detalhes": {
    "mensagem": "CCR e Objetivo cadastrados com sucesso"
  }
}
```

## 📖 Documentação

### Swagger UI

Acesse a documentação interativa em:
```
http://localhost:8077/apidocs/
```

### Modelos de Dados

#### CCR (Componente Curricular)
```python
{
  "id": int,
  "codigo": str,
  "descricao": str,
  "unidade": str,
  "carga_horaria_presencial": int,
  "carga_horaria_ead": int,
  "modalidade": int,
  "ementa": str,
  "objetivo": str,
  "referencias_basicas": dict,
  "referencias_complementares": dict
}
```

#### Objetivo
```python
{
  "codigo": str,
  "objetivo": str
}
```

## 🔧 Desenvolvimento

### Estrutura do Projeto

```
academico-bot/
├── apps/
│   ├── __init__.py              # Configuração principal da aplicação
│   ├── trab_com_ccrs/          # Módulo de CCRs
│   │   ├── routes.py           # Rotas da API
│   │   ├── models.py           # Modelos Pydantic
│   │   ├── cadastro_ccr.py     # RPA para cadastro
│   │   └── editar_ccr.py       # RPA para edição
│   ├── utilities/              # Utilitários
│   ├── navegar_no_sig/         # Navegação no SIGAA
│   └── config/                 # Configurações
├── requirements.txt
├── config.ini
└── README.md
```

## 🔒 Segurança

### Práticas Implementadas

- ✅ **Autenticação JWT** com expiração
- ✅ **Validação de entrada** com Pydantic
- ✅ **Cofre de senhas** para credenciais
- ✅ **Logs de auditoria** para rastreamento
- ✅ **Tratamento de erros** robusto

### Configurações de Segurança

```python
# Configurar chave secreta forte
JWT_SECRET_KEY = 'sua-chave-muito-segura-aqui'

# Definir tempo de expiração do token
JWT_EXPIRATION_DELTA = datetime.timedelta(hours=24)
```

## 📊 Monitoramento

### Logs

Os logs são registrados com informações sobre:
- Tentativas de login
- Operações realizadas
- Erros e exceções
- Performance das operações RPA

## 📝 Changelog

### v1.0.0 (2025-07-01)
- ✨ Implementação inicial da API
- ✨ Cadastro e edição de CCRs
- ✨ Autenticação JWT
- ✨ Documentação Swagger


## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.