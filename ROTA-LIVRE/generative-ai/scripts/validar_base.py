"""Valida o acervo e o gabarito sem rede ou dependências externas."""

import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DISTRIBUICAO = {"respondível": 12, "parafrase": 6, "ambigua": 6, "sem_evidencia": 6}
STATUS = {
    "respondível": {"respondido"},
    "parafrase": {"respondido"},
    "ambigua": {"esclarecimento", "recusa"},
    "sem_evidencia": {"sem_evidencia"},
}
INDICIOS_PESSOAIS = re.compile(
    r"\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b|\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"
    r"|\b\d{11}\b|\(?\b\d{2}\)?\s+\d{4,5}-\d{4}\b",
    re.IGNORECASE,
)


def exigir(condicao, mensagem):
    if not condicao:
        raise ValueError(mensagem)


def objeto_json(pares):
    objeto = dict(pares)
    exigir(len(objeto) == len(pares), "chave JSON duplicada")
    return objeto


def constante_invalida(valor):
    raise ValueError(f"constante JSON inválida: {valor}")


def ler_json(conteudo, local):
    try:
        return json.loads(
            conteudo, object_pairs_hook=objeto_json, parse_constant=constante_invalida
        )
    except ValueError as erro:
        raise ValueError(f"{local}: {erro}") from erro


def ler(registro, jsonl=False):
    conteudo = (ROOT / registro).read_text(encoding="utf-8")
    exigir(not INDICIOS_PESSOAIS.search(conteudo), f"{registro}: indício de dado pessoal")
    if jsonl:
        return [
            ler_json(linha, f"{registro}:{numero}")
            for numero, linha in enumerate(conteudo.splitlines(), 1)
        ]
    return ler_json(conteudo, registro)


def campos_texto(registro, campos, local):
    exigir(isinstance(registro, dict), f"{local}: objeto esperado")
    for campo in campos.split():
        valor = registro.get(campo)
        exigir(isinstance(valor, str) and valor.strip(), f"{local}: {campo} inválido")


def indexar(registros, chave, campos):
    exigir(isinstance(registros, list) and registros, f"{chave}: lista vazia ou inválida")
    indice = {}
    for numero, registro in enumerate(registros, 1):
        local = f"{chave}, registro {numero}"
        campos_texto(registro, f"{chave} {campos}", local)
        id_registro = registro[chave]
        exigir(re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", id_registro), f"{local}: ID inválido")
        exigir(id_registro not in indice, f"{local}: ID duplicado: {id_registro}")
        indice[id_registro] = registro
    return indice


def validar_url(url):
    partes = urlsplit(url)
    exigir(
        not re.search(r"[\s\\]", url)
        and partes.scheme in {"http", "https"}
        and partes.hostname
        and re.fullmatch(r"(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}", partes.hostname)
        and partes.username is None
        and partes.password is None
        and (partes.port is None or partes.port > 0),
        f"URL inválida: {url}",
    )


def validar_data(valor):
    exigir(date.fromisoformat(valor).isoformat() == valor, f"data inválida: {valor}")


def validar_base():
    fontes = indexar(
        ler("base/fontes.json"),
        "source_id",
        "titulo instituicao url tipo_documento data_publicacao data_acesso "
        "licenca_ou_status_juridico permissao_reproducao referencia observacoes",
    )
    for fonte in fontes.values():
        validar_url(fonte["url"])
        validar_data(fonte["data_acesso"])
        if fonte["data_publicacao"] != "não verificado":
            validar_data(fonte["data_publicacao"])
            exigir(fonte["data_publicacao"] <= fonte["data_acesso"], "publicação posterior ao acesso")

    chunks = indexar(
        ler("base/chunks.jsonl", jsonl=True),
        "chunk_id",
        "source_id titulo texto secao_artigo url_origem",
    )
    exigir(30 <= len(chunks) <= 60, "a base deve conter entre 30 e 60 chunks")
    for chunk_id, chunk in chunks.items():
        fonte = fontes.get(chunk["source_id"])
        exigir(fonte, f"{chunk_id}: fonte inexistente")
        validar_url(chunk["url_origem"])
        exigir(chunk["url_origem"] == fonte["url"], f"{chunk_id}: origem diverge da fonte")
        meta = chunk.get("metadados")
        campos_texto(meta, "idioma tipo_texto data_verificacao localizador", chunk_id)
        exigir(meta["localizador"] == chunk["secao_artigo"], f"{chunk_id}: seção divergente")
        exigir(meta["data_verificacao"] == fonte["data_acesso"], f"{chunk_id}: data divergente")
    exigir({c["source_id"] for c in chunks.values()} == fontes.keys(), "fonte sem chunks")
    return fontes, chunks


def validar_referencias(ids, indice, caso_id):
    exigir(isinstance(ids, list), f"{caso_id}: referências devem formar uma lista")
    exigir(
        all(isinstance(item, str) and item in indice for item in ids),
        f"{caso_id}: referência inexistente ou inválida",
    )
    exigir(len(ids) == len(set(ids)), f"{caso_id}: referência duplicada")
    return set(ids)


def validar_casos(fontes, chunks):
    casos = indexar(
        ler("avaliacao/casos_teste.jsonl", jsonl=True),
        "id",
        "pergunta categoria resposta_esperada status_esperado justificativa criterio_avaliacao",
    )
    contagens = Counter(c["categoria"] for c in casos.values())
    exigir(contagens.keys() == DISTRIBUICAO.keys(), "categorias do dataset inválidas")
    for categoria, minimo in DISTRIBUICAO.items():
        exigir(contagens[categoria] >= minimo, f"{categoria}: mínimo de {minimo} casos")
    perguntas = {" ".join(c["pergunta"].casefold().split()) for c in casos.values()}
    exigir(len(perguntas) == len(casos), "pergunta duplicada")

    for caso_id, caso in casos.items():
        status = caso["status_esperado"]
        resposta = caso["resposta_esperada"]
        exigir(status in STATUS[caso["categoria"]], f"{caso_id}: status incompatível")
        evidencia = validar_referencias(caso.get("chunk_ids_esperados"), chunks, caso_id)
        origem = validar_referencias(caso.get("source_ids_esperados"), fontes, caso_id)
        exigir(origem == {chunks[item]["source_id"] for item in evidencia}, f"{caso_id}: fontes divergentes")
        if status == "respondido":
            trechos = [chunks[item]["texto"] for item in caso["chunk_ids_esperados"]]
            exigir(evidencia and resposta == " ".join(trechos), f"{caso_id}: gabarito diverge da evidência")
        else:
            exigir(not evidencia and not origem, f"{caso_id}: referências inesperadas")
            if status == "esclarecimento":
                exigir(resposta.strip().endswith("?"), f"{caso_id}: falta pergunta de esclarecimento")
            else:
                exigir(resposta == "não consta", f"{caso_id}: resposta deve ser literalmente 'não consta'")
    ambiguos = {c["status_esperado"] for c in casos.values() if c["categoria"] == "ambigua"}
    exigir(ambiguos == STATUS["ambigua"], "inclua esclarecimentos e recusas entre os casos ambíguos")
    return casos


def main():
    try:
        fontes, chunks = validar_base()
        casos = validar_casos(fontes, chunks)
    except (OSError, ValueError) as erro:
        print(f"Falha de integridade: {erro}", file=sys.stderr)
        return 1
    print(f"Integridade OK — {len(fontes)} fontes, {len(chunks)} chunks e {len(casos)} casos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
