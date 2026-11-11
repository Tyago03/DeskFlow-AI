# Resultados de laboratório — DeskFlow AI

**Data:** 10 de novembro de 2026 (execução de avaliação preparada nesta entrega).  
**Conjunto:** 16 solicitações completamente sintéticas e rotuladas manualmente para exercício.  
**Classificador medido:** linha de base por regras e palavras-chave (`baseline_classify`). **Não é IA generativa.**

| Métrica | Resultado da execução local |
| --- | ---: |
| Categoria | 15/16 = **93,75%** |
| Prioridade | 16/16 = **100%** |
| Categoria + prioridade simultâneas | 15/16 = **93,75%** |

Esses valores são apenas para testar a mecânica da avaliação em uma amostra pequena e previsível; não são generalizáveis e não representam acurácia do Qwen. O classificador-base foi construído com regras do mesmo domínio das frases sintéticas, portanto a amostra não deve ser vista como benchmark independente.

## Classificação real com Qwen

**Execução:** 10/11/2026 no computador do autor, usando `qwen3:4b-instruct` via Ollama.
**Conjunto:** os mesmos 16 casos sintéticos rotulados; são dados de exercício, não solicitações reais de uma empresa.

| Métrica | Qwen / Ollama |
| --- | ---: |
| Categoria | **15/16 = 93,75%** |
| Prioridade | **12/16 = 75,00%** |
| Categoria + prioridade corretas | **11/16 = 68,75%** |
| Latência média | **4.116 ms (~4,1 s)** |

Os casos com divergência conjunta foram T07 (prioridade crítica → alta), T10 (financeiro → outros), T12 (média → baixa), T13 (alta → média) e T15 (média → alta). **Não houve falha de execução do modelo nas 16 chamadas.**

**Comparação:** no mesmo conjunto, a baseline por regras atingiu 15/16 categorias e 16/16 prioridades. Essa baseline foi construída com regras do próprio domínio de teste; a amostra pequena **não permite** concluir superioridade ou inferioridade geral de uma abordagem.

## Integrações executadas com dados fictícios

**Validação adicional em 10–11/11/2026:**

- **Formulário web → FastAPI → Qwen → revisão humana:** executado localmente.
- **n8n webhook → API autenticada → Qwen → resposta HTTP:** executado ponta a ponta; um ticket chegou com origem `n8n`, categoria `rede`, prioridade `alta` e latência de 12.576 ms.
- **Google Sheets:** workflow acionado **manualmente** com credencial OAuth do autor. O registro de duas solicitações aprovadas foi verificado na aba `Solicitacoes` e seus indicadores na aba `Resumo`; somente metadados permitidos foram sincronizados.
- **Média de latência no conjunto das duas solicitações sincronizadas:** aproximadamente **11,8 s** (10.929 e 12.576 ms). Não compare diretamente com a média dos 16 casos de avaliação, pois foram execuções diferentes.

Os dois tickets tiveram `review_changed=FALSE`. Isso apenas indica ausência de alterações humanas nessas revisões; não equivale a precisão validada nem produtividade de negócio.


**Não medido:** horas economizadas, redução de custo, produtividade de funcionários reais, SLA ou resultados comerciais. Para alegar qualquer ganho seria necessário medir esses indicadores em ambiente autorizado com grupo de comparação apropriado.
