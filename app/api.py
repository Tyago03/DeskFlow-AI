"""API local: sugestões de IA são sempre revisadas por pessoa."""
from __future__ import annotations
from contextlib import asynccontextmanager
import csv
import hmac
import io
from pathlib import Path
from typing import Callable

import httpx
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .config import DB_PATH, DEMO_MODE, INGEST_KEY, MODEL, OLLAMA_URL
from .schemas import ReviewIn, TicketIn
from .store import Store, TicketNotFound, ReviewConflict
from .triage import OllamaTriage, TriageUnavailable, baseline_classify, TriageOutcome

STATIC = Path(__file__).resolve().parent / "static"


def create_app(*, store: Store | None = None, classifier: Callable[[TicketIn], TriageOutcome] | None = None,
               integration_key: str | None = None, demo: bool | None = None) -> FastAPI:
    db = store or Store(DB_PATH)
    demo_mode = DEMO_MODE if demo is None else demo
    triage = classifier if classifier is not None else (baseline_classify if demo_mode else OllamaTriage())
    key = INGEST_KEY if integration_key is None else integration_key

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        db.initialize()
        yield

    app = FastAPI(title="DeskFlow AI", version="1.0.0", lifespan=lifespan, docs_url=None, redoc_url=None)
    app.state.db=db
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "host.docker.internal", "testserver"])

    @app.middleware("http")
    async def safety(request: Request, call_next):
        if request.method in {"POST", "PUT", "PATCH"}:
            if request.headers.get("content-type", "").split(";")[0].strip().lower() != "application/json":
                return JSONResponse({"detail":"Use Content-Type: application/json"},status_code=415)
            if len(await request.body())>8192:
                return JSONResponse({"detail":"Solicitação acima do tamanho permitido"},status_code=413)
        # Defesa básica contra submissões de origem web cruzada; autenticação de n8n é separada.
        origin=request.headers.get("origin")
        if origin:
            from urllib.parse import urlsplit
            parts=urlsplit(origin)
            if parts.netloc != request.headers.get("host") or parts.scheme != request.url.scheme:
                return JSONResponse({"detail":"Origem bloqueada"},status_code=403)
        response=await call_next(request)
        response.headers["Cache-Control"]="no-store"
        response.headers["X-Content-Type-Options"]="nosniff"
        response.headers["X-Frame-Options"]="DENY"
        response.headers["Referrer-Policy"]="no-referrer"
        response.headers["Content-Security-Policy"]=("default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
                                                    "connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
        return response

    @app.exception_handler(TriageUnavailable)
    async def model_error(request: Request, exc: TriageUnavailable):
        return JSONResponse({"detail":str(exc)},status_code=503)

    @app.exception_handler(TicketNotFound)
    async def not_found(request: Request, exc: TicketNotFound):
        return JSONResponse({"detail":"Solicitação não encontrada"},status_code=404)

    @app.exception_handler(ReviewConflict)
    async def conflict(request: Request, exc: ReviewConflict):
        return JSONResponse({"detail":str(exc)},status_code=409)

    @app.exception_handler(RequestValidationError)
    async def validation(request: Request, exc: RequestValidationError):
        return JSONResponse({"detail":"Campos inválidos ou incompletos. Confira os limites e formatos."},status_code=422)

    def require_key(value: str | None):
        if not key:
            raise HTTPException(503,"Integração desativada: configure DESKFLOW_INGEST_KEY localmente.")
        if not value or not hmac.compare_digest(key,value):
            raise HTTPException(403,"Credencial de integração ausente ou inválida.")

    @app.get("/")
    def home():
        return FileResponse(STATIC/"index.html")

    @app.get("/api/health")
    def health():
        return {"status":"ok","version":"1.0.0","triage_mode":"baseline_demo" if demo_mode else "ollama","model":MODEL}

    @app.get("/api/system")
    def system():
        if demo_mode:
            return {"mode":"baseline_demo","model":None,"ollama_online":None,"integration_ready":bool(key)}
        try:
            response=httpx.get(OLLAMA_URL+"/api/tags",timeout=2)
            response.raise_for_status()
            installed=any(m.get("name")==MODEL or m.get("model")==MODEL for m in response.json().get("models", []))
        except (httpx.HTTPError, ValueError, TypeError, AttributeError):
            installed=False
        return {"mode":"ollama","model":MODEL,"ollama_online":installed,"integration_ready":bool(key)}

    @app.get("/api/tickets")
    def tickets():
        return {"items":db.list()}

    @app.post("/api/tickets",status_code=201)
    def create_ticket(ticket: TicketIn):
        return db.insert(ticket,triage(ticket))

    @app.get("/api/tickets/{ticket_id}")
    def get_ticket(ticket_id: str):
        return {"ticket":db.get(ticket_id),"history":db.history(ticket_id)}

    @app.post("/api/tickets/{ticket_id}/review")
    def review_ticket(ticket_id: str, decision: ReviewIn):
        return db.review(ticket_id,decision)

    @app.get("/api/metrics")
    def metrics():
        return db.metrics()

    @app.get("/api/export.csv")
    def export_csv():
        # Previne execução de fórmula em planilhas CSV.
        def safe_cell(value):
            s=str(value if value is not None else "")
            if s.lstrip().startswith(("=","+","-","@")) or s.startswith(("\t","\r","\n")):
                return "'"+s
            return s
        rows=db.list(100000)
        fields=["id","created_at","title","source","status","category","priority","team","triage_mode","latency_ms","final_category","final_priority","reviewed_at"]
        output=io.StringIO()
        writer=csv.writer(output)
        writer.writerow(fields)
        for row in rows:
            writer.writerow([safe_cell(row.get(f)) for f in fields])
        return Response("\ufeff"+output.getvalue(),media_type="text/csv; charset=utf-8",
                        headers={"Content-Disposition":"attachment; filename=deskflow_tickets.csv"})

    @app.post("/api/integrations/tickets",status_code=201)
    def n8n_ingest(ticket: TicketIn, x_deskflow_key: str | None = Header(default=None)):
        require_key(x_deskflow_key)
        return db.insert(ticket.model_copy(update={"source":"n8n"}),triage(ticket))

    @app.get("/api/integrations/sheets_rows")
    def sheets_rows(x_deskflow_key: str | None = Header(default=None)):
        require_key(x_deskflow_key)
        return {"rows":db.rows_for_sheets()}

    app.mount("/static",StaticFiles(directory=STATIC),name="static")
    return app

app = create_app()
