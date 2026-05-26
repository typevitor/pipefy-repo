from tests.conftest import TEST_WEBHOOK_SECRET

AUTH = {"X-Webhook-Secret": TEST_WEBHOOK_SECRET}


async def test_webhook_prioridade_alta(client, mock_pipefy):
    await client.post("/clientes", json={
        "cliente_nome": "João Silva",
        "cliente_email": "joao.silva@example.com",
        "tipo_solicitacao": "Atualização cadastral",
        "valor_patrimonio": 250_000,
    })

    response = await client.post("/webhooks/pipefy/card-updated", json={
        "event_id": "evt_001",
        "card_id": "card_001",
        "cliente_email": "joao.silva@example.com",
        "timestamp": "2026-05-25T12:00:00Z",
    }, headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
    assert data["prioridade"] == "prioridade_alta"


async def test_webhook_prioridade_normal(client, mock_pipefy):
    await client.post("/clientes", json={
        "cliente_nome": "Maria Santos",
        "cliente_email": "maria.santos@example.com",
        "tipo_solicitacao": "Cadastro novo",
        "valor_patrimonio": 100_000,
    })

    response = await client.post("/webhooks/pipefy/card-updated", json={
        "event_id": "evt_002",
        "card_id": "card_002",
        "cliente_email": "maria.santos@example.com",
        "timestamp": "2026-05-25T12:00:00Z",
    }, headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
    assert data["prioridade"] == "prioridade_normal"


async def test_webhook_sem_autenticacao(client, mock_pipefy):
    response = await client.post("/webhooks/pipefy/card-updated", json={
        "event_id": "evt_003",
        "card_id": "card_003",
        "cliente_email": "joao.silva@example.com",
        "timestamp": "2026-05-25T12:00:00Z",
    })

    assert response.status_code == 401


async def test_webhook_cliente_nao_encontrado(client, mock_pipefy):
    response = await client.post("/webhooks/pipefy/card-updated", json={
        "event_id": "evt_004",
        "card_id": "card_004",
        "cliente_email": "desconhecido@example.com",
        "timestamp": "2026-05-25T12:00:00Z",
    }, headers=AUTH)

    assert response.status_code == 404


async def test_webhook_idempotencia(client, mock_pipefy):
    await client.post("/clientes", json={
        "cliente_nome": "Carlos Oliveira",
        "cliente_email": "carlos.oliveira@example.com",
        "tipo_solicitacao": "Resgate",
        "valor_patrimonio": 300_000,
    })

    payload = {
        "event_id": "evt_dup",
        "card_id": "card_003",
        "cliente_email": "carlos.oliveira@example.com",
        "timestamp": "2026-05-25T12:00:00Z",
    }

    r1 = await client.post("/webhooks/pipefy/card-updated", json=payload, headers=AUTH)
    assert r1.status_code == 200
    assert r1.json()["status"] == "processed"

    r2 = await client.post("/webhooks/pipefy/card-updated", json=payload, headers=AUTH)
    assert r2.status_code == 200
    assert r2.json()["status"] == "already_processed"

    assert mock_pipefy.update_card_fields.call_count == 1
