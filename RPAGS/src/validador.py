"""Validação dos campos obrigatórios de cada obstáculo."""


CAMPOS = ("id", "tipo", "descricao", "latitude", "longitude", "status")


def validar(registro):
    if not isinstance(registro, dict):
        return ["O registro deve ser um objeto JSON."]

    erros = []
    for campo in CAMPOS:
        if campo not in registro:
            erros.append(f"Campo obrigatório ausente: {campo}.")
            continue

        valor = registro[campo]
        if campo == "id":
            if type(valor) is not int and not (isinstance(valor, str) and valor.strip()):
                erros.append("O id deve ser um inteiro ou texto não vazio.")
        elif campo in ("latitude", "longitude"):
            limite = 90 if campo == "latitude" else 180
            if type(valor) not in (int, float) or not -limite <= valor <= limite:
                erros.append(f"{campo} deve ser um número entre {-limite} e {limite}.")
        else:
            if not isinstance(valor, str) or not valor.strip():
                erros.append(f"{campo} deve ser um texto não vazio.")
    return erros
