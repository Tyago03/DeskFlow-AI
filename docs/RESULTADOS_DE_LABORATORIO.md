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

**O que ainda precisa ser feito para relatar IA generativa:** executar `AVALIAR_DESKFLOW.bat` com o Ollama/Qwen real, guardar o relatório gerado em `evaluation/results/` (ignorado pelo Git), revisar falhas e documentar resultados honestos.

**Não medido:** horas economizadas, redução de custo, produtividade de funcionários reais, SLA ou resultados comerciais. Para alegar qualquer ganho seria necessário medir esses indicadores em ambiente autorizado com grupo de comparação apropriado.
