# Verificação da demonstração local

O build do Vite terminou com sucesso. No navegador, a página exibiu dois obstáculos e dois marcadores do Leaflet. A pergunta “Em que espaços podem existir barreiras urbanísticas?” foi enviada pelo formulário. Após a inferência local, o chat mostrou a resposta sobre vias e espaços públicos ou privados abertos ao público ou de uso coletivo e o link da Câmara. A [resposta HTTP](api_resposta.json) foi capturada separadamente com a mesma pergunta e contém a citação lbi-02.

A suíte passou em 19 testes, incluindo quatro de integração ASGI com TestClient. O cliente HTTP de loopback verificou GET /api/obstacles e POST /api/ai/ask, com inferência real nos casos factuais. O [resultado reservado](../avaliacao/validacao_reservada.json) contém quatro casos por modo e oito acertos pelo critério de status, ID esperado ou recusa/esclarecimento. O limiar permaneceu congelado. O caso de esclarecimento é uma regressão próxima da pergunta histórica qa-021, e os quatro casos são insuficientes para estimar desempenho geral.

Antes da correção, o evento histórico qa-021 pedia local, situação ou requisito de modo genérico. Depois, a regra solicita qual item e oferece exemplos. A pergunta original e uma variação passaram no teste da API. Os outros quatro diagnósticos mantêm propostas de correção.
