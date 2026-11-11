# Validação da entrega — DeskFlow AI 1.0.0

**Ambiente:** Python 3.13/Linux, teste local em novembro de 2026. Não representa teste nativo de Windows ou n8n em Docker.

## Execuções desta entrega

- **24 testes automatizados aprovados:** criação de tickets, revisão, concorrência/repetição, métricas, esquema do modelo via resposta simulada, autorização de integrações, exportação CSV, workflows JSON, persistência e validação de entradas.
- **Verificação do JavaScript:** `node --check app/static/app.js` aprovado.
- **Compilação dos módulos Python:** concluída sem erros.
- **Scanner preventivo:** `python -m scripts.preflight` sem alertas nos arquivos de publicação.
- **Avaliação da baseline determinística:** 16 casos sintéticos: 15/16 categorias e 16/16 prioridades. Não é avaliação de IA.

## Limitações desta validação

- **Ollama/Qwen real:** não executado nesta máquina. A API do LLM foi simulada com `httpx.MockTransport` para testar contratos de dados e falhas.
- **n8n e Google Sheets:** modelos JSON validados estruturalmente, porém a importação no n8n Docker e as credenciais Google OAuth **não foram executadas**, pois não estão disponíveis aqui.
- **Windows `.bat`:** revisados como texto; execução em Windows não ocorreu.
- **Interface via navegador:** Chromium/Playwright renderizou o HTML, CSS e JavaScript reais usando respostas do FastAPI de uma base demonstrativa, transmitidas por uma ponte simulada em memória. Confirmados: painel com cinco solicitações fictícias, status “Modo demonstração · sem IA”, indicadores, abertura de modal e ausência de exceções JavaScript nos cenários de captura. Duas imagens estão em `docs/preview.webp` e `docs/review.webp`. O acesso HTTP direto do navegador ao servidor foi bloqueado (`ERR_BLOCKED_BY_ADMINISTRATOR`); **isso não equivale a um teste de navegador com rede real**.
- **Impacto de negócios:** não medido. Não há horas economizadas, usuários empresariais reais ou produção em empresa.

Os resultados acima distinguem claramente **testes de software** de **acertos reais do modelo**. Em caso de divergência, não apresente métricas sintéticas como desempenho em produção.

## Publicação e capturas

- Screenshots feitos com **solicitações fictícias** e a linha de base por regras; a captura do modal foi aberta pela interação com uma linha de tabela.
- A marcação visual “sem IA” foi preservada, para não induzir quem lê o portfólio a acreditar que os prints validam Qwen ou n8n.
- Publicação exclui `.env`, bancos, caches, logs, resultados locais e o script de criação automática do repositório, desnecessário na versão já publicada.
