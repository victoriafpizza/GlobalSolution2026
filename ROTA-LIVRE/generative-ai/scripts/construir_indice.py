import argparse
import logging

from rag.embeddings import Embeddings, MODEL, REVISION
from rag.indexador import INDEX, construir


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baixar-modelo", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    try:
        total = construir(Embeddings(args.baixar_modelo))
    except (ValueError, OSError, RuntimeError) as error:
        parser.exit(1, f"{error}\n")
    logging.info("%d chunks, %s@%s, índice %s", total, MODEL, REVISION, INDEX)


if __name__ == "__main__":
    main()
