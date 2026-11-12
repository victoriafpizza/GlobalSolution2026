"""Regressão do robô, do log operacional e dos endpoints locais."""

import hashlib
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from contextlib import contextmanager
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import ProxyHandler, build_opener

import uvicorn
from fastapi import FastAPI

from config import RAIZ
from integracao_backend.exemplo_fastapi import criar_roteador
from src.gerenciador_logs import LOGGER, configurar_logs
from src.integracao import RelatorioIndisponivel, ler_ultimo_relatorio


ENTRADA = RAIZ / "dados" / "obstaculos_exemplo.json"


@contextmanager
def servidor_local(app):
    servidor = uvicorn.Server(uvicorn.Config(app, log_level="error", timeout_graceful_shutdown=2))
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        porta = listener.getsockname()[1]
        thread = threading.Thread(target=servidor.run, kwargs={"sockets": [listener]}, daemon=True)
        thread.start()
        try:
            limite = time.monotonic() + 5
            while not servidor.started:
                if not thread.is_alive() or time.monotonic() >= limite:
                    raise RuntimeError("O servidor FastAPI local não iniciou.")
                time.sleep(0.01)
            yield f"http://127.0.0.1:{porta}"
        finally:
            servidor.should_exit = True
            thread.join(timeout=5)


def consultar(base, endpoint):
    cliente = build_opener(ProxyHandler({}))
    try:
        resposta = cliente.open(base + endpoint, timeout=3)
    except HTTPError as erro:
        resposta = erro
    with resposta:
        return resposta.status, json.load(resposta)


class RegressaoEtapa3(unittest.TestCase):
    def setUp(self):
        self.temporario = tempfile.TemporaryDirectory(prefix="rota-regressao-")
        self.addCleanup(self.temporario.cleanup)
        self.pasta = Path(self.temporario.name)
        self.saida = self.pasta / "saida"
        self.log = self.pasta / "logs" / "rota_livre.log"

    def executar(self, *args):
        # Usa a CLI e a lógica do robô com destinos isolados para os artefatos de teste.
        entrada = (
            "import sys; from pathlib import Path; import main; "
            "main.PASTA_SAIDA = Path(sys.argv.pop(1)); "
            "main.PASTA_LOGS = Path(sys.argv.pop(1)); raise SystemExit(main.main())"
        )
        env = {chave: valor for chave, valor in os.environ.items() if not chave.startswith("ROTA_")}
        env.update(PYTHONIOENCODING="utf-8", NO_PROXY="127.0.0.1")
        return subprocess.run(
            [sys.executable, "-B", "-c", entrada, str(self.saida), str(self.log.parent), *map(str, args)],
            cwd=RAIZ, env=env, capture_output=True, encoding="utf-8", timeout=15,
        )

    def gerar_relatorio(self):
        original = hashlib.sha256(ENTRADA.read_bytes()).digest()
        execucao = self.executar("--arquivo", ENTRADA)
        self.assertEqual(execucao.returncode, 0, execucao.stderr)
        self.assertEqual(hashlib.sha256(ENTRADA.read_bytes()).digest(), original)
        arquivo, = self.saida.glob("resultado_*.json")
        return json.loads(arquivo.read_bytes())

    def escrever_lote(self, registros):
        arquivo = self.pasta / "lote.json"
        arquivo.write_text(json.dumps(registros), encoding="utf-8")
        return arquivo

    def test_lote_prioridades_invalidos_duplicidade_e_logs(self):
        relatorio = self.gerar_relatorio()
        resumo = relatorio["resumo"]
        self.assertEqual(resumo, dict(total=6, validos=4, invalidos=1, duplicados=1))
        posicoes = [
            item["posicao"] for categoria in ("validos", "invalidos", "duplicados")
            for item in relatorio[categoria]
        ]
        self.assertEqual(sorted(posicoes), list(range(1, 7)))
        self.assertEqual(
            [item["prioridade"] for item in relatorio["validos"]], ["alta", "alta", "media", "baixa"],
        )
        self.assertTrue(any("latitude" in motivo for motivo in relatorio["invalidos"][0]["motivos"]))
        self.assertEqual(relatorio["duplicados"][0]["posicao_original"], 1)
        self.assertEqual(relatorio["situacao"], "sucesso_parcial")
        log = self.log.read_text(encoding="utf-8")
        self.assertRegex(log, r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ")
        self.assertIn(relatorio["execucao_id"], log)
        for evento in (
            "Execução iniciada.", "Execução finalizada.", "Registro inválido", "Registro duplicado",
            "origem=arquivo", "situacao=sucesso_parcial",
        ):
            self.assertIn(evento, log)
        for campo, total in resumo.items():
            self.assertIn(f"{campo}={total}", log)

    def test_json_malformado(self):
        arquivo = self.pasta / "malformado.json"
        conteudo = b'[{"id":101,}]'
        arquivo.write_bytes(conteudo)
        execucao = self.executar("--arquivo", arquivo)
        self.assertEqual(execucao.returncode, 1)
        self.assertIn("JSON malformado", execucao.stderr)
        self.assertNotIn("Traceback", execucao.stderr)
        self.assertEqual(arquivo.read_bytes(), conteudo)
        self.assertFalse(list(self.saida.glob("resultado_*.json")))
        self.assertIn("situacao=falha", self.log.read_text(encoding="utf-8"))

    def test_latitude_invalida_no_meio_do_lote(self):
        modelo = json.loads(ENTRADA.read_bytes())[0]
        arquivo = self.escrever_lote([
            dict(modelo, id=201), dict(modelo, id=202, latitude=91), dict(modelo, id=203),
        ])
        execucao = self.executar("--arquivo", arquivo)
        self.assertEqual(execucao.returncode, 0, execucao.stderr)
        relatorio, = self.saida.glob("resultado_*.json")
        dados = json.loads(relatorio.read_bytes())
        self.assertEqual([item["registro"]["id"] for item in dados["validos"]], [201, 203])
        invalido, = dados["invalidos"]
        self.assertEqual(invalido["registro"]["id"], 202)
        self.assertEqual(invalido["motivos"], ["latitude deve ser um número entre -90 e 90."])

    def test_ids_equivalentes_preservam_a_entrada(self):
        modelo = json.loads(ENTRADA.read_bytes())[0]
        arquivo = self.escrever_lote([dict(modelo, id=101), dict(modelo, id=" 101 ")])
        entrada = arquivo.read_bytes()
        execucao = self.executar("--arquivo", arquivo)
        self.assertEqual(execucao.returncode, 0, execucao.stderr)
        relatorio, = self.saida.glob("resultado_*.json")
        dados = json.loads(relatorio.read_bytes())
        primeiro, = dados["validos"]
        duplicado, = dados["duplicados"]
        self.assertEqual(primeiro["registro"]["id"], 101)
        self.assertEqual(duplicado["registro"]["id"], " 101 ")
        self.assertEqual(duplicado["posicao_original"], primeiro["posicao"])
        self.assertEqual(duplicado["motivo"], "Mesmo ID de um registro válido anterior.")
        self.assertEqual(arquivo.read_bytes(), entrada)

    def test_execucoes_limpas_tem_ids_distintos_e_sucesso(self):
        arquivo = self.escrever_lote(json.loads(ENTRADA.read_bytes())[:1])
        for _ in range(2):
            execucao = self.executar("--arquivo", arquivo)
            self.assertEqual(execucao.returncode, 0, execucao.stderr)
        dados = [json.loads(p.read_bytes()) for p in self.saida.glob("resultado_*.json")]
        self.assertEqual(len({d["execucao_id"] for d in dados}), 2)
        self.assertTrue(all(d["situacao"] == "sucesso" for d in dados))
        self.assertEqual(self.log.read_text(encoding="utf-8").count("erros=0 situacao=sucesso"), 2)

    def test_rotacao_mantem_tres_copias(self):
        with configurar_logs(self.log.parent, "teste-rotacao"):
            arquivo, console = LOGGER.handlers
            arquivo.maxBytes = 250
            console.setLevel("CRITICAL")
            for indice in range(20):
                LOGGER.info("Evento de teste da rotação %d", indice)
        self.assertEqual(
            sorted(p.name for p in self.log.parent.iterdir()),
            ["rota_livre.log", "rota_livre.log.1", "rota_livre.log.2", "rota_livre.log.3"],
        )

    def test_api_indisponivel(self):
        with socket.socket() as reservada:
            reservada.bind(("127.0.0.1", 0))
            porta = reservada.getsockname()[1]
            execucao = self.executar(
                "--api-url", f"http://127.0.0.1:{porta}/obstaculos",
                "--timeout", "0.3", "--tentativas", "2", "--intervalo", "0",
            )
        self.assertEqual(execucao.returncode, 1)
        self.assertEqual(execucao.stderr.count("WARNING API, tentativa"), 2)
        self.assertIn("Não foi possível obter uma lista de obstáculos da API.", execucao.stderr)
        self.assertNotIn("Traceback", execucao.stderr)
        self.assertFalse(list(self.saida.glob("resultado_*.json")))
        log = self.log.read_text(encoding="utf-8")
        self.assertIn(" | ERROR | ", log)
        self.assertIn("erros=1 situacao=falha", log)

    def test_leitor_e_endpoints_com_sucesso_e_falha(self):
        obstaculos, resumo = "/rpa/obstaculos-processados", "/rpa/resumo"
        app = FastAPI()
        app.include_router(criar_roteador(self.saida))
        with servidor_local(app) as base:
            for endpoint in (obstaculos, resumo):
                self.assertEqual(consultar(base, endpoint), (404, {
                    "detail": "Nenhum relatório de triagem disponível.",
                }))
            self.saida.mkdir()
            quebrado = self.saida / "resultado_corrompido.json"
            quebrado.write_text('{"execucao_id":', encoding="utf-8")
            with self.assertRaises(RelatorioIndisponivel):
                ler_ultimo_relatorio(self.saida)
            for endpoint in (obstaculos, resumo):
                self.assertEqual(consultar(base, endpoint), (503, {
                    "detail": "Nenhum relatório de triagem válido está disponível.",
                }))
            quebrado.unlink()
            relatorio = self.gerar_relatorio()
            quebrado.write_text('{"execucao_id":', encoding="utf-8")
            (self.saida / "resultado_incompleto.json").write_text('{"origem":"api"}', encoding="utf-8")
            dados = ler_ultimo_relatorio(self.saida)
            self.assertEqual(consultar(base, obstaculos), (200, dados))
            self.assertEqual(consultar(base, resumo), (200, {
                chave: valor for chave, valor in dados.items() if chave != "obstaculos"
            }))
            self.assertEqual(dados["execucao_id"], relatorio["execucao_id"])
            self.assertIn(dados["execucao_id"], self.log.read_text(encoding="utf-8"))
            self.assertEqual(dados["resumo"], relatorio["resumo"])
            self.assertEqual(dados["por_prioridade"], dict(alta=2, media=1, baixa=1))
            self.assertTrue(all("descricao" not in item for item in dados["obstaculos"]))
