import argparse
import json
from statistics import mean

from llm.cliente_local import ClienteLocal, MODELO, REVISAO
from llm.gerador import Gerador, limiar_local
from rag.busca import Busca
from rag.embeddings import LOCAL
from scripts.avaliar_recuperacao import PASTA, ler_casos

STATUS = {"respondido": "respondido", "esclarecimento": "esclarecimento_necessario",
          "recusa": "nao_consta", "sem_evidencia": "nao_consta"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--modos", nargs="+", choices=("baseline", "rag", "agente"),
                        default=["baseline", "rag", "agente"])
    args = parser.parse_args()
    casos = ler_casos()
    busca = Busca() if any(m != "baseline" for m in args.modos) else None
    engine = Gerador(ClienteLocal(), busca, limiar_local() if busca else None,
                     LOCAL / "consultas.jsonl")
    report = {"modelo": MODELO, "revisao": REVISAO, "modos": {}}
    for modo in args.modos:
        rows = []
        for caso in casos:
            answer, evento = engine.executar(caso["pergunta"], modo)
            ids = {c.chunk_id for c in answer.citacoes}
            esperado = STATUS[caso["status_esperado"]]
            rows.append(dict(id=caso["id"], esperado=esperado, resposta=answer.model_dump(),
                             json_saida_valido=True,
                             status_correto=answer.status == esperado,
                             texto_exato=answer.resposta == caso["resposta_esperada"],
                             citacao_gabarito=bool(ids & set(caso["chunk_ids_esperados"])),
                             fundamentada=answer.status == "respondido" and bool(ids),
                             recusa_adequada=esperado == answer.status == "nao_consta",
                             evento=evento))
        factual = [r for r in rows if r["esperado"] == "respondido"]
        recusas = [r for r in rows if r["esperado"] == "nao_consta"]
        inferidas = [r for r in rows if r["evento"]["inferencias"]]
        report["modos"][modo] = {
            "n": len(rows), "acuracia_status": mean(r["status_correto"] for r in rows),
            "acerto_textual_factual": mean(r["texto_exato"] for r in factual),
            "citacao_gabarito_factual": mean(r["citacao_gabarito"] for r in factual),
            "fundamentadas": sum(r["fundamentada"] for r in rows),
            "recusa_adequada": mean(r["recusa_adequada"] for r in recusas),
            "latencia_media_s": mean(r["evento"]["segundos"] for r in rows),
            "inferencias": len(inferidas),
            "json_modelo_validos": sum(r["evento"]["json_modelo_valido"] for r in inferidas),
            "erros": sum(r["evento"]["erro"] is not None for r in rows),
            "casos": rows,
        }
        print(modo, {k: v for k, v in report["modos"][modo].items() if k != "casos"}, flush=True)
    (PASTA / "comparacao_configuracoes.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
