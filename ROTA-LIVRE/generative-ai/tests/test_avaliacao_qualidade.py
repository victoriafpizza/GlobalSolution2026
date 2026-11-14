import hashlib
import json
import unittest

from scripts.avaliar_qualidade import MODOS, auditar, metricas, taxa
from scripts.avaliar_recuperacao import PASTA, ler_casos
from scripts.validar_base import validar_base


class AuditoriaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        payload = (PASTA / "comparacao_configuracoes.json").read_bytes()
        cls.historico = json.loads(payload)
        cls.casos = ler_casos()
        _, cls.chunks = validar_base()
        cls.rows = auditar(cls.historico, cls.casos, cls.chunks, hashlib.sha256(payload).hexdigest())

    def test_mesmos_casos_e_eventos_distintos(self):
        self.assertEqual(len(self.rows), 90)
        self.assertEqual(len({r["evento"]["id"] for r in self.rows}), 90)
        with self.assertRaises(ValueError):
            auditar(self.historico, self.casos[::-1], self.chunks, "teste")

    def test_placar_recalculado(self):
        for modo, acertos in zip(MODOS, (8, 19, 19)):
            with self.subTest(modo=modo):
                scores = metricas([r for r in self.rows if r["modo"] == modo])
                self.assertEqual(scores["acerto"]["n"], acertos)
                self.assertEqual(scores["recusa_adequada"], taxa(8, 8))
                self.assertEqual(scores["json_final"], taxa(30, 30))

    def test_proveniencia_nao_basta_e_alucinacao_tem_denominador(self):
        exemplos = {(r["modo"], r["id"]): r for r in self.rows}
        self.assertTrue(exemplos["agente", "qa-001"]["suporte_textual"])
        self.assertEqual(exemplos["agente", "qa-001"]["resultado"], "citacao_nao_pertinente")
        self.assertEqual(exemplos["baseline", "qa-007"]["resultado"], "alucinacao_factual")
        self.assertEqual(taxa(0, 0)["percentual"], None)
