# Limiar de recuperação · análise exploratória

O score é a similaridade cosseno do primeiro candidato. Aceite significa que o score atingiu o limiar. Esse critério mede a passagem pelo filtro e não confirma que o candidato responde à pergunta.

| Limiar | Aceites corretos | Rejeições corretas | Falsos positivos | Falsos negativos | Taxa de rejeição |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0,398938 | 18 | 5 | 1 | 0 | 20,83% |
| 0,448389 | 18 | 6 | 0 | 0 | 25,00% |
| 0,529954 | 17 | 6 | 0 | 1 | 29,17% |

A seleção minimiza a média entre a taxa de falsos positivos e a de falsos negativos. Em empate, prefere menos falsos positivos e depois o limiar maior. O valor usado é 0,4483887553215027, ponto médio entre o maior negativo (0,408741) e o menor positivo (0,488036). As seis perguntas ambíguas ficaram fora do ajuste. Uma delas ultrapassou o limiar. A tabela mostra três candidatos vizinhos e o CSV preserva a varredura completa.

| Grupo factual | Recall@1 e Hit@1 | Recall@3 e Hit@3 |
| --- | ---: | ---: |
| Total | 13/18 (72,22%) | 17/18 (94,44%) |
| Diretas | 9/12 (75,00%) | 11/12 (91,67%) |
| Paráfrases | 4/6 (66,67%) | 6/6 (100,00%) |

Em qa-001, o índice retornou lbi-10 (0,587925) sobre adaptação em projetos. A definição esperada em lbi-01 ficou fora do top-3, embora a consulta tenha ultrapassado o limiar. A separação observada é exploratória. O mesmo gabarito escolheu o limiar e produziu os resultados, com apenas 18 positivos, seis negativos e um corpus de 30 chunks.
