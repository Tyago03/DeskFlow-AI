"""Avaliação de triagem em dados sintéticos: não afirma impacto em produção."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics

from app.schemas import TicketIn
from app.triage import baseline_classify, OllamaTriage, TriageUnavailable

ROOT=Path(__file__).resolve().parent.parent
DATASET=ROOT/"datasets"/"holdout.jsonl"
OUT=ROOT/"evaluation"/"results"

def evaluate(mode: str = "baseline") -> dict:
    classifier=baseline_classify if mode=="baseline" else OllamaTriage()
    lines=[json.loads(line) for line in DATASET.read_text(encoding="utf-8").splitlines() if line.strip()]
    reports=[]
    for item in lines:
        sample=TicketIn(title=item["title"],description=item["description"],requester="Avaliação sintética",source="demo")
        try:
            outcome=classifier(sample)
            correct_cat=(outcome.result.category==item["expected_category"])
            correct_priority=(outcome.result.priority==item["expected_priority"])
            reports.append({"id":item["id"],"category_expected":item["expected_category"],"category_predicted":outcome.result.category,
              "priority_expected":item["expected_priority"],"priority_predicted":outcome.result.priority,
              "category_correct":correct_cat,"priority_correct":correct_priority,
              "both_correct":correct_cat and correct_priority,"latency_ms":outcome.latency_ms})
        except TriageUnavailable:
            reports.append({"id":item["id"],"error":"LLM indisponível / retorno inválido","category_correct":False,
                            "priority_correct":False,"both_correct":False,"latency_ms":None})
    n=len(reports)
    elapsed=[r["latency_ms"] for r in reports if isinstance(r.get("latency_ms"),int)]
    return {
      "mode":mode,"dataset":"dados sintéticos, rótulos humanos preparados para exercício",
      "executed_at":datetime.now(timezone.utc).isoformat(timespec="seconds"),
      "cases":n,
      "category_accuracy":round(sum(r["category_correct"] for r in reports)/n,3),
      "priority_accuracy":round(sum(r["priority_correct"] for r in reports)/n,3),
      "joint_accuracy":round(sum(r["both_correct"] for r in reports)/n,3),
      "mean_latency_ms":round(statistics.mean(elapsed)) if elapsed else None,
      "no_business_impact_claim":True,
      "results":reports,
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=["baseline","ollama"],default="baseline")
    mode=parser.parse_args().mode
    result=evaluate(mode)
    OUT.mkdir(parents=True,exist_ok=True)
    stem="triagem_"+mode+"_"+datetime.now().strftime("%Y%m%d_%H%M%S")
    location=OUT/(stem+".json")
    location.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Modo: {mode} | Casos: {result['cases']}")
    print(f"Acerto categoria: {result['category_accuracy']:.1%} | prioridade: {result['priority_accuracy']:.1%} | conjunto: {result['joint_accuracy']:.1%}")
    print("Esse resultado mede um conjunto sintético limitado, não economia de tempo nem produtividade em empresa.")
    print("Relatório salvo em:",location)
    return 0 if all("error" not in r for r in result["results"]) else 2

if __name__=="__main__":raise SystemExit(main())
