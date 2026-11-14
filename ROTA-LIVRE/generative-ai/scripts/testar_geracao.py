import argparse

from llm.cliente_local import ClienteLocal
from llm.gerador import Gerador, limiar_local
from rag.busca import Busca
from rag.embeddings import LOCAL


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pergunta")
    parser.add_argument("--modo", choices=("baseline", "rag", "agente"), default="rag")
    args = parser.parse_args()
    modo = args.modo
    engine = Gerador(ClienteLocal(), None if modo == "baseline" else Busca(),
                     None if modo == "baseline" else limiar_local(), LOCAL / "consultas.jsonl")
    answer, _ = engine.executar(args.pergunta, modo)
    print(answer.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
