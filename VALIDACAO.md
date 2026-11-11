# Validação da entrega — DeskFlow AI 1.0.0

**Ambiente da entrega inicial:** Python 3.13/Linux, com respostas simuladas. **Validação complementar:** Windows, Ollama/Qwen, Docker Desktop, n8n e Google Sheets executados posteriormente no computador do autor, em 10–11/11/2026.

## Execuções desta entrega

- **24 testes automatizados aprovados:** criação de tickets, revisão, concorrência/repetição, métricas, esquema do modelo via resposta simulada, autorização de integrações, exportação CSV, workflows JSON, persistência e validação de entradas.
- **Verificação do JavaScript:** `node --check app/static/app.js` aprovado.
- **Compilação dos módulos Python:** concluída sem erros.
- **Scanner preventivo:** `python -m scripts.preflight` sem alertas nos arquivos de publicação.
- **Avaliação da baseline determinística:** 16 casos sintéticos: 15/16 categorias e 16/16 prioridades. Não é avaliação de IA.

## Validação complementar com integrações reais (10–11/11/2026)

A execução do autor, em um notebook Windows, comprovou:

- **Qwen via Ollama:** avaliação de 16 casos sintéticos; categoria **15/16**, prioridade **12/16**, acerto conjunto **11/16**; latência média **4.116 ms**. Não houve falha de execução nesses 16 casos.
- **DeskFlow web:** envio de solicitação fictícia, triagem real pelo Ollama e decisão humana registrada.
- **Webhook n8n:** os três nós de entrada, encaminhamento autenticado e resposta concluíram a execução; o PowerShell recebeu ticket com `source=n8n`, `triage_mode=ollama` e `latency_ms=12576`.
- **Google Sheets via n8n:** os quatro nós foram concluídos e a leitura posterior da planilha confirmou **2 registros**, ambos aprovados, sendo **1 com origem n8n**. Latências registradas: 10.929 ms e 12.576 ms (**média aproximada de 11,8 s**).
- **Revisão:** nenhum ajuste humano nos campos revisados dessas duas solicitações; isso **não é** medida de precisão geral.

A sincronização com Google Sheets foi **manual**. Os dados empregados na demonstração eram fictícios; credenciais OAuth, conteúdo pessoal da planilha e segredos não integram o repositório.

## Limitações dos testes iniciais (ambiente Linux)

Os tópicos abaixo se referem à **entrega inicial**, antes da validação complementar realizada no Windows. Foram preservados para documentar quais aspectos originalmente não estavam cobertos:


- **Ollama/Qwen real na execução inicial em Linux:** não executado nessa máquina; a API foi simulada com `httpx.MockTransport`. A execução real posterior no Windows está registrada acima.
- **n8n e Google Sheets na entrega inicial:** os JSON foram validados estruturalmente, mas não havia Docker/OAuth nesse ambiente. A execução posterior no Windows está registrada acima.
- **Windows `.bat` na entrega inicial:** revisados como texto; a execução no notebook do autor foi confirmada posteriormente por capturas e resultados, mas sem uma nova auditoria automatizada de todos os atalhos.
- **Interface via navegador:** Chromium/Playwright renderizou o HTML, CSS e JavaScript reais usando respostas do FastAPI de uma base demonstrativa, transmitidas por uma ponte simulada em memória. Confirmados: painel com cinco solicitações fictícias, status “Modo demonstração · sem IA”, indicadores, abertura de modal e ausência de exceções JavaScript nos cenários de captura. Duas imagens estão em `docs/preview.webp` e `docs/review.webp`. O acesso HTTP direto do navegador ao servidor foi bloqueado (`ERR_BLOCKED_BY_ADMINISTRATOR`); **isso não equivale a um teste de navegador com rede real**.
- **Impacto de negócios:** não medido. Não há horas economizadas, usuários empresariais reais ou produção em empresa.

Os resultados acima distinguem claramente **testes de software** de **acertos reais do modelo**. Em caso de divergência, não apresente métricas sintéticas como desempenho em produção.

## Publicação e capturas

- Screenshots feitos com **solicitações fictícias** e a linha de base por regras; a captura do modal foi aberta pela interação com uma linha de tabela.
- A marcação visual “sem IA” foi preservada, para não induzir quem lê o portfólio a acreditar que os prints validam Qwen ou n8n.
- Publicação exclui `.env`, bancos, caches, logs, resultados locais e o script de criação automática do repositório, desnecessário na versão já publicada.
