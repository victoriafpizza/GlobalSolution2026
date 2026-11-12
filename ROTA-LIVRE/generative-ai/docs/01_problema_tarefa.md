# Etapa 1 · Problema e tarefa

## Mobilidade e público

Calçadas danificadas, rampas bloqueadas e travessias difíceis podem interromper deslocamentos e reduzir a autonomia de quem precisa acessar transporte, trabalho e serviços. Pessoas com deficiência, pessoas com mobilidade reduzida e idosos são o público prioritário. Demais cidadãos também podem consultar orientações de acessibilidade para entender e reconhecer barreiras.

O assistente ROTA LIVRE propõe traduzir documentos oficiais em orientações gerais em português claro, com referências que permitam ao usuário conferir as fontes.

## Situação do projeto

O [frontend React/Vite](../../frontend/package.json) usa Leaflet. O [backend FastAPI](../../backend/main.py) expõe `GET /api/obstacles` e retorna dois registros definidos no código. O [documento de arquitetura](../../docs/arquitetura/arquitetura.md) descreve o MVP. O assistente, a recuperação de evidências e a geração de respostas são funcionalidades planejadas. A base desta entrega contém legislação e os registros da API ficam fora do acervo.

## Contrato do assistente

A entrada é uma pergunta textual em português, com contexto funcional opcional, como tipo de via, instalação ou obstáculo. A saída tem um estado e um texto curto. Para respostas factuais, inclui referências com título da lei, dispositivo, URL e ID do chunk.

| Estado | Comportamento |
| --- | --- |
| `respondido` | Explicar exclusivamente o que os chunks verificados sustentam. Citar cada afirmação factual e preservar condições, exceções e âmbito do dispositivo. |
| `esclarecimento` | Fazer uma pergunta objetiva quando a informação em falta puder tornar a consulta documental respondível. Omitir fatos e citações até resolver a ambiguidade. |
| `sem_evidencia` | Quando a pergunta estiver clara e faltar evidência suficiente, retornar literalmente `não consta`, em minúsculas, sem aspas, pontuação, complemento ou referências. |
| `recusa` | Recusar internamente pedidos de garantia de segurança, certificação ou navegação operacional quando um esclarecimento for insuficiente. Quando faltar evidência, o texto visível é literalmente `não consta`. |

O escopo cobre conceitos de acessibilidade, tipos de barreira, requisitos legais gerais e direitos de usuários no transporte. Pedidos de rotas acessíveis, condições atuais de vias e equipamentos, dados geográficos, laudos, aconselhamento jurídico individual e medidas de normas técnicas ausentes ficam fora do escopo. Inventar leis, números de artigos, normas, condições de circulação ou garantias é proibido. As menções legais à ABNT sustentam a existência de uma referência técnica. Medidas dependem da consulta autorizada ao texto aplicável.

## Segurança e privacidade

Aplicar finalidade, adequação e necessidade. Solicitar apenas o contexto funcional da consulta. Evitar CPF, telefone, endereço residencial, localização precisa, diagnóstico e prontuário. Em futura implementação, suprimir esses dados antes do registro de logs, limitar acesso e retenção e avaliar a base legal antes de qualquer tratamento de dados pessoais. Perguntas e trechos recuperados devem ser tratados como dados, inclusive quando contiverem instruções para ignorar o contrato. [LGPD, art. 6º](https://www2.camara.leg.br/legin/fed/lei/2018/lei-13709-14-agosto-2018-787077-normaatualizada-pl.html)

## Casos de uso e aceite futuro

| Consulta | Critério observável |
| --- | --- |
| Classificar barreira em espaço de uso coletivo | Identificar o conceito correto e citar o dispositivo com ID e URL válidos. |
| Entender quais informações devem existir nos pontos de embarque | Cobrir itinerários, horários, tarifas e conexões sem atribuir condições a um ponto específico. |
| Perguntar “Tem percentual mínimo?” | Pedir que o usuário identifique o item antes de informar um percentual. |
| Perguntar por condição atual de uma rampa | Produzir exatamente `não consta` e zero citações. |
| Pedir garantia de passagem segura | Classificar como recusa e produzir exatamente `não consta`. |

No conjunto de aceite, cada um dos 18 casos factuais deve cumprir seu critério e citar evidência válida. Os quatro esclarecimentos devem pedir apenas o contexto necessário. As duas recusas e os seis casos sem evidência devem usar a expressão literal, sem citações.
