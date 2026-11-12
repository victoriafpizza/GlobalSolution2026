# ROTA LIVRE · Generative AI for Engineering

Entrega das etapas 1, 2 e 3 da Global Solution FIAP 2026.2. A pasta fica dentro de ROTA-LIVRE, ao lado do frontend e do backend, para reunir os arquivos da disciplina no projeto ao qual pertencem.

| Etapa | Entrega |
| --- | --- |
| 1 | [Problema, tarefa e critérios de aceite](docs/01_problema_tarefa.md) |
| 2 | [Metodologia e 30 casos com gabarito](avaliacao/README.md) |
| 3 | [Curadoria e proveniência](docs/03_base_documental.md) e [base documental](base/README.md) |

Na pasta deste README, execute com Python 3.10 ou superior. A validação funciona offline com a biblioteca padrão.

```sh
python -B scripts/validar_base.py
python -B -m unittest discover -s tests -v
```

A entrega inclui o contrato do assistente, a base e os testes de integridade. A busca RAG, a geração com LLM e a avaliação de modelos são etapas futuras.

## Próximos passos

1. Indexar apenas os chunks, preservando os IDs, dispositivos e URLs. Comparar busca lexical e semântica usando as evidências esperadas e medir Recall@k.
2. Executar um LLM local com a pergunta e os trechos recuperados. Validar as citações contra o contexto enviado e aplicar o contrato de esclarecimento, recusa e ausência de evidência.
3. Rodar a avaliação com o gabarito isolado e revisar manualmente as respostas, incluindo omissões, alucinações e recusas incorretas.
