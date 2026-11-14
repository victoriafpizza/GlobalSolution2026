from scripts.validar_base import validar_base


class Ferramentas:
    def __init__(self, busca, evento, limite=8):
        self.busca = busca
        self.fontes, self.chunks = validar_base()
        self.evento = evento
        self.limite = limite

    def registrar(self, ferramenta):
        if len(self.evento["ferramentas"]) >= self.limite:
            raise RuntimeError("Limite de ferramentas")
        self.evento["ferramentas"].append(ferramenta)

    def buscar_documentos(self, pergunta, top_k, limiar):
        self.registrar("buscar_documentos")
        return self.busca.consultar(pergunta, top_k, limiar)

    def obter_chunk(self, chunk_id):
        self.registrar("obter_chunk")
        return self.chunks.get(chunk_id)

    def verificar_fonte(self, source_id):
        self.registrar("verificar_fonte")
        return self.fontes.get(source_id)

    def validar_evidencias(self, candidato):
        self.registrar("validar_evidencias")
        chunk = self.obter_chunk(candidato["chunk_id"])
        fonte = self.verificar_fonte(candidato["source_id"])
        return bool(chunk and fonte and chunk["source_id"] == fonte["source_id"]
                    and chunk["url_origem"] == fonte["url"]
                    and chunk["texto"] == candidato["texto"])
