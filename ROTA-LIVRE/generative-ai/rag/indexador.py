import hashlib
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import BadZipFile, ZipFile

import faiss
import numpy as np

from rag.embeddings import DIM, LOCAL, MODEL, REVISION, ROOT
from scripts.validar_base import validar_base

INDEX = LOCAL / "indice.zip"


def corpus():
    fontes, chunks = validar_base()
    rows = list(chunks.values())
    payload = json.dumps([fontes, rows], sort_keys=True, ensure_ascii=False).encode()
    manifest = {
        "versao": 1, "sha256": hashlib.sha256(payload).hexdigest(),
        "modelo": MODEL, "revisao": REVISION, "dimensao": DIM,
        "vetores": [[row["chunk_id"], row["source_id"]] for row in rows],
    }
    return rows, manifest


def unitarios(vectors, n):
    matrix = np.ascontiguousarray(vectors, dtype=np.float32)
    if matrix.shape != (n, DIM) or not np.allclose(np.linalg.norm(matrix, axis=1), 1, atol=1e-5):
        raise ValueError("Vetores incompatíveis com o índice.")
    return matrix


def construir(encoder, destino=INDEX):
    rows, manifest = corpus()
    index = faiss.IndexFlatIP(DIM)
    index.add(unitarios(encoder.encode([row["texto"] for row in rows]), len(rows)))
    destino.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=destino.parent, delete=False) as file:
        temp = Path(file.name)
    try:
        with ZipFile(temp, "w") as archive:
            archive.writestr("manifesto.json", json.dumps(manifest))
            archive.writestr("indice.faiss", faiss.serialize_index(index).tobytes())
        os.replace(temp, destino)
    finally:
        temp.unlink(missing_ok=True)
    return len(rows)


def carregar(origem=INDEX):
    rows, manifest = corpus()
    try:
        with ZipFile(origem) as archive:
            if json.loads(archive.read("manifesto.json")) != manifest:
                raise ValueError("Índice desatualizado. Reconstrua com scripts.construir_indice.")
            index = faiss.deserialize_index(np.frombuffer(archive.read("indice.faiss"), dtype=np.uint8))
    except (OSError, BadZipFile, KeyError, RuntimeError, json.JSONDecodeError) as error:
        raise ValueError("Índice ausente ou inválido. Execute scripts.construir_indice.") from error
    if not isinstance(index, faiss.IndexFlatIP) or index.d != DIM or index.ntotal != len(rows):
        raise ValueError("Índice incompatível com o manifesto.")
    return index, rows
