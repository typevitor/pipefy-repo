import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)

ENDPOINT = "https://api.pipefy.com/graphql"

CREATE_CARD_MUTATION = """
mutation CreateCard($input: CreateCardInput!) {
  createCard(input: $input) {
    card {
      id
      title
    }
  }
}
"""

UPDATE_FIELDS_MUTATION = """
mutation UpdateFieldsValues($input: UpdateFieldsValuesInput!) {
  updateFieldsValues(input: $input) {
    success
  }
}
"""


class PipefyClient:
    def __init__(self) -> None:
        self._s = get_settings()

    async def create_card(self, nome: str, email: str, valor_patrimonio: int) -> str:
        variables = {
            "input": {
                "pipe_id": self._s.pipefy_pipe_id,
                "title": nome,
                "fields_attributes": [
                    {"field_id": self._s.pipefy_field_nome, "field_value": nome},
                    {"field_id": self._s.pipefy_field_email, "field_value": email},
                    {
                        "field_id": self._s.pipefy_field_patrimonio,
                        "field_value": str(valor_patrimonio),
                    },
                ],
            }
        }
        logger.info(
            "[PIPEFY SIMULATION] createCard\nQuery:%s\nVariables: %s",
            CREATE_CARD_MUTATION,
            variables,
        )
        card_id = str(abs(hash(email)) % 10**9)
        logger.info("[PIPEFY SIMULATION] card_id=%s", card_id)
        return card_id

    async def update_card_fields(
        self, card_id: str, status: str, prioridade: str
    ) -> bool:
        variables = {
            "input": {
                "nodeId": int(card_id),  # Pipefy schema: nodeId is Int
                "values": [
                    {"fieldId": self._s.pipefy_field_status, "value": status},
                    {"fieldId": self._s.pipefy_field_prioridade, "value": prioridade},
                ],
            }
        }
        logger.info(
            "[PIPEFY SIMULATION] updateFieldsValues\nQuery:%s\nVariables: %s",
            UPDATE_FIELDS_MUTATION,
            variables,
        )
        return True
