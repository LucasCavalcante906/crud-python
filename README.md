# CRUD de Usuários — FastAPI + PostgreSQL + Docker

API REST simples para cadastro de usuários (**nome, sobrenome, telefone e endereço**),
feita com FastAPI e PostgreSQL, mais uma página web que consome a API — tudo rodando
em Docker.

Implementa os métodos HTTP: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD` e `OPTIONS`.

São três containers:

| Container       | O que é                   | Endereço                |
| --------------- | ------------------------- | ----------------------- |
| `crud_web`      | front-end (nginx)         | http://localhost:8080   |
| `crud_api`      | API FastAPI               | http://localhost:8000   |
| `crud_postgres` | banco PostgreSQL          | localhost:5432          |

---

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e Docker Compose (já vem junto no Docker Desktop)

Não é preciso ter Python nem PostgreSQL instalados na máquina.

---

## Como rodar

1. Clone/baixe o projeto e entre na pasta:

```bash
cd crud-python
```

2. (Opcional) Crie o arquivo `.env` a partir do exemplo, caso queira mudar usuário,
   senha ou portas:

```bash
cp .env.example .env
```

> No Windows (PowerShell): `Copy-Item .env.example .env`
> Sem o `.env` a aplicação usa os valores padrão (`postgres` / `postgres` / `crud_db`,
> front na porta 8080 e API na porta 8000).

3. Suba tudo:

```bash
docker compose up -d --build
```

4. Pronto. Acesse:

- **Front-end: http://localhost:8080**
- API: http://localhost:8000
- **Swagger (documentação interativa): http://localhost:8000/docs**
- ReDoc: http://localhost:8000/redoc
- Healthcheck: http://localhost:8000/health

O banco é criado automaticamente e a tabela `users` é gerada na inicialização da API.

### Comandos úteis

```bash
docker compose logs -f api      # acompanhar os logs da API
docker compose logs -f web      # logs do nginx (front)
docker compose ps               # ver status dos containers
docker compose down             # parar tudo (mantém os dados)
docker compose down -v          # parar e APAGAR os dados do banco
docker compose up -d --build    # reconstruir após mudar dependências
```

O código em `./app` está montado como volume com `--reload`: ao editar um arquivo,
a API reinicia sozinha, sem precisar rebuildar. O mesmo vale para `./frontend` —
basta salvar o `index.html` e dar F5 no navegador.

---

## Endpoints

Base: `http://localhost:8000`

| Método    | Rota           | Descrição                                   | Status de sucesso |
| --------- | -------------- | ------------------------------------------- | ----------------- |
| `GET`     | `/users`       | Lista usuários (com `skip` e `limit`)       | 200               |
| `GET`     | `/users/{id}`  | Busca um usuário pelo id                     | 200               |
| `POST`    | `/users`       | Cria um usuário                              | 201               |
| `PUT`     | `/users/{id}`  | Substitui o usuário (todos os campos)        | 200               |
| `PATCH`   | `/users/{id}`  | Atualiza parcialmente (campos opcionais)     | 200               |
| `DELETE`  | `/users/{id}`  | Remove o usuário                             | 204               |
| `HEAD`    | `/users/{id}`  | Verifica se o usuário existe (sem corpo)     | 200               |
| `OPTIONS` | `/users`       | Métodos aceitos na coleção (header `Allow`)  | 204               |
| `GET`     | `/health`      | Status da API e da conexão com o banco       | 200               |

Quando o id não existe, a resposta é `404` com `{"detail": "Usuário X não encontrado"}`.

### Campos do usuário

| Campo           | Tipo     | Obrigatório | Observação                   |
| --------------- | -------- | ----------- | ---------------------------- |
| `id`            | int      | gerado      | chave primária               |
| `nome`          | string   | sim         | 1–100 caracteres             |
| `sobrenome`     | string   | sim         | 1–100 caracteres             |
| `telefone`      | string   | sim         | 8–20 caracteres              |
| `endereco`      | string   | sim         | 1–255 caracteres             |
| `criado_em`     | datetime | gerado      | preenchido pelo banco        |
| `atualizado_em` | datetime | gerado      | atualizado a cada alteração  |

---

## Exemplos com curl

Criar (`POST`):

```bash
curl -X POST http://localhost:8000/users -H "Content-Type: application/json" -d "{\"nome\":\"Maria\",\"sobrenome\":\"Silva\",\"telefone\":\"+55 11 99999-0000\",\"endereco\":\"Rua das Flores, 123 - Sao Paulo/SP\"}"
```

Listar (`GET`):

```bash
curl http://localhost:8000/users
```

Buscar um (`GET`):

```bash
curl http://localhost:8000/users/1
```

Substituir (`PUT` — exige todos os campos):

```bash
curl -X PUT http://localhost:8000/users/1 -H "Content-Type: application/json" -d "{\"nome\":\"Maria\",\"sobrenome\":\"Souza\",\"telefone\":\"+55 11 98888-1111\",\"endereco\":\"Av. Paulista, 1000 - Sao Paulo/SP\"}"
```

Atualizar parcialmente (`PATCH`):

```bash
curl -X PATCH http://localhost:8000/users/1 -H "Content-Type: application/json" -d "{\"telefone\":\"+55 11 97777-2222\"}"
```

Remover (`DELETE`):

```bash
curl -X DELETE http://localhost:8000/users/1
```

> Dica: no Swagger (`/docs`) dá para testar todos esses endpoints pelo navegador,
> sem precisar de curl.

---

## Front-end (http://localhost:8080)

Uma página única (`frontend/index.html`) estilizada com **Tailwind CSS**, servida por
nginx. É JavaScript puro, sem build e sem framework — o Tailwind entra pela CDN.
Tem tema claro/escuro automático (segue o sistema) e funciona bem no celular.

### Duas telas

Navegação por hash, então dá para copiar e colar o link de um usuário:

| Tela         | URL                            | O que mostra |
| ------------ | ------------------------------ | ------------ |
| **Listagem** | `http://localhost:8080/#/`     | tabela paginada com avatar, nome, telefone, endereço e `atualizado_em`; controles de `skip`/`limit` e botões Anterior/Próxima |
| **Detalhe**  | `http://localhost:8080/#/users/1` | ficha completa do usuário, metadados (`criado_em`, `atualizado_em`), a resposta crua da API e a coluna de ações |

Clicar na linha (ou em "Ver") abre o detalhe. No celular a tabela encolhe para nome +
telefone e as ações ficam no detalhe.

### Modais

Toda ação de escrita acontece em um modal, que mostra no cabeçalho exatamente qual
requisição vai ser feita:

| Modal                      | Requisição                     | Detalhe |
| -------------------------- | ------------------------------ | ------- |
| **Novo usuário**           | `POST /users` → **201**        | os 4 campos, obrigatórios |
| **Editar usuário**         | `PUT /users/{id}` → **200**    | substitui o registro: envia sempre os 4 campos |
| **Atualizar campos**       | `PATCH /users/{id}` → **200**  | cada campo tem um checkbox; só os marcados entram no corpo |
| **Excluir usuário**        | `DELETE /users/{id}` → **204** | confirmação com os dados do registro |

O modal de PATCH mostra em tempo real o corpo que será enviado
(`corpo: {"telefone":"..."}`) e só habilita o botão quando há pelo menos um campo
marcado — o contrato recusa um PATCH vazio com `400`.

### Aderência ao contrato

- **Respostas sem corpo**: `DELETE` (204), `HEAD` e `OPTIONS` não têm o corpo lido.
- **Erros**: `404` e `400` mostram o `detail` (string); `422` é quebrado campo a campo,
  lendo o `loc`/`msg` de cada item da lista de erros do FastAPI, dentro do próprio modal.
- **Limites** (1–100, 8–20, 1–255) estão nos `maxlength` e escritos embaixo de cada campo.
- **HEAD** e **OPTIONS** têm botões próprios: "Checar existência · HEAD" no detalhe e
  "OPTIONS /users" no topo (mostra o header `Allow`).
- **`GET /health`** alimenta o selo do cabeçalho, revalidado a cada 30s.
- O painel **"Requisições"** (botão no topo) abre uma gaveta com método, rota e status de
  cada chamada — dá para conferir o contrato em tempo real enquanto usa a tela.

O nginx faz proxy de `/api/` para o container da API, então o navegador chama
`/api/users` (mesma origem) e não depende de CORS. A configuração está em
[`nginx/default.conf`](nginx/default.conf).

---

## Estrutura do projeto

```
crud-python/
├── app/
│   ├── main.py            # cria o app, healthcheck e cria as tabelas no startup
│   ├── config.py          # lê as variáveis de ambiente e monta a URL do banco
│   ├── database.py        # engine, sessão e Base do SQLAlchemy
│   ├── models.py          # tabela users
│   ├── schemas.py         # validação de entrada/saída (Pydantic)
│   ├── crud.py            # operações no banco
│   └── routers/
│       └── users.py       # endpoints /users
├── frontend/
│   └── index.html         # front completo: Tailwind + JS puro, 2 telas e os modais
├── nginx/
│   └── default.conf       # serve o front e faz proxy de /api -> api:8000
├── Dockerfile             # imagem da API
├── docker-compose.yml     # front (nginx) + API + PostgreSQL
├── requirements.txt
├── .env.example
└── README.md
```

---

## Acessar o banco direto

```bash
docker compose exec db psql -U postgres -d crud_db -c "SELECT * FROM users;"
```

Para conectar com um cliente externo (DBeaver, pgAdmin): `localhost:5432`,
banco `crud_db`, usuário `postgres`, senha `postgres`.

---

## Rodando sem Docker (opcional)

Você precisa de um PostgreSQL rodando localmente.

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
```

Crie um `.env` apontando para o seu banco (note o `POSTGRES_HOST=localhost`,
já que fora do Docker não existe o host `db`):

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=crud_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

E rode:

```bash
uvicorn app.main:app --reload
```

---

## Problemas comuns

- **`Error response from daemon: Docker Desktop is unable to start`**: normalmente é o
  kernel do WSL 2 faltando ou desatualizado. Abra um PowerShell **como
  administrador** e rode:

  ```bash
  wsl --update
  ```

  Reinicie o Docker Desktop (ou a máquina) e tente `docker compose up -d --build` de novo.
  Confirme também que a virtualização está habilitada na BIOS e que os recursos
  "Plataforma de Máquina Virtual" e "Subsistema do Windows para Linux" estão ativos
  em *Ativar ou desativar recursos do Windows*.
- **`port is already allocated` / porta 5432, 8000 ou 8080 ocupada**: crie o `.env` e mude
  `POSTGRES_PORT_EXTERNO`, `API_PORT` ou `WEB_PORT` (ex.: `5433`, `8001` e `8081`), depois
  `docker compose up -d`.
- **A página aparece sem estilo nenhum**: o Tailwind vem da CDN
  (`cdn.tailwindcss.com`), então é preciso ter internet. A API e o banco continuam
  funcionando normalmente offline — só o visual se perde.
- **Editei o `index.html` e o navegador mostra a versão antiga**: o nginx já responde
  `Cache-Control: no-cache`, mas se persistir force a recarga (Ctrl+F5).
- **Abrir o `index.html` com duplo clique não funciona direito**: nesse caso não há o proxy
  do nginx, então a página cai no fallback `http://localhost:8000` e depende de CORS.
  Use sempre http://localhost:8080.
- **API sobe antes do banco**: já tratado — o compose espera o healthcheck do
  Postgres e a API ainda tenta reconectar por ~20s no startup.
- **Mudou usuário/senha e o login falha**: as credenciais só são aplicadas na
  criação do volume. Rode `docker compose down -v` para recriar o banco do zero.
- **Alterou o `requirements.txt`**: rebuilde com `docker compose up -d --build`.
