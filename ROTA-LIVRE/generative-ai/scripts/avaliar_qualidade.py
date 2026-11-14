"""Recalcula o placar histórico e aplica a revisão semântica dos casos."""

import csv
import hashlib
import json
from collections import Counter
from statistics import mean, quantiles

from llm.schemas import Resposta
from scripts.avaliar_recuperacao import PASTA, ler_casos
from scripts.validar_base import validar_base

STATUS = dict(respondido="respondido", esclarecimento="esclarecimento_necessario",
              recusa="nao_consta", sem_evidencia="nao_consta")
MODOS = ("baseline", "rag", "agente")
# Julgamentos após leitura das respostas, dos critérios e dos dispositivos.
# O SHA-256 fixa a revisão às saídas efetivamente examinadas.
REVISAO = {
    ("baseline", "qa-001"): ("parcialmente_correta", "Descreve inclusão, mas restringe o conceito ao urbano e omite a dispensa de adaptação ou projeto específico."),
    ("baseline", "qa-003"): ("parcialmente_correta", "Confirma saídas acessíveis, mas omite a referência normativa e acrescenta um desvio sobre esporte."),
    ("baseline", "qa-004"): ("incorreta", "Repete a pergunta e não lista os seis componentes."),
    ("baseline", "qa-007"): ("alucinacao_factual", "Atribui à LBI garantias sobre posição, função e direção sem suporte. O trecho lbi-07 trata de prioridade e segurança no embarque e desembarque."),
    ("baseline", "qa-014"): ("incorreta", "Repete a pergunta e não confirma o acesso livre de barreiras."),
    ("rag", "qa-015"): ("citacao_nao_pertinente", "pnmu-10 trata de municípios sem transporte público, e não da prioridade geral dos modos não motorizados em pnmu-05."),
}
REVISAO[("agente", "qa-015")] = ("citacao_nao_pertinente", "pnmu-08 trata dos públicos do plano e não da prioridade modal prevista em pnmu-05.")
for modo in ("rag", "agente"):
    REVISAO.update({
        (modo, "qa-001"): ("citacao_nao_pertinente", "lbi-10 trata de aplicação do desenho universal e adaptação. A definição solicitada está em lbi-01."),
        (modo, "qa-004"): ("citacao_nao_pertinente", "lbi-07 trata de prioridade e segurança. lbi-04 lista os seis componentes do transporte."),
        (modo, "qa-017"): ("citacao_nao_pertinente", "pnmu-01 descreve o objetivo geral da política. pnmu-07 enumera os instrumentos de participação."),
    })


def julgar(modo, caso, resposta, chunks):
    esperado = STATUS[caso["status_esperado"]]
    status, texto = resposta.status, resposta.resposta
    if status == "nao_consta":
        ok = esperado == status and texto == "não consta" and not resposta.citacoes
        return ("recusa_correta", "Recusa literal e sem citação conforme o gabarito.", False) if ok else (
            "recusa_indevida", "O caso pede resposta factual ou esclarecimento.", False)
    if status == "esclarecimento_necessario":
        if esperado == status and texto.endswith("?") and not resposta.citacoes:
            if caso["id"] in {"qa-021", "qa-022"}:
                return "parcialmente_correta", "Pede esclarecimento genérico e omite o item percentual ou o documento e contexto requeridos.", False
            return "esclarecimento_correto", "Solicita contexto do local, situação ou requisito sem presumir fatos.", False
        return "erro_ambiguidade", "Esclarecimento incompatível com o contrato do caso.", False
    if any(c.chunk_id not in chunks for c in resposta.citacoes):
        return "citacao_inexistente", "ID de citação ausente no corpus.", False
    if (modo, caso["id"]) in REVISAO:
        return (*REVISAO[modo, caso["id"]], False)
    ids = {c.chunk_id for c in resposta.citacoes}
    if esperado == "respondido" and texto == caso["resposta_esperada"]:
        if ids == set(caso["chunk_ids_esperados"]):
            return "correta_fundamentada", "O texto satisfaz o critério e a citação corresponde ao dispositivo que o sustenta.", False
        if not ids:
            return "correta_sem_evidencia", "O texto corresponde ao gabarito e não apresenta citação.", False
    return "revisao_pendente", "A pertinência ou o suporte da resposta requer revisão humana.", True


def auditar(historico, casos, chunks, hash_historico):
    if set(historico["modos"]) != set(MODOS):
        raise ValueError("Modos históricos incompatíveis.")
    rows = []
    ids = [c["id"] for c in casos]
    if len(ids) != 30 or len(set(ids)) != 30:
        raise ValueError("Esperados 30 IDs únicos.")
    eventos = set()
    for modo in MODOS:
        entradas = historico["modos"][modo]["casos"]
        if [item["id"] for item in entradas] != ids:
            raise ValueError(f"Casos ausentes, duplicados ou fora de ordem em {modo}.")
        for caso, item in zip(casos, entradas, strict=True):
            raw, evento = item["resposta"], item["evento"]
            esperado = STATUS[caso["status_esperado"]]
            if (raw["pergunta"] != caso["pergunta"] or item["esperado"] != esperado
                    or evento["id"] in eventos or evento["modo"] != modo):
                raise ValueError("Identidade da execução divergente.")
            eventos.add(evento["id"])
            resposta = Resposta.model_validate(raw)
            resultado, justificativa, revisao = julgar(modo, caso, resposta, chunks)
            citacoes = resposta.citacoes
            metadados_validos = bool(citacoes) and all(
                c.chunk_id in chunks and c.chunk_id in evento["chunks"]
                and (c.source_id, c.titulo, c.url) == tuple(
                    chunks[c.chunk_id][key] for key in ("source_id", "titulo", "url_origem"))
                for c in citacoes
            )
            suporte = metadados_validos and any(raw["resposta"] == chunks[c.chunk_id]["texto"] for c in citacoes)
            rows.append(dict(id=caso["id"], modo=modo, categoria=caso["categoria"],
                             pergunta=caso["pergunta"], resposta=raw, gabarito=caso,
                             resultado=resultado, justificativa=justificativa,
                             revisao_humana=revisao, evento=evento,
                             historico_sha256=hash_historico,
                             status_correto=resposta.status == esperado,
                             texto_exato=resposta.resposta == caso["resposta_esperada"],
                             citacao_gabarito=bool({c.chunk_id for c in citacoes} & set(caso["chunk_ids_esperados"])),
                             citacao_valida=metadados_validos, suporte_textual=suporte,
                             json_final_valido=True))
    return rows


def taxa(n, d):
    return dict(n=n, denominador=d, percentual=100*n/d if d else None)


def metricas(rows):
    n = len(rows)
    counts = Counter(r["resultado"] for r in rows)
    facts = [r for r in rows if r["gabarito"]["status_esperado"] == "respondido"]
    answered = [r for r in rows if r["resposta"]["status"] == "respondido"]
    cited = [r for r in answered if r["resposta"]["citacoes"]]
    refused = [r for r in rows if r["resposta"]["status"] == "nao_consta"]
    expected_refusals = sum(r["gabarito"]["status_esperado"] in {"recusa", "sem_evidencia"} for r in rows)
    inferred = [r for r in rows if r["evento"]["inferencias"]]
    ts = [r["evento"]["segundos"] for r in rows]
    return dict(
        status=taxa(sum(r["status_correto"] for r in rows), n),
        acerto=taxa(sum(counts[k] for k in ("correta_fundamentada", "correta_sem_evidencia",
                                          "recusa_correta", "esclarecimento_correto")), n),
        factual=taxa(counts["correta_fundamentada"] + counts["correta_sem_evidencia"], len(facts)),
        factual_texto_exato=taxa(sum(r["texto_exato"] for r in facts), len(facts)),
        citacao_gabarito=taxa(sum(r["citacao_gabarito"] for r in facts), len(facts)),
        citacao_valida=taxa(sum(r["citacao_valida"] for r in cited), len(cited)),
        citacao_pertinente=taxa(sum(r["resultado"] == "correta_fundamentada" for r in cited), len(cited)),
        suporte_textual=taxa(sum(r["suporte_textual"] for r in rows), n),
        fundamentada=taxa(counts["correta_fundamentada"], n),
        alucinacao=taxa(counts["alucinacao_factual"], len(answered)),
        resposta_sem_evidencia=taxa(sum(not r["suporte_textual"] for r in answered), len(answered)),
        recusa_adequada=taxa(counts["recusa_correta"], expected_refusals),
        recusa_indevida=taxa(counts["recusa_indevida"], len(refused)),
        json_final=taxa(sum(r["json_final_valido"] for r in rows), n),
        json_modelo=taxa(sum(r["evento"]["json_modelo_valido"] is True for r in inferred), len(inferred)),
        revisao_pendente=taxa(sum(r["revisao_humana"] for r in rows), n),
        latencia_s=dict(n=n, media=mean(ts), p50=quantiles(ts, n=100, method="inclusive")[49],
                        p95=quantiles(ts, n=100, method="inclusive")[94]),
        distribuicao=dict(counts),
    )


def main():
    payload = (PASTA / "comparacao_configuracoes.json").read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != "7ef99ccc236aad8816f1a1058b77595642073a84d947dd7eacb71ff4932ff075":
        raise ValueError("Novo histórico exige revisão semântica antes da publicação do placar.")
    historico = json.loads(payload)
    _, chunks = validar_base()
    rows = auditar(historico, ler_casos(), chunks, digest)
    report = {}
    with (PASTA / "placar_configuracoes.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(("modo", "categoria", "metrica", "n", "denominador", "percentual"))
        for modo in MODOS:
            selected = [r for r in rows if r["modo"] == modo]
            grupos = {"total": selected, **{
                cat: [r for r in selected if r["categoria"] == cat]
                for cat in sorted({r["categoria"] for r in selected})}}
            report[modo] = {grupo: metricas(items) for grupo, items in grupos.items()}
            for grupo, values in report[modo].items():
                for name, value in values.items():
                    if "percentual" in value:
                        writer.writerow((modo, grupo, name, value["n"], value["denominador"], value["percentual"]))
    (PASTA / "auditoria_respostas.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    (PASTA / "metricas_qualidade.json").write_text(
        json.dumps(dict(historico_sha256=digest, modelo=historico["modelo"],
                        revisao=historico["revisao"], modos=report), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(f"{len(rows)} respostas auditadas. SHA-256: {digest}")


if __name__ == "__main__":
    main()
