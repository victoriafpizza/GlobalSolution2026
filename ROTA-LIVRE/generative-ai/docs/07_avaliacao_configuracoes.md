# Etapa 7 · Avaliação reproduzível

A pasta independente contém as etapas 1 a 6. A pasta antiga em C:\GSIA\ROTA-LIVRE\generative-ai contém o material inicial e dependências locais. Os hashes do corpus e do gabarito coincidem. A consolidação proposta é manter a pasta independente como referência, preservar o checkout antigo e comparar hashes e diffs antes de importar qualquer trabalho exclusivo. Esta execução fez apenas leitura na pasta antiga.

Na raiz independente, em PowerShell com o ambiente Python das etapas anteriores ativo:

```powershell
python -B -m scripts.avaliar_qualidade
python -B -m unittest discover -s tests -v
```

O script relê o histórico das 90 execuções e verifica a identidade e ordem dos casos. Preserva os arquivos de origem. A avaliação usa uma revisão semântica vinculada pelo SHA-256 ao histórico examinado. Uma nova execução precisa de revisão própria. Veja o [placar e interpretação](../avaliacao/analise_comparativa.md).

Para recriar os gráficos, instale matplotlib 3.11.2 em um ambiente separado e execute python -B -m scripts.graficos_qualidade. [Figura](../avaliacao/graficos_qualidade.png).
