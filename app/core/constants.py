STATUS_PENDENTE = 1
STATUS_PROCESSADO = 2
STATUS_LABEL: dict[int, str] = {
    STATUS_PENDENTE: "Pendente",
    STATUS_PROCESSADO: "Processado",
}

PRIORIDADE_INDEFINIDA = "prioridade_indefinida"
PRIORIDADE_NORMAL = "prioridade_normal"
PRIORIDADE_ALTA = "prioridade_alta"
PRIORIDADE_LABEL: dict[str, str] = {
    PRIORIDADE_INDEFINIDA: "Indefinido",
    PRIORIDADE_NORMAL: "Normal",
    PRIORIDADE_ALTA: "Alta",
}
