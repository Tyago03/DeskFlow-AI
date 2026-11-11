# Integração n8n + Google Sheets

Os arquivos `workflows/*.json` são **modelos de workflow importáveis**. É preciso conectar as credenciais do seu próprio n8n. Eles **não têm tokens embutidos** e não são ativados automaticamente. A importação real no n8n não foi executada no ambiente de desenvolvimento (Docker indisponível); valide os campos no editor após importar.

## Iniciar o n8n

1. Instale **Docker Desktop** e confira `docker compose version`.
2. Abra `INICIAR_N8N.bat` (ou execute `docker compose up -d` na raiz).
3. Acesse `http://127.0.0.1:5678` e configure o proprietário da instância local. Não exponha a porta na internet.

## Preparar credencial do backend

1. Execute `CONFIGURAR_INTEGRACAO.bat` após preparar `.venv`; ele cria **`.env` local** com um segredo aleatório.
2. Para permitir chamadas do n8n Docker, inicie a API com `INICIAR_COM_N8N.bat`. **O backend passa a escutar em `0.0.0.0`: restrinja a porta 8000 no firewall.**
3. No editor n8n, crie uma credencial **Header Auth** com `Name: X-DeskFlow-Key` e `Value: (DESKFLOW_INGEST_KEY salvo no seu .env local)`.
4. Atribua essa credencial ao nó **Enviar para DeskFlow** e ao nó **Consultar métricas DeskFlow** dos respectivos workflows.

**Não coloque a chave literalmente no JSON do workflow nem publique o `.env`.** Se usar outra máquina para o n8n, ajuste a URL do backend e configure uma rede protegida — este MVP não foi projetado para exposição remota.

## Fluxo 1 — entrada automatizada

1. No n8n, importe `workflows/01_entrada_n8n.json` (menu de workflows → importar arquivo).
2. Configure a credencial Header Auth no nó HTTP Request.
3. No nó **Webhook de entrada**, use **Test URL**, clique em **Listen for test event** e envie um POST com título, descrição e solicitante.
4. Depois de validar, salve e **publique/ative** o workflow para usar a URL de produção. Para evitar exposição, mantenha o n8n local.

Exemplo com PowerShell (substitua a URL pela que o n8n mostrar):

```powershell
$body = @{ title = "VPN desconectando na reunião"; description = "A conexão cai a cada dez minutos e atrapalha reuniões internas."; requester = "Pessoa fictícia" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:5678/webhook-test/deskflow-intake" -Method Post -ContentType "application/json" -Body $body
```

O webhook retorna a solicitação recebida e sua sugestão de triagem, que aparece **pendente de aprovação** no painel DeskFlow. Mesmo se o Qwen demorar, o workflow é síncrono nesta versão e pode estourar timeout; esse limite é intencionalmente documentado.

## Fluxo 2 — Google Sheets (opcional e sem dados pessoais)

1. Crie uma planilha de demonstração com uma aba chamada **`Solicitacoes`**.
2. Preencha a linha 1 com os cabeçalhos abaixo, na mesma grafia:

```text
ticket_id | created_at | status | category | priority | team | source | triage_mode | latency_ms | review_changed
```

3. Importe `workflows/02_exportar_google_sheets.json` no n8n.
4. Configure credencial **Header Auth** no nó HTTP Request de consulta ao backend.
5. Crie credencial Google Sheets no n8n (OAuth / método disponível à sua conta) e selecione essa credencial no último nó.
6. Substitua `REPLACE_WITH_SHEET_ID` pelo ID da planilha e confira o nome da aba.
7. Faça **execução manual**, examine as linhas, depois decida se quer automatizar com um Schedule Trigger.

O fluxo utiliza **Append or Update Row** pela coluna `ticket_id` para evitar duplicação. O endpoint `/api/integrations/sheets_rows` não transmite nome do solicitante, título, descrição ou resposta sugerida. **A sincronização automática não é ativada sem sua configuração.**

## Cuidados

- Use apenas **solicitações fictícias** na demonstração. Evite dados reais de funcionários ou clientes.
- n8n e Google Sheets são serviços de terceiros e podem armazenar dados das execuções. Configure retenção e permissões.
- Não envie a `.env`, banco SQLite, credenciais OAuth, exports de n8n com segredos, nem planilhas pessoais ao GitHub.

Referências: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/ ; https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.googlesheets/sheet-operations/
