async def test_create_cliente_valido(client, mock_pipefy):
    payload = {
        "cliente_nome": "João Silva",
        "cliente_email": "joao.silva@example.com",
        "tipo_solicitacao": "Atualização cadastral",
        "valor_patrimonio": 250_000,
    }

    response = await client.post("/clientes", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "joao.silva@example.com"
    assert data["nome"] == "João Silva"
    assert data["valor_patrimonio"] == 250_000
    assert data["status"] == "Pendente"
    assert data["prioridade"] == "prioridade_indefinida"
    assert data["prioridade_label"] == "Indefinido"
    mock_pipefy.create_card.assert_called_once_with(
        nome="João Silva",
        email="joao.silva@example.com",
        valor_patrimonio=250_000,
    )


async def test_create_cliente_email_duplicado(client, mock_pipefy):
    payload = {
        "cliente_nome": "João Silva",
        "cliente_email": "joao.silva@example.com",
        "tipo_solicitacao": "Atualização cadastral",
        "valor_patrimonio": 250_000,
    }

    await client.post("/clientes", json=payload)
    response = await client.post("/clientes", json=payload)

    assert response.status_code == 409
    assert "Email já cadastrado" in response.json()["detail"]


async def test_create_cliente_patrimonio_invalido(client):
    response = await client.post("/clientes", json={
        "cliente_nome": "João Silva",
        "cliente_email": "joao.silva@example.com",
        "tipo_solicitacao": "Atualização cadastral",
        "valor_patrimonio": 0,
    })
    assert response.status_code == 422


async def test_create_cliente_email_invalido(client):
    response = await client.post("/clientes", json={
        "cliente_nome": "João Silva",
        "cliente_email": "nao-e-um-email",
        "tipo_solicitacao": "Atualização cadastral",
        "valor_patrimonio": 250_000,
    })
    assert response.status_code == 422
