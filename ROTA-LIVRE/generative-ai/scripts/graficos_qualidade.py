"""Gera a figura estática a partir do JSON auditado."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PASTA = Path(__file__).resolve().parents[1] / "avaliacao"


def main():
    data = json.loads((PASTA / "metricas_qualidade.json").read_text(encoding="utf-8"))
    rows = [data["modos"][m]["total"] for m in ("baseline", "rag", "agente")]
    labels = ["Baseline", "RAG", "Agente"]
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
    for ax, key, title in (
        (axes[0, 0], "acerto", "Acertos integrais"),
        (axes[0, 1], "recusa_adequada", "Recusas adequadas"),
    ):
        metrics = [r[key] for r in rows]
        bars = ax.bar(labels, [m["percentual"] for m in metrics], color="#246e80")
        ax.bar_label(bars, [f"{m['n']}/{m['denominador']}" for m in metrics], padding=4)
        ax.set_ylim(0, 115)
        ax.set_ylabel("%")
        ax.set_title(title)
    ax = axes[1, 0]
    bottom = [0, 0, 0]
    for key, label, color in (
        ("recusa_indevida", "Recusa indevida", "#ad5e2b"),
        ("citacao_nao_pertinente", "Citação impertinente", "#825b98"),
        ("parcialmente_correta", "Parcial", "#d0a53a"),
        ("incorreta", "Incorreta", "#ad3d55"),
        ("alucinacao_factual", "Alucinação factual", "#3d4b73"),
    ):
        values = [r["distribuicao"].get(key, 0) for r in rows]
        ax.bar(labels, values, bottom=bottom, label=label, color=color)
        bottom = [a+b for a, b in zip(bottom, values)]
    ax.set_title("Distribuição dos erros por caso")
    ax.set_ylabel("Casos")
    ax.legend(fontsize=8)
    ax = axes[1, 1]
    for offset, key, label in ((-0.24, "media", "Média"), (0, "p50", "p50"), (0.24, "p95", "p95")):
        ax.bar([i+offset for i in range(3)], [r["latencia_s"][key] for r in rows],
               width=0.22, label=label)
    ax.set_xticks(range(3), labels)
    ax.set_title("Latência registrada")
    ax.set_ylabel("Segundos")
    ax.legend()
    fig.savefig(PASTA / "graficos_qualidade.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
