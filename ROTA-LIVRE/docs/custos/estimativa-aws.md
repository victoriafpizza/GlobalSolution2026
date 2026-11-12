# Estimativa de custos AWS — ROTA LIVRE

**Referência das tarifas:** 12/11/2026. **Região:** US East (Ohio), `us-east-2`. **Moeda:** USD. A estimativa usa preços públicos sob demanda, sem impostos ou créditos promocionais, para uma EC2 Linux `t3.small`, um volume raiz gp3 criptografado de 20 GiB e um IPv4 público em uso. A auditoria confirmou 3.000 IOPS, 125 MiB/s e modo de créditos de CPU `unlimited`. [Terraform da EC2](../../infra/main.tf)

## Tarifas e cálculo

O cenário diário considera 24 horas contínuas. O mensal usa 30 dias de 24 horas, totalizando 720 horas, com o volume provisionado durante todo o período. Os totais são arredondados apenas ao final.

| Componente | Tarifa pública | 24 horas | 30 dias |
| --- | ---: | ---: | ---: |
| EC2 Linux `t3.small` sob demanda | US$ 0,0208/h | US$ 0,4992 | US$ 14,9760 |
| IPv4 público em uso | US$ 0,005/h | US$ 0,1200 | US$ 3,6000 |
| EBS gp3, 20 GiB, desempenho básico | US$ 0,08 por GB-mês | US$ 0,0533, proporcional | US$ 1,6000 |
| VPC padrão, subnet e Security Group | Sem cobrança própria pelos componentes usados | US$ 0 | US$ 0 |
| IAM role e instance profile | Sem cobrança própria de IAM | US$ 0 | US$ 0 |
| Systems Manager na EC2 | Sem cobrança adicional de Session Manager e Run Command na EC2 | US$ 0 | US$ 0 |
| **Total-base estimado** | **US$ 0,0258/h de EC2 + IPv4, mais EBS** | **US$ 0,67** | **US$ 20,18** |

Cálculo mensal: `720 × 0,0208 + 720 × 0,005 + 20 × 0,08 = 20,176 USD`. O cenário-base pressupõe saída de dados dentro da franquia aplicável e zero créditos excedentes de CPU cobrados. O gp3 inclui os 3.000 IOPS e 125 MiB/s verificados. A configuração usa Run Command para diagnóstico e Session Manager para o túnel de métricas. Serviços adicionais ligados ao SSM e a transferência de dados têm regras próprias. [EC2 sob demanda](https://aws.amazon.com/ec2/pricing/on-demand/) · [EBS](https://aws.amazon.com/ebs/pricing/) · [VPC e IPv4](https://aws.amazon.com/vpc/pricing/) · [IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html) · [Systems Manager](https://aws.amazon.com/systems-manager/pricing/)

## Transferência de dados e créditos de CPU

O catálogo consultado indicou **US$ 0 por GB** na entrada da internet e **US$ 0,09 por GB** na primeira faixa paga de saída de Ohio, até 10 TB por mês além da franquia global. A AWS publica uma franquia de 100 GB mensais de saída para a internet, agregada entre serviços e regiões elegíveis. Por exemplo, 150 GB de saída no mês com os 100 GB de franquia ainda disponíveis resultam em 50 GB pagos, **US$ 4,50** adicionais e total estimado de **US$ 24,68**. O frontend e a API públicos contribuem para o tráfego do projeto. O volume real de saída e a franquia restante ficaram sem verificação. [Transferência de dados EC2](https://aws.amazon.com/ec2/pricing/on-demand/) · [Catálogo regional AWS Data Transfer](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSDataTransfer/current/us-east-2/index.json)

A `t3.small` tem 2 vCPUs e capacidade-base de CPU de 20% por vCPU. No modo `unlimited` verificado, picos cobertos pelo saldo de créditos estão incluídos na tarifa da instância. Uso sustentado acima da capacidade-base pode resultar em créditos excedentes faturados, conforme a média móvel de 24 horas ou a vida da instância, quando menor. A tarifa publicada para T3 Linux é **US$ 0,05 por vCPU-hora excedente cobrada**. A estimativa-base não inclui esse adicional, pois o consumo faturável ficou sem medição. [Especificações T3](https://aws.amazon.com/ec2/instance-types/t3/) · [Modo Unlimited](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/burstable-performance-instances-unlimited-mode.html) · [Tarifa de créditos de CPU](https://aws.amazon.com/ec2/pricing/on-demand/)

## Free Tier, créditos promocionais e fatura

O Free Tier depende do plano e da elegibilidade da conta. A AWS anuncia até US$ 200 em créditos para novos clientes elegíveis no programa atual. Créditos promocionais podem abater cobranças de serviços elegíveis até esgotarem ou vencerem. O saldo, a validade, os serviços elegíveis e a fatura da conta do projeto ficaram sem verificação. Use **US$ 20,18 por 30 dias** como referência antes de eventuais abatimentos. Para apurar o líquido, o responsável pela conta pode comparar **Bills** e **Credits** no console AWS Billing and Cost Management. [AWS Free Tier](https://aws.amazon.com/free/) · [Aplicação de créditos](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/useconsolidatedbilling-credits.html) · [Termos promocionais](https://aws.amazon.com/awscredits/)

## Como conferir as tarifas

A consulta de 12/11/2026 usou `aws pricing get-products` em modo somente leitura. A região do endpoint do catálogo foi `us-east-1`. Os filtros selecionaram produtos da região `us-east-2`. Nenhum recurso AWS foi criado para elaborar a estimativa. [Documentação do AWS Price List](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/price-changes.html)

| Consulta | Filtros aplicados | SKU e publicação do catálogo |
| --- | --- | --- |
| `AmazonEC2`, computação | `regionCode=us-east-2`, `instanceType=t3.small`, `operatingSystem=Linux`, `tenancy=Shared`, `preInstalledSw=NA`, `capacitystatus=Used`, `licenseModel=No License required` | `BQPEB7HYTVEZPKJW`, 10/11/2026 |
| `AmazonEC2`, gp3 | `regionCode=us-east-2`, `usagetype=USE2-EBS:VolumeUsage.gp3` | `M6UGCCQ3CDJQAA37`, 10/11/2026 |
| `AWSDataTransfer`, entrada | `usagetype=USE2-DataTransfer-In-Bytes` | `5CHDB6K4USP8QXF3`, 11/11/2026 |
| `AWSDataTransfer`, saída | `usagetype=USE2-DataTransfer-Out-Bytes` | `36H7S3NU9B7S3UT5`, 11/11/2026 |

Na resposta da API, consulte `terms.OnDemand` → `priceDimensions` → `pricePerUnit.USD`. A tabela regional da AWS para Linux em Ohio também retornou a tarifa de US$ 0,0208/h da EC2. [Catálogo regional Amazon EC2](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/us-east-2/index.json) · [Tabela regional AWS, Linux sob demanda](https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20%28Ohio%29/Linux/index.json) · [AWS Pricing Calculator](https://calculator.aws/)

## Estratégias de redução

- Acompanhar as linhas de EC2, EBS, IPv4, transferência e créditos de CPU pelo console do Cost Explorer, quando disponível à conta. Usar os dados observados antes de redimensionar a instância ou alterar o modo de CPU. [Cost Explorer](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-what-is.html)
- Manter o volume gp3 no desempenho básico enquanto ele atender ao MVP. Manter Prometheus e Grafana na estação de monitoramento evita provisionar uma instância AWS para esses serviços. [EBS](https://aws.amazon.com/ebs/pricing/) · [Monitoramento local](../../monitoring/README.md)
- Preservar a disponibilidade enquanto a URL for usada na entrega. Depois do período de avaliação, planejar janelas sem execução apenas se a aplicação puder ficar fora do ar. Uma parada deixa o EBS faturável e pode alterar o IPv4 atribuído automaticamente ao reiniciar. [Comportamento e custos do stop/start](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/how-ec2-instance-stop-start-works.html)
