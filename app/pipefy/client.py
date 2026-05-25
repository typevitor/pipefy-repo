import logging

import httpx

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


def _check_graphql_errors(body: dict) -> None:
    """GraphQL always returns HTTP 200; errors appear in the body, not the status."""
    if "errors" in body:
        msg = body["errors"][0].get("message", "unknown GraphQL error")
        raise RuntimeError(f"Pipefy GraphQL error: {msg}")


class PipefyClient:
    def __init__(self) -> None:
        self._s = get_settings()
        self._headers = {
            "Authorization": f"Bearer {self._s.pipefy_token}",
            "Content-Type": "application/json",
        }

    async def create_card(self, nome: str, email: str, valor_patrimonio: int) -> str:
        patrimonio_reais = f"{valor_patrimonio / 100:.2f}"
        variables = {
            "input": {
                "pipe_id": self._s.pipefy_pipe_id,
                "title": nome,
                "fields_attributes": [
                    {"field_id": self._s.pipefy_field_nome, "field_value": nome},
                    {"field_id": self._s.pipefy_field_email, "field_value": email},
                    {"field_id": self._s.pipefy_field_patrimonio, "field_value": patrimonio_reais},
                ],
            }
        }
        async with httpx.AsyncClient() as http:
            resp = await http.post(
                ENDPOINT,
                json={"query": CREATE_CARD_MUTATION, "variables": variables},
                headers=self._headers,
                timeout=10.0,
            )
            resp.raise_for_status()
            body = resp.json()
            _check_graphql_errors(body)
            return str(body["data"]["createCard"]["card"]["id"])

    async def update_card_fields(
        self, card_id: str, status: str, prioridade: str
    ) -> bool:
        variables = {
            "input": {
                "nodeId": int(card_id),
                "values": [
                    {"fieldId": self._s.pipefy_field_status, "value": status},
                    {"fieldId": self._s.pipefy_field_prioridade, "value": prioridade},
                ],
            }
        }
        async with httpx.AsyncClient() as http:
            resp = await http.post(
                ENDPOINT,
                json={"query": UPDATE_FIELDS_MUTATION, "variables": variables},
                headers=self._headers,
                timeout=10.0,
            )
            resp.raise_for_status()
            body = resp.json()
            _check_graphql_errors(body)
            return bool(body["data"]["updateFieldsValues"]["success"])
