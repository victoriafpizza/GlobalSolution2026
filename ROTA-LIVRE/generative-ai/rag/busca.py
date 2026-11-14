import argparse
import json

from rag.embeddings import Embeddings
from rag.indexador import INDEX, carregar, unitarios


class Busca:
    def __init__(self, encoder=None, origem=INDEX):
        self.index, self.chunks = carregar(origem)
        self.encoder = encoder if encoder is not None else Embeddings()

    def lote(self, perguntas, k=3, limiar=None):
        if not perguntas or any(not isinstance(p, str) or not p.strip() for p in perguntas):
            raise ValueError("Informe perguntas não vazias.")
        if type(k) is not int or k < 1:
            raise ValueError("k deve ser inteiro positivo.")
        if limiar is not None and not -1 <= limiar <= 1:
            raise ValueError("Limiar fora de [-1, 1].")
        vectors = unitarios(self.encoder.encode([p.strip() for p in perguntas]), len(perguntas))
        scores, indexes = self.index.search(vectors, min(k, len(self.chunks)))
        return [
            [{**self.chunks[i], "score": float(score)} for score, i in zip(ss, ii)
             if limiar is None or score >= limiar]
            for ss, ii in zip(scores, indexes)
        ]

    def consultar(self, pergunta, k=3, limiar=None):
        return self.lote([pergunta], k, limiar)[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pergunta")
    parser.add_argument("-k", type=int, default=3)
    parser.add_argument("--limiar", type=float)
    args = parser.parse_args()
    try:
        print(json.dumps(Busca().consultar(args.pergunta, args.k, args.limiar), ensure_ascii=False))
    except (ValueError, OSError, RuntimeError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
