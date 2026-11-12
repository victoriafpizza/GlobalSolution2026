# Base documental

[`fontes.json`](fontes.json) contém o catálogo de fontes. [`chunks.jsonl`](chunks.jsonl) contém um objeto JSON por linha, em UTF-8. Cada chunk tem ID estável, fonte, título, texto, dispositivo, URL consultada, idioma, tipo de texto, data de verificação e localizador.

Para auditar um trecho, consulte `source_id`, abra `url_origem` e procure `secao_artigo`. Use a [curadoria](../docs/03_base_documental.md) para conferir as decisões de seleção e reutilização. O corpus é um recorte temático da legislação federal. Condições de vias, dados da API de obstáculos e textos de normas técnicas ficam fora desse recorte.

O [validador offline](../scripts/validar_base.py) verifica esquema, IDs, tamanho do acervo, proveniência, formato de URLs, datas, campos jurídicos e referências cruzadas. A triagem automática procura padrões de CPF, e-mail e telefone. Nomes, endereços e outros dados em texto livre exigem revisão humana.
