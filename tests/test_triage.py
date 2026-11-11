import json
import httpx
import pytest
from pydantic import ValidationError
from app.schemas import TicketIn,Triage
from app.triage import OllamaTriage, baseline_classify,TriageUnavailable

SAMPLE=TicketIn(title="Acesso não funciona",description="Não consigo entrar no portal de teste.")
RESULT={"category":"acesso","priority":"media","team":"suporte_ti","summary":"Conta indisponível no portal", 
        "suggested_reply":"Recebemos seu relato e solicitamos o horário em que começou.",
        "rationale":"Solicitação informa dificuldade de login.","confidence":0.71}

def test_baseline_is_not_ai():
    res=baseline_classify(SAMPLE)
    assert res.mode=="baseline_demo"
    assert res.result.confidence==0
    assert "não IA" in res.result.rationale


def test_llm_strict_output_with_mock_transport():
    captured=[]
    def handler(request):
        payload=json.loads(request.content)
        captured.append(payload)
        return httpx.Response(200,json={"message":{"content":json.dumps(RESULT)}})
    client=httpx.Client(transport=httpx.MockTransport(handler))
    result=OllamaTriage(client=client)(SAMPLE)
    assert result.mode=="ollama"
    assert result.result.category=="acesso"
    assert captured[0]["format"]["type"]=="object"
    assert captured[0]["stream"] is False
    assert "https://" not in captured[0]["messages"][0]["content"]


def test_llm_invalid_json_and_extra_field_rejected():
    for content in ["not json", json.dumps({**RESULT,"injected":True}),json.dumps({**RESULT,"confidence":12})]:
        client=httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(200,json={"message":{"content":content}})))
        with pytest.raises(TriageUnavailable):OllamaTriage(client=client)(SAMPLE)


def test_http_503_is_safe_message():
    client=httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(503,text="SECRET SECRET")))
    with pytest.raises(TriageUnavailable) as exc:OllamaTriage(client=client)(SAMPLE)
    assert "SECRET" not in str(exc.value)


def test_model_schema_validation():
    with pytest.raises(ValidationError):Triage.model_validate({**RESULT,"category":"inventada"})
    with pytest.raises(ValidationError):TicketIn(title="x",description="short")
