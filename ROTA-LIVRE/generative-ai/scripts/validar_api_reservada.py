"""Valida casos reservados contra o backend em execução no loopback."""

import json
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]


def main():
    folder = ROOT / "avaliacao"
    cases = [json.loads(line) for line in
             (folder / "casos_reservados.jsonl").read_text(encoding="utf-8").splitlines()]
    rows = []
    with httpx.Client(base_url="http://127.0.0.1:8000", timeout=45, trust_env=False) as client:
        obstacles = client.get("/api/obstacles")
        obstacles.raise_for_status()
        assert obstacles.json()["total"] == len(obstacles.json()["obstaculos"]) == 2
        for mode in ("rag", "agente"):
            for case in cases:
                time.sleep(1.05)
                response = client.post("/api/ai/ask", json={"pergunta": case["pergunta"], "modo": mode})
                response.raise_for_status()
                result = response.json()
                ok = result["status"] == case["status"]
                if case["chunk"]:
                    ok = ok and case["chunk"] in [c["chunk_id"] for c in result["citacoes"]]
                elif case["status"] == "nao_consta":
                    ok = ok and result["resposta"] == "não consta" and not result["citacoes"]
                else:
                    ok = ok and "qual item" in result["resposta"]
                rows.append(dict(modo=mode, caso=case["id"], acerto=ok, resposta=result))
    for row in rows:
        print(row["modo"], row["caso"], row["acerto"])
    return 0 if all(row["acerto"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
