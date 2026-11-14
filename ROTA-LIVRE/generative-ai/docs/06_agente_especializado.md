# Etapa 6 · Agente especializado

A comparação usa a mesma revisão do Qwen, temperatura zero, seed 42, 340 tokens máximos e timeout de 25 segundos por inferência.

| Modo | Execução |
| --- | --- |
| baseline | LLM sem índice e sem citações. Controle experimental. |
| rag | Busca top-3 com limiar, decisão do modelo e validação textual. |
| agente | Política para mobilidade urbana, busca por ferramenta e verificação do candidato no catálogo documental antes da resposta. |

O agente tem fluxo fixo com ferramentas reais e estruturadas. `buscar_documentos` reutiliza o índice. `validar_evidencias` usa `obter_chunk` e `verificar_fonte` para confirmar texto, IDs e URL. O fluxo permite uma chamada ao LLM e limita a oito chamadas de ferramenta. Os logs locais registram ID aleatório, modo, ferramentas, passos, chunks, erro, tempo e status. A pergunta e o texto do usuário ficam fora do log operacional.

```powershell
& .\.venv\Scripts\python.exe -m scripts.testar_geracao 'O que significa desenho universal segundo a LBI?' --modo agente
& .\.venv\Scripts\python.exe -m scripts.comparar_configuracoes
```

O avaliador envia a mesma pergunta a cada modo e usa o gabarito após a saída. Acurácia de status usa todos os casos. Igualdade textual e citações esperadas usam os 18 factuais. Igualdade textual favorece a estratégia extrativa e pode subestimar paráfrases corretas do baseline. Recusa adequada usa os oito casos com recusa ou ausência de evidência. Fundamentação indica resposta com evidência textual verificada. Isso não mede alucinação sem revisão semântica, especialmente no baseline. O relatório distingue JSON do modelo de JSON final produzido pelo pipeline.

Nas próximas etapas, reservar casos independentes, revisar relevância e alucinação manualmente, testar ataques variados e medir desempenho em um corpus ampliado.
