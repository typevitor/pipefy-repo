# pipefy-test

## Contexto

API REST construída com **FastAPI + SQLite** para gerenciar clientes e integrar com o **Pipefy** via GraphQL.

O fluxo principal é:

1. Um cliente é cadastrado via `POST /clientes` — o sistema cria o registro no banco e dispara a criação de um card no Pipefy.
2. Quando o card é movido no Pipefy, um webhook `POST /webhooks/pipefy/card-updated` atualiza o status e a prioridade do cliente no banco.

As chamadas ao Pipefy são **simuladas**: o código monta as mutations GraphQL exatas conforme a documentação oficial e as registra em log, mas não faz requests HTTP ao servidor do Pipefy.

**Regra de prioridade:**

| `valor_patrimonio` | Prioridade |
|---|---|
| `>= 200000` | `prioridade_alta` |
| `< 200000` | `prioridade_normal` |

`valor_patrimonio` é um inteiro em **centavos**. Exemplo: R$ 2.500,00 → `250000`.

---

## Como Rodar

**Pré-requisitos:** Docker e Docker Compose instalados.

### Passo a passo

```bash
# 1. Clone o repositório e entre na pasta
git clone <url-do-repo>
cd pipefy_test

# 2. Torne o script executável e rode
chmod +x scripts/init.sh
./scripts/init.sh
```

Na primeira execução, se o `.env` não existir, o script cria um a partir do `.env.example` e encerra. Preencha as variáveis obrigatórias e rode `./scripts/init.sh` novamente.

| Variável | Obrigatória | Descrição |
|---|---|---|
| `PIPEFY_TOKEN` | ✅ | Service Account token (Settings → Service Accounts no Pipefy) |
| `PIPEFY_PIPE_ID` | ✅ | ID numérico do Pipe de destino |
| `PIPEFY_WEBHOOK_SECRET` | ✅ | Segredo compartilhado para autenticar webhooks (header `X-Webhook-Secret`) |

Após subir, a API estará disponível em `http://localhost:8000` e a documentação interativa em `http://localhost:8000/docs`.

### Execução local (sem Docker)

```bash
uv sync --dev
uv run uvicorn app.main:app --reload
```

---

## Testes

Os testes usam SQLite in-memory e Pipefy mockado — não dependem do `.env` de produção.

```bash
docker compose run --rm api sh -c \
  "PIPEFY_TOKEN=test PIPEFY_PIPE_ID=1 PIPEFY_WEBHOOK_SECRET=test-webhook-secret uv run pytest -v"
```

---

## Exemplos de Chamadas

### Criar cliente

```bash
curl -X POST http://localhost:8000/clientes \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_nome": "João Silva",
    "cliente_email": "joao.silva@example.com",
    "tipo_solicitacao": "Atualização cadastral",
    "valor_patrimonio": 250000
  }'
```

Resposta `201 Created`:
```json
{
  "id": 1,
  "nome": "João Silva",
  "email": "joao.silva@example.com",
  "tipo_solicitacao": "Atualização cadastral",
  "valor_patrimonio": 250000,
  "status": "Aguardando Análise",
  "prioridade": null,
  "pipefy_card_id": "123456789"
}
```

### Buscar cliente por e-mail

```bash
curl http://localhost:8000/clientes/joao.silva@example.com
```

Resposta `200 OK`:
```json
{
  "id": 1,
  "nome": "João Silva",
  "email": "joao.silva@example.com",
  "tipo_solicitacao": "Atualização cadastral",
  "valor_patrimonio": 250000,
  "status": "Aguardando Análise",
  "prioridade": null,
  "pipefy_card_id": "123456789"
}
```

### Processar webhook

Requer o header `X-Webhook-Secret` com o valor de `PIPEFY_WEBHOOK_SECRET`. Requisições sem o header ou com valor errado retornam `401`.

```bash
curl -X POST http://localhost:8000/webhooks/pipefy/card-updated \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: <seu-secret>" \
  -d '{
    "event_id": "evt_123",
    "card_id": "card_456",
    "cliente_email": "joao.silva@example.com",
    "timestamp": "2026-05-25T12:00:00Z"
  }'
```

Resposta `200 OK`:
```json
{ "status": "processed", "prioridade": "prioridade_alta" }
```

Segunda chamada com o mesmo `event_id` (idempotência):
```json
{ "status": "already_processed", "prioridade": null }
```

---

## Visão de Produção na AWS
