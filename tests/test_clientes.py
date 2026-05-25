async def test_create_cliente_valido(client, mock_pipefy):
    payload = {
        "cliente_nome": "João Silva",
        "cliente_email": "joao.silva@example.com",
        "tipo_solicitacao": "Atualização cadastral",
        "valor_patrimonio": 25_000_000,  # R$ 250.000,00 em centavos
    }

    response = await client.post("/clientes", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "joao.silva@example.com"
    assert data["nome"] == "João Silva"
    assert data["valor_patrimonio"] == 25_000_000
    assert data["status"] == "Aguardando Análise"
    mock_pipefy.create_card.assert_called_once_with(
        nome="João Silva",
        email="joao.silva@example.com",
        valor_patrimonio=25_000_000,
    )


async def test_create_cliente_email_duplicado(client, mock_pipefy):
    payload = {
        "cliente_nome": "João Silva",
        "cliente_email": "joao.silva@example.com",
        "tipo_solicitacao": "Atualização cadastral",
        "valor_patrimonio": 25_000_000,
    }

    await client.post("/clientes", json=payload)
    response = await client.post("/clientes", json=payload)

    assert response.status_code == 409
    assert "Email já cadastrado" in response.json()["detail"]
