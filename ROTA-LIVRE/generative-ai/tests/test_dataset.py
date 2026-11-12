import unittest
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.validar_base import DISTRIBUICAO, validar_base, validar_casos


class DatasetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fontes, cls.chunks = validar_base()
        cls.casos = validar_casos(cls.fontes, cls.chunks)

    def test_distribuicao(self):
        distribuicao = Counter(caso["categoria"] for caso in self.casos.values())
        for categoria, minimo in DISTRIBUICAO.items():
            with self.subTest(categoria=categoria):
                self.assertGreaterEqual(distribuicao[categoria], minimo)

    def test_perguntas_factuais_independentes(self):
        evidencias = [
            frozenset(caso["chunk_ids_esperados"])
            for caso in self.casos.values()
            if caso["status_esperado"] == "respondido"
        ]
        self.assertGreaterEqual(len(set(evidencias)), 18)

    def test_ausencia_de_evidencia_e_recusa(self):
        for caso in self.casos.values():
            if caso["status_esperado"] in {"sem_evidencia", "recusa"}:
                with self.subTest(caso=caso["id"]):
                    self.assertEqual(caso["resposta_esperada"], "não consta")
                    self.assertEqual(caso["chunk_ids_esperados"], [])
                    self.assertEqual(caso["source_ids_esperados"], [])


if __name__ == "__main__":
    unittest.main()
