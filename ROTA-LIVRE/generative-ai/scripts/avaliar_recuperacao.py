import csv
import json
from statistics import mean, median

from rag.busca import Busca
from rag.embeddings import DIM, MODEL, REVISION, ROOT

PASTA = ROOT / "avaliacao"
FACTUAIS = ("respondível", "parafrase")


def ler_casos():
    return [json.loads(line) for line in (PASTA / "casos_teste.jsonl").read_text(encoding="utf-8").splitlines()]


def ranking(rows, k):
    fractions = []
    for row in rows:
        expected = set(row["esperados"])
        retrieved = {hit["chunk_id"] for hit in row["top"][:k]}
        fractions.append(len(expected & retrieved) / len(expected))
    return {"recall": mean(fractions), "hit": mean(f > 0 for f in fractions)}


def confusao(positivos, negativos, limiar):
    vp = sum(s >= limiar for s in positivos)
    fp = sum(s >= limiar for s in negativos)
    fn, vn = len(positivos) - vp, len(negativos) - fp
    return dict(limiar=limiar, vp=vp, fp=fp, fn=fn, vn=vn,
                rejeicao=(fn + vn) / (len(positivos) + len(negativos)),
                erro_balanceado=(fp / len(negativos) + fn / len(positivos)) / 2)


def main():
    casos = ler_casos()
    busca = Busca()
    resultados = busca.lote([c["pergunta"] for c in casos])
    rows = [
        dict(id=c["id"], pergunta=c["pergunta"], categoria=c["categoria"],
             esperados=c["chunk_ids_esperados"], top=[
                 {key: hit[key] for key in ("chunk_id", "source_id", "score", "secao_artigo")}
                 for hit in hits])
        for c, hits in zip(casos, resultados, strict=True)
    ]
    groups = {cat: [r for r in rows if r["categoria"] == cat] for cat in {r["categoria"] for r in rows}}
    positive = [r for cat in FACTUAIS for r in groups[cat]]
    metrics = {
        cat: {f"k{k}": ranking(items, k) for k in (1, 3)}
        for cat, items in {"factual": positive, **{cat: groups[cat] for cat in FACTUAIS}}.items()
    }
    def scores(items):
        return [r["top"][0]["score"] for r in items]

    pos, neg = scores(positive), scores(groups["sem_evidencia"])
    vals = sorted(set(pos + neg))
    candidates = sorted({-1, 1, *((a + b) / 2 for a, b in zip(vals, vals[1:]))})
    table = [confusao(pos, neg, t) for t in candidates]
    chosen = min(table, key=lambda r: (r["erro_balanceado"], r["fp"], -r["limiar"]))
    report = dict(modelo=MODEL, revisao=REVISION, dimensao=DIM, chunks=len(busca.chunks),
                  ranking=metrics, escolhido=chosen, calibracao="exploratória",
                  distribuicao={cat: dict(n=len(items), min=min(scores(items)),
                                         mediana=median(scores(items)), max=max(scores(items)),
                                         aceitos=sum(s >= chosen["limiar"] for s in scores(items)))
                               for cat, items in sorted(groups.items())}, casos=rows)
    (PASTA / "resultados_recuperacao.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (PASTA / "metricas_recuperacao.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(chosen))
        writer.writeheader()
        writer.writerows(table)
    print(json.dumps(dict(ranking=metrics, escolhido=chosen), ensure_ascii=False))


if __name__ == "__main__":
    main()
