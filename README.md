# pipefy-test — Client Management & Pipefy Integration

FastAPI + SQLite API que gerencia clientes e integra com o Pipefy via GraphQL.

As chamadas ao Pipefy são **simuladas**: o código monta as mutations exatas conforme a documentação oficial e as registra em log, mas não faz requests HTTP ao servidor do Pipefy.

---

## Pré-requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (`pip install uv`)
- Docker + Docker Compose (para execução em container)

---

## Configuração

```bash
cp .env.example .env
```

| Variável | Obrigatória | Descrição |
|---|---|---|
| `PIPEFY_TOKEN` | ✅ | Service Account token (Settings → Service Accounts no Pipefy) |
| `PIPEFY_PIPE_ID` | ✅ | ID numérico do Pipe de destino |
| `PIPEFY_WEBHOOK_SECRET` | ✅ | Segredo compartilhado para autenticar webhooks (header `X-Webhook-Secret`) |
| `PIPEFY_FIELD_NOME` | — | `field_id` do campo nome (default: `employee_name`) |
| `PIPEFY_FIELD_EMAIL` | — | `field_id` do campo email (default: `email`) |
| `PIPEFY_FIELD_PATRIMONIO` | — | `field_id` do campo patrimônio (default: `patrimonio`) |
| `PIPEFY_FIELD_STATUS` | — | `field_id` do campo status (default: `status`) |
| `PIPEFY_FIELD_PRIORIDADE` | — | `field_id` do campo prioridade (default: `prioridade`) |

Os `field_id`s podem ser encontrados via: `query { pipe(id: <ID>) { fields { id label } } }`.

---

## Execução local

```bash
uv sync --dev
uv run uvicorn app.main:app --reload
```

API em `http://localhost:8000`. Docs interativas: `http://localhost:8000/docs`.

---

## Execução via Docker Compose

```bash
docker compose up --build
```

---

## Testes

```bash
PIPEFY_TOKEN=test PIPEFY_PIPE_ID=1 PIPEFY_WEBHOOK_SECRET=test-webhook-secret uv run pytest -v
```

---

## Regra de prioridade

| `valor_patrimonio` | Prioridade |
|---|---|
| `>= 200000` (R$ 200.000,00) | `prioridade_alta` |
| `< 200000` | `prioridade_normal` |

`valor_patrimonio` é um inteiro em reais. Exemplo: R$ 250.000,00 → `250000`.

---

## Exemplos de requisição

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

Segunda chamada com o mesmo `event_id`:
```json
{ "status": "already_processed", "prioridade": null }
```

---

## Visão de Produção na AWS (opcional)

**Recepção de webhooks:** Endpoint `POST /webhooks/pipefy/card-updated` exposto via **API Gateway** + **AWS Lambda** (Python). Estado em **DynamoDB** com idempotência garantida por `ConditionExpression: attribute_not_exists(event_id)` — atômico, sem race condition.

**Banco relacional:** Para volumes maiores, substituir SQLite por **RDS (PostgreSQL)** com read replica.

**Segredos:** `PIPEFY_TOKEN` e `PIPEFY_WEBHOOK_SECRET` no **AWS Secrets Manager**, injetados como variáveis de ambiente na Lambda — nunca em código ou imagem Docker.

**Escala:** API Gateway + Lambda escalam automaticamente com o volume de webhooks.
