import pytest
from fastapi.testclient import TestClient
from app.api import create_app
from app.store import Store
from app.triage import baseline_classify

@pytest.fixture
def app_client(tmp_path):
    store=Store(tmp_path/"test.sqlite3")
    app=create_app(store=store,classifier=baseline_classify,integration_key="a"*32,demo=True)
    with TestClient(app) as client:
        yield client

@pytest.fixture
def sample():
    return {"title":"Não consigo entrar no sistema","description":"Minha conta está bloqueada desde o início do expediente.","requester":"Usuário fictício"}
