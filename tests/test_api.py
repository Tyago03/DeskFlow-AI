import pytest

def test_home_and_health(app_client):
    r=app_client.get("/")
    assert r.status_code==200
    assert "DeskFlow" in r.text
    assert app_client.get("/api/health").json()["status"]=="ok"
    assert app_client.get("/api/system").json()["mode"]=="baseline_demo"


def test_creation_and_review(app_client,sample):
    made=app_client.post("/api/tickets",json=sample)
    assert made.status_code==201
    ticket=made.json()
    assert ticket["status"]=="pending"
    assert ticket["triage_mode"]=="baseline_demo"
    assert ticket["category"]=="acesso"
    assert app_client.get("/api/metrics").json()["total"]==1
    review={"decision":"approve","category":"software","priority":"alta","team":"suporte_ti",
            "suggested_reply":"Recebemos seu problema e precisamos confirmar mais detalhes.","reviewer_note":"Ajuste humano"}
    out=app_client.post(f"/api/tickets/{ticket['id']}/review",json=review)
    assert out.status_code==200
    assert out.json()["status"]=="approved"
    assert out.json()["final_category"]=="software"
    metrics=app_client.get("/api/metrics").json()
    assert metrics["reviewed"]==1
    assert metrics["override_rate_percent"]==100
    assert metrics["average_llm_latency_ms"] is None
    assert len(app_client.get(f"/api/tickets/{ticket['id']}").json()["history"])==1
    assert app_client.post(f"/api/tickets/{ticket['id']}/review",json=review).status_code==409


def test_reject_does_not_approve(app_client,sample):
    t=app_client.post("/api/tickets",json=sample).json()
    review={"decision":"reject","category":t["category"],"priority":t["priority"],"team":t["team"],
            "suggested_reply":t["suggested_reply"],"reviewer_note":"Sem informação suficiente"}
    res=app_client.post("/api/tickets/"+t["id"]+"/review",json=review)
    assert res.status_code==200
    assert res.json()["status"]=="rejected"
    assert app_client.get("/api/metrics").json()["rejected"]==1


def test_missing_and_bad_validation(app_client,sample):
    assert app_client.get("/api/tickets/missing").status_code==404
    assert app_client.post("/api/tickets/missing/review",json={}).status_code==422
    assert app_client.post("/api/tickets",json={**sample,"title":"x"}).status_code==422
    assert app_client.post("/api/tickets",json={**sample,"random":"ignored?"}).status_code==422
    assert app_client.post("/api/tickets",data="a").status_code==415
    assert app_client.post("/api/tickets",content=b"x"*8200,headers={"content-type":"application/json"}).status_code==413
    assert app_client.post("/api/tickets",json=sample,headers={"Origin":"https://evil.example"}).status_code==403


def test_integrations_require_secret(app_client,sample):
    assert app_client.post("/api/integrations/tickets",json=sample).status_code==403
    assert app_client.post("/api/integrations/tickets",json=sample,headers={"X-DeskFlow-Key":"wrong"}).status_code==403
    assert app_client.get("/api/integrations/sheets_rows").status_code==403
    r=app_client.post("/api/integrations/tickets",json=sample,headers={"X-DeskFlow-Key":"a"*32})
    assert r.status_code==201
    assert r.json()["source"]=="n8n"
    sheets=app_client.get("/api/integrations/sheets_rows",headers={"X-DeskFlow-Key":"a"*32}).json()
    assert len(sheets["rows"])==1
    row=sheets["rows"][0]
    assert "description" not in row
    assert "requester" not in row
    assert "title" not in row
    assert row["ticket_id"]


def test_csv_escapes_formula(app_client,sample):
    app_client.post("/api/tickets",json={**sample,"title":"=HYPERLINK(\"https://example.com\")"})
    csv=app_client.get("/api/export.csv")
    assert csv.status_code==200
    assert "text/csv" in csv.headers["content-type"]
    assert "'=HYPERLINK" in csv.text


def test_empty_metrics(app_client):
    data=app_client.get("/api/metrics").json()
    assert data["total"]==0 and data["override_rate_percent"] is None
    assert data["ai_triages"]==0
