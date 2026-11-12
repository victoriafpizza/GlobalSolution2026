"""Classificação de prioridade por tipo de obstáculo."""

import unicodedata


def classificar(tipo):
    decomposto = unicodedata.normalize("NFD", tipo.casefold())
    sem_acentos = "".join(letra for letra in decomposto if not unicodedata.combining(letra))
    normalizado = " ".join(sem_acentos.split())

    if normalizado in {"rampa bloqueada", "travessia perigosa"}:
        return "alta"
    elif normalizado == "calcada danificada":
        return "media"
    else:
        return "baixa"
