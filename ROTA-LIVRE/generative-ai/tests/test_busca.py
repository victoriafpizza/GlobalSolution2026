import tempfile
import unittest
from pathlib import Path

import numpy as np

from rag.busca import Busca
from rag.embeddings import DIM
from rag.indexador import carregar, construir
from scripts.avaliar_recuperacao import confusao, ranking


class TesteBusca(unittest.TestCase):
    def test_indice_e_reconstrucao(self):
        class Encoder:
            def encode(self, texts):
                vectors = np.zeros((len(texts), DIM), dtype=np.float32)
                vectors[:, 0] = 1
                return vectors

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "indice.zip"
            with self.assertRaises(ValueError):
                carregar(path)
            for _ in range(2):
                self.assertEqual(construir(Encoder(), path), 30)
            hit = Busca(Encoder(), path).consultar("rampa", k=1)[0]
            self.assertTrue(hit["source_id"] and hit["metadados"] and hit["url_origem"])

    def test_metrica_multiplos_chunks(self):
        rows = [{"esperados": ["a", "b"], "top": [{"chunk_id": "a"}]}]
        self.assertEqual(ranking(rows, 1), {"recall": 0.5, "hit": 1})
        self.assertEqual(confusao([0.8, 0.1], [0.7, 0.2], 0.5)["fp"], 1)
