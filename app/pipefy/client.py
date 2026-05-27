import logging

from gql import Client, gql
from gql.transport.httpx import HTTPXAsyncTransport

from app.core.config import get_settings

logger = logging.getLogger(__name__)

FIELD_NOME = "employee_name"
FIELD_EMAIL = "email"
FIELD_PATRIMONIO = "patrimonio"
FIELD_STATUS = "status"
FIELD_PRIORIDADE = "prioridade"

CREATE_CARD_MUTATION = gql("""
    mutation CreateCard($input: CreateCardInput!) {
      createCard(input: $input) {
        card {
          id
          title
        }
      }
    }
""")

UPDATE_FIELDS_MUTATION = gql("""
    mutation UpdateFieldsValues($input: UpdateFieldsValuesInput!) {
      updateFieldsValues(input: $input) {
        success
      }
    }
""")


class PipefyClient:
    def __init__(self) -> None:
        self._s = get_settings()
        transport = HTTPXAsyncTransport(
            url=self._s.pipefy_endpoint,
            headers={"Authorization": f"Bearer {self._s.pipefy_token}"},
        )
        self._client = Client(transport=transport)

    async def create_card(self, nome: str, email: str, valor_patrimonio: int) -> str:
        variables = {
            "input": {
                "pipe_id": self._s.pipefy_pipe_id,
                "title": nome,
                "fields_attributes": [
                    {"field_id": FIELD_NOME, "field_value": nome},
                    {"field_id": FIELD_EMAIL, "field_value": email},
                    {"field_id": FIELD_PATRIMONIO, "field_value": str(valor_patrimonio)},
                ],
            }
        }
        logger.info("[PIPEFY SIMULATION] createCard variables=%s", variables)
        # produção: result = await self._client.execute_async(CREATE_CARD_MUTATION, variable_values=variables)
        # produção: return result["createCard"]["card"]["id"]
        card_id = str(abs(hash(email)) % 10**9)
        logger.info("[PIPEFY SIMULATION] card_id=%s", card_id)
        return card_id

    async def update_card_fields(self, card_id: str, status: str, prioridade: str) -> bool:
        variables = {
            "input": {
                "nodeId": int(card_id),
                "values": [
                    {"fieldId": FIELD_STATUS, "value": status},
                    {"fieldId": FIELD_PRIORIDADE, "value": prioridade},
                ],
            }
        }
        logger.info("[PIPEFY SIMULATION] updateFieldsValues variables=%s", variables)
        # produção: result = await self._client.execute_async(UPDATE_FIELDS_MUTATION, variable_values=variables)
        # produção: return result["updateFieldsValues"]["success"]
        return True
