# Roteiro de demonstração — 3 minutos

**Antes de gravar:** use uma instalação local, nada de dados pessoais reais. A aplicação não deve estar exposta à internet. Abra o Ollama e baixe `qwen3:4b-instruct`. Se não estiver funcionando, informe explicitamente que está em modo demonstração **sem IA**; não use a baseline fingindo que é o Qwen.

1. **Apresente o painel:** total de solicitações, pendências, taxa de ajustes humanos e latência medida do modelo. Explique por que taxa de ajuste não é sinônimo de erro de IA.
2. **Crie uma solicitação fictícia:** título “VPN desconecta durante reunião”, descrição com o contexto e pessoa fictícia. Mostre que o Qwen sugere categoria e prioridade, mas não aprova nada sozinho.
3. **Abra a revisão:** ajuste uma prioridade ou equipe, registre justificativa e aprove. Mostre que o histórico guarda tanto a sugestão quanto a decisão humana.
4. **Mostre o n8n:** importe o webhook e acione uma solicitação, ou mostre o fluxo importável se não houver Docker disponível. Não afirme execução se não tiver sido feita.
5. **Mostre avaliação:** rode `AVALIAR_DESKFLOW.bat` com o Qwen real e mostre a contagem de acertos e erros, ou destaque que os resultados ainda são somente baseline sintética.
6. **Google Sheets opcional:** se tiver autorizado credenciais, faça sincronização de metadados pelo n8n. Se não, mostre o workflow preparado e explique que ele exige credenciais próprias.

## Como explicar decisões em entrevista

**Por que não aprovar automaticamente?** Um LLM pode errar categoria, prioridade e resposta; o sistema precisa de revisão para decisões com impacto sobre pessoas.

**Por que SQLite?** Simplicidade para protótipo local e testes reproduzíveis. Para equipe/produção, banco compartilhado, autenticação, filas e backups adequados seriam necessários.

**Por que n8n?** Integrações são desenhadas visualmente e podem ser alteradas sem tocar no núcleo de classificação. A entrada via webhook é genérica; planilha é uma saída opcional.

**O que é realmente seu?** Arquitetura do fluxo, validações, integração, UI, modelo de dados, trilha de auditoria, avaliação e documentação do projeto. Qwen, Ollama, n8n e Google Sheets são tecnologias de terceiros. Reconheça a assistência de IA no desenvolvimento.

**Qual foi o resultado medido?** 24 testes automatizados do software e, em laboratório, 15/16 acertos de categoria da baseline determinística. Resultados reais com Qwen e métricas de negócio dependem de execução e medição separadas.
