#  Projeto de Bloco: Agentes de IA e Desenvolvimento Seguro de APIs

Este projeto consiste em uma solução ponta a ponta para um sistema agêntico de suporte ao cliente, integrando **Análise Exploratória de Dados (EDA)** e uma **API RESTful desenvolvida em FastAPI**. A aplicação foi projetada seguindo rigorosas práticas de **Desenvolvimento Seguro (AppSec)** e recomendações do **OWASP Top 10**, com persistência relacional em **SQLite/SQLModel**, autenticação **JWT**, controle de acesso baseado em propriedade (**ownership/BOLA**), **hardening de cabeçalhos HTTP**, **CORS estrito** e **rate limiting**.

---

## Estrutura do Repositório

```text
.
├── README.md                 # Documentação principal com instruções e arquitetura
├── data/
│   └── customer_support_tickets.csv # Dataset oficial do Customer Support Ticket
├── eda/
│   └── eda_pb.ipynb    # Notebook Jupyter com a Análise Exploratória de Dados
├── fastapi/
│   ├── config/               # Configurações centralizadas (BaseSettings e SlowAPI)
│   ├── database/             # Conexão e sessão do banco de dados SQLite
│   ├── models/               # Modelos Pydantic (DTOs) e SQLModel (DAOs)
│   ├── routes/               # Roteadores modulares (/health, /auth, /predict)
│   ├── security/             # Autenticação JWT e Middlewares de segurança
│   ├── main.py               # Ponto de entrada da aplicação FastAPI
│   ├── sqlite_database.py    # Script de criação e população inicial do banco
│   ├── database.db           # Banco de dados SQLite populado
│   ├── requirements.txt          # Dependências do projeto Python
│   └──tests/
│      ├── conftest.py           # Fixtures e configurações do Pytest (SQLite em memória)
│      ├── test_predict.py       # Testes automatizados da rota /predict (BOLA e Mass Assignment)
│      └── test_security.py      # Testes automatizados de segurança (401 sem token, 429 Rate Limit)
└── zap/
    ├── scan_passivo_zap.md   # Análise técnica dos achados do scan passivo OWASP ZAP
    └── owasp_zap_report.html # Relatório bruto exportado pelo OWASP ZAP
```

---

##  Pré-requisitos e Instalação

### 1. Clonar o Repositório e Acessar o Diretório

```bash
git clone <https://github.com/MatheusSantos285/matheus-pedro-leonardo.git>
cd <matheus-pedro-leonardo>
```

### 2. Criar e Ativar o Ambiente Virtual

- **Linux / macOS:**

  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

- **Windows (PowerShell):**

  ```powershell
  python -m venv .venv
  \.venv\Scripts\Activate.ps1
  ```

### 3. Instalar as Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

##  Criação e População do Banco de Dados

O banco de dados relacional utiliza o **SQLite** com mapeamento ORM via **SQLModel**.

Para criar as tabelas e popular o banco inicial (`fastapi/database.db`) com usuários de exemplo (`admin` e `analyst_01`) e predições associadas a diferentes proprietários (`owner_id`):

```bash
python fastapi/sqlite_database.py
```

> **Nota:** A aplicação também possui verificação automática no gerenciador de ciclo de vida (`lifespan` no `main.py`), garantindo que a estrutura da base de dados seja instanciada e populada caso o arquivo `database.db` ainda não exista.

---

## Execução da API FastAPI

Para iniciar o servidor local de desenvolvimento com *hot reload*:

```bash
uvicorn fastapi.main:app --reload
```

A API estará acessível em:

- **Base URL:** `http://127.0.0.1:8000`
- **Documentação Interativa (Swagger UI):** `http://127.0.0.1:8000/docs`
- **Documentação Alternativa (ReDoc):** `http://127.0.0.1:8000/redoc`

---

## Execução dos Testes Automatizados (Pytest)

A suíte de testes utiliza um banco SQLite isolado em memória (`sqlite://`) para garantir que os testes sejam reproduzíveis e não afetem o banco de desenvolvimento.

Os testes cobrem obrigatoriamente:

1. **Tentativa de acesso sem token JWT** (Retorna `HTTP 401 Unauthorized`).
2. **Acesso e isolamento de recursos por propriedade / BOLA** (Garante vinculação via `owner_id`).
3. **Envio de campos extras não mapeados no payload** (Bloqueado com `HTTP 422 Unprocessable Entity` via `extra="forbid"` do Pydantic).
4. **Proteção contra ataques de força bruta no login** (Retorna `HTTP 429 Too Many Requests` após o limite do Rate Limit).

Para rodar todos os testes:

```bash
pytest -v
```

---

## Destaques de Segurança e Controles OWASP Top 10

- **Autenticação JWT (`/auth/token`):** Emissão de tokens Bearer com senhas armazenadas em hash criptográfico (`bcrypt`).
- **Rate Limiting (`SlowAPI`):** Limite estrito de **10 requisições/minuto** no endpoint de autenticação para mitigar Brute Force.
- **Validação Estrita na Borda (Pydantic):** Uso de Enums e `model_config = ConfigDict(extra="forbid")` para anular ataques de *Mass Assignment* (OWASP A08).
- **Controle de Acesso em Nível de Objeto (BOLA / OWASP A01):** O `owner_id` de cada registro é extraído diretamente da identidade do token JWT autenticado, prevenindo adulteração de IDs por parte do cliente.
- **Prevenção de SQL Injection (OWASP A05):** Consultas 100% parametrizadas através da interface ORM do SQLModel.
- **Hardening de Cabeçalhos HTTP:** Middleware injetando `Strict-Transport-Security` (HSTS), `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff` e `Content-Security-Policy` (CSP).
- **Política CORS Restritiva:** Configuração de allowlist explícita de origens permitidas, eliminando a permissividade de wildcard (`*`).
- **Auditoria OWASP ZAP:** Scan passivo executado e documentado em `zap/scan_passivo_zap.md`.
