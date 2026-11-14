# Roteiro de demonstração

1. **Abertura.** Apresente o ROTA LIVRE, a Global Solution FIAP 2026.2 e a disciplina Generative AI for Engineering. Calçadas danificadas, rampas bloqueadas e travessias difíceis podem limitar a autonomia. O mapa mostra ocorrências de exemplo e o assistente oferece orientação documental.
2. **Mapa.** Abra o [MVP local](http://127.0.0.1:5173/). Mostre os dois obstáculos e clique no marcador de calçada danificada. O popup mostra o status “Pendente”.
3. **Como funciona.** Três fontes oficiais deram origem a 30 chunks. O MiniLM transforma a pergunta em vetor. O FAISS recupera até três trechos acima do limiar. O Qwen2.5-0.5B-Instruct roda em CPU e seleciona texto documental. A aplicação valida a saída e monta as citações.
4. **Chat com evidência.** Envie “Em que espaços podem existir barreiras urbanísticas?”. Mostre a resposta sobre vias e espaços públicos ou privados abertos ao público ou de uso coletivo. A interface apresenta a citação “Barreiras urbanísticas”, correspondente ao chunk `lbi-02`.
5. **Ausência de evidência.** Envie “O elevador da estação Paraíso está funcionando agora?”. Mostre a resposta literal `não consta`. A base legislativa não tem informação operacional atual.
6. **Ambiguidade.** Envie “Tem percentual mínimo?”. Mostre “Percentual mínimo de qual item, como vagas ou banheiros químicos?”.
7. **Agente.** O chat usa o agente por padrão. Ele reutiliza a busca e verifica o chunk e sua fonte antes da resposta. O RAG simples e o agente empataram no conjunto histórico.
8. **Métricas e conclusão.** Apresente Recall@1 de 13/18 (72,22%) e Recall@3 de 17/18 (94,44%). Nos 30 casos por modo, o acerto integral foi 8/30 no baseline e 19/30 tanto no RAG como no agente. O limiar foi calibrado de forma exploratória. Cada modo documental teve 9/13 citações pertinentes. O MVP demonstra orientação rastreável e ainda exige validação mais ampla.

As três perguntas foram verificadas no chat e nos dois modos por HTTP. [Respostas registradas](../evidencias/consultas_gravacao.json) · [Placar e limitações](../avaliacao/analise_comparativa.md)
