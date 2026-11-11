import json
from pathlib import Path
from scripts.evaluate import evaluate
from scripts.preflight import main as preflight
from app.schemas import TicketIn
from app.store import Store
from app.triage import baseline_classify

ROOT=Path(__file__).resolve().parents[1]

def test_n8n_workflows_have_valid_references():
    for path in (ROOT/"workflows").glob("*.json"):
        flow=json.loads(path.read_text(encoding="utf-8"))
        ids=[n["id"] for n in flow["nodes"]]
        names={n["name"] for n in flow["nodes"]}
        assert len(ids)==len(set(ids))
        for node,edges in flow["connections"].items():
            assert node in names
            for arr in edges["main"]:
                for connection in arr:
                    assert connection["node"] in names
        assert all("credentials" not in n for n in flow["nodes"])

def test_evaluation_baseline_is_measured_not_fake():
    report=evaluate("baseline")
    assert report["cases"]==16
    assert 0<=report["category_accuracy"]<=1
    assert report["mode"]=="baseline"
    assert report["no_business_impact_claim"]

def test_preflight_passes_repo_template():
    assert preflight()==0

def test_persistence_survives_new_store_object(tmp_path):
    db=tmp_path/"file.sqlite3"
    store=Store(db);store.initialize()
    ticket=TicketIn(title="Tela do sistema indisponível",description="Tela fica preta ao acessar o sistema interno.")
    out=store.insert(ticket,baseline_classify(ticket))
    assert Store(db).get(out["id"])["title"]==ticket.title

def test_export_contains_only_operational_fields(tmp_path):
    db=Store(tmp_path/"test.sqlite3");db.initialize()
    ticket=TicketIn(title="Senha esquecida",description="Não lembro minha senha no ambiente de demonstração.", requester="Pessoa X")
    db.insert(ticket,baseline_classify(ticket))
    rows=db.rows_for_sheets()
    assert len(rows)==1 and "requester" not in rows[0] and "description" not in rows[0]
