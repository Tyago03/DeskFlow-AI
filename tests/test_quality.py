"""Regressão de integridade, autenticação, relatórios e revisões."""
import csv
import io
import json
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

from app.api import create_app
from app.schemas import TicketIn
from app.store import Store
from app.triage import OllamaTriage

RESULT={
 "category":"rede","priority":"media","team":"infraestrutura",
 "summary":"Conexão instável na sala de reuniões",
 "suggested_reply":"Recebemos a solicitação; informe os horários aproximados das quedas.",
 "rationale":"A conexão apresenta quedas em uma sala.","confidence":0.63,
}


def test_real_llm_mode_metrics_with_mock(tmp_path):
    def handler(req):
        assert req.url.path=="/api/chat"
        return httpx.Response(200,json={"message":{"content":json.dumps(RESULT)}})
    cls=OllamaTriage(client=httpx.Client(transport=httpx.MockTransport(handler)))
    app=create_app(store=Store(tmp_path/"mock_model.sqlite3"),classifier=cls,demo=False,integration_key="x"*32)
    with TestClient(app) as client:
        data={"title":"VPN caindo na reunião", "description":"A conexão cai a cada cinco minutos na reunião de testes."}
        response=client.post("/api/tickets",json=data)
        assert response.status_code==201
        row=response.json()
        assert row["triage_mode"]=="ollama"
        assert row["priority"]=="media"
        metrics=client.get("/api/metrics").json()
        assert metrics["ai_triages"]==1
        assert metrics["baseline_triages"]==0
        assert metrics["average_llm_latency_ms"] is not None


def test_integrations_disabled_without_secret(tmp_path):
    from app.triage import baseline_classify
    app=create_app(store=Store(tmp_path/"no_key.sqlite3"),classifier=baseline_classify,demo=True,integration_key="")
    with TestClient(app) as client:
        response=client.post("/api/integrations/tickets",json={"title":"Nova solicitação", "description":"Pedido fictício de integração com o n8n."})
        assert response.status_code==503


def test_sheets_export_uses_final_after_review(app_client,sample):
    t=app_client.post("/api/tickets",json=sample).json()
    final={"decision":"approve","category":"financeiro","priority":"baixa","team":"financeiro",
           "suggested_reply":"Obrigado pelo contato; equipe financeira revisará os dados.","reviewer_note":"Teste"}
    app_client.post(f"/api/tickets/{t['id']}/review",json=final)
    row=app_client.get("/api/integrations/sheets_rows",headers={"X-DeskFlow-Key":"a"*32}).json()["rows"][0]
    assert row["category"]=="financeiro"
    assert row["priority"]=="baixa"
    assert row["review_changed"] is True
    assert row["status"]=="approved"


def test_csv_has_header_and_safe_cell(app_client,sample):
    t=app_client.post("/api/tickets",json={**sample,"title":"@CMD|teste"}).json()
    response=app_client.get("/api/export.csv")
    content=response.content.decode("utf-8-sig")
    rows=list(csv.DictReader(io.StringIO(content)))
    assert len(rows)==1
    assert rows[0]["title"].startswith("'@")
    assert rows[0]["id"]==t["id"]


def test_review_original_prediction_unchanged(app_client,sample):
    t=app_client.post("/api/tickets",json=sample).json()
    outcome=app_client.post(f"/api/tickets/{t['id']}/review",json={
      "decision":"approve","category":"hardware","priority":"critica","team":"suporte_ti",
      "suggested_reply":"Recebemos seu contato e vamos avaliar as condições informadas."
    }).json()
    assert outcome["category"]==t["category"]
    assert outcome["priority"]==t["priority"]
    assert outcome["final_category"]=="hardware"
    assert outcome["final_priority"]=="critica"


def test_ui_includes_no_external_script_or_cdn():
    html=(Path(__file__).resolve().parents[1]/"app/static/index.html").read_text(encoding="utf8")
    assert "https://" not in html
    assert '<script src="/static/app.js"' in html
    assert "innerHTML" not in (Path(__file__).resolve().parents[1]/"app/static/app.js").read_text(encoding="utf8")


def test_no_secret_in_n8n_workflow_templates():
    root=Path(__file__).resolve().parents[1]
    for file in (root/"workflows").glob("*.json"):
        raw=file.read_text(encoding="utf8")
        assert "DESKFLOW_INGEST_KEY=" not in raw
        assert '"credentials"' not in raw
