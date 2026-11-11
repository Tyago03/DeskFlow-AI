"""SQLite: dados locais, auditoria e revisão humana, com consultas parametrizadas."""
from __future__ import annotations
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from typing import Any

from .schemas import TicketIn, ReviewIn
from .triage import TriageOutcome


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class TicketNotFound(Exception):
    pass

class ReviewConflict(Exception):
    pass

class Store:
    def __init__(self, path: Path):
        self.path = Path(path)

    @contextmanager
    def connection(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path, timeout=10, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA foreign_keys=ON")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize(self):
        with self.connection() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    requester TEXT NOT NULL,
                    source TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    category TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    team TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    suggested_reply TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    triage_mode TEXT NOT NULL,
                    latency_ms INTEGER NOT NULL,
                    final_category TEXT,
                    final_priority TEXT,
                    final_team TEXT,
                    final_reply TEXT,
                    reviewer TEXT,
                    reviewer_note TEXT,
                    reviewed_at TEXT
                );
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id TEXT NOT NULL REFERENCES tickets(id),
                    reviewed_at TEXT NOT NULL,
                    reviewer TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    original_category TEXT NOT NULL,
                    original_priority TEXT NOT NULL,
                    final_category TEXT NOT NULL,
                    final_priority TEXT NOT NULL,
                    note TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_tickets_created ON tickets(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_reviews_ticket ON reviews(ticket_id);
            """)

    @staticmethod
    def _as_dict(row: sqlite3.Row) -> dict[str, Any]:
        return dict(row)

    def insert(self, ticket: TicketIn, outcome: TriageOutcome) -> dict[str, Any]:
        row = {
            "id": uuid4().hex[:12], "created_at": utc_now(), "title": ticket.title,
            "description": ticket.description, "requester": ticket.requester,
            "source": ticket.source, "status": "pending",
            "category": outcome.result.category, "priority": outcome.result.priority,
            "team": outcome.result.team, "summary": outcome.result.summary,
            "suggested_reply": outcome.result.suggested_reply,
            "rationale": outcome.result.rationale, "confidence": outcome.result.confidence,
            "triage_mode": outcome.mode, "latency_ms": outcome.latency_ms,
        }
        columns = ", ".join(row)
        marks = ", ".join("?" for _ in row)
        with self.connection() as db:
            db.execute(f"INSERT INTO tickets ({columns}) VALUES ({marks})", tuple(row.values()))
        return self.get(row["id"])

    def get(self, ticket_id: str) -> dict[str, Any]:
        with self.connection() as db:
            row = db.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone()
            if row is None:
                raise TicketNotFound(ticket_id)
            return self._as_dict(row)

    def list(self, limit: int=150) -> list[dict[str, Any]]:
        with self.connection() as db:
            return [self._as_dict(r) for r in db.execute("SELECT * FROM tickets ORDER BY created_at DESC, rowid DESC LIMIT ?", (limit,))]

    def review(self, ticket_id: str, request: ReviewIn) -> dict[str, Any]:
        at=utc_now()
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone()
            if row is None:
                raise TicketNotFound(ticket_id)
            if row["status"] != "pending":
                raise ReviewConflict("Este registro já foi revisado; não será alterado duas vezes.")
            status = "approved" if request.decision=="approve" else "rejected"
            cursor=db.execute("""
              UPDATE tickets SET status=?, final_category=?, final_priority=?, final_team=?,
              final_reply=?, reviewer=?, reviewer_note=?, reviewed_at=? WHERE id=? AND status='pending'
            """, (status,request.category,request.priority,request.team,request.suggested_reply,
                  request.reviewer,request.reviewer_note,at,ticket_id))
            if cursor.rowcount!=1:
                raise ReviewConflict("Revisão concorrente; atualize a página.")
            db.execute("""
              INSERT INTO reviews(ticket_id,reviewed_at,reviewer,decision,
              original_category,original_priority,final_category,final_priority,note)
              VALUES (?,?,?,?,?,?,?,?,?)
            """, (ticket_id,at,request.reviewer,request.decision,row["category"],row["priority"],request.category,request.priority,request.reviewer_note))
        return self.get(ticket_id)

    def history(self, ticket_id: str) -> list[dict[str, Any]]:
        self.get(ticket_id)
        with self.connection() as db:
            return [self._as_dict(r) for r in db.execute("SELECT * FROM reviews WHERE ticket_id=? ORDER BY id",(ticket_id,))]

    def metrics(self) -> dict[str, Any]:
        rows=self.list(100000)
        reviewed=[r for r in rows if r["status"] in ("approved","rejected")]
        overrides=[r for r in reviewed if r["category"]!=r["final_category"] or r["priority"]!=r["final_priority"]]
        latencies=[r["latency_ms"] for r in rows if r["triage_mode"]=="ollama"]
        return {
          "total":len(rows),"pending":sum(r["status"]=="pending" for r in rows),
          "reviewed":len(reviewed),"approved":sum(r["status"]=="approved" for r in rows),
          "rejected":sum(r["status"]=="rejected" for r in rows),
          "override_rate_percent":round(100*len(overrides)/len(reviewed),1) if reviewed else None,
          "average_llm_latency_ms":round(sum(latencies)/len(latencies)) if latencies else None,
          "ai_triages":len(latencies),"baseline_triages":sum(r["triage_mode"]=="baseline_demo" for r in rows),
          "by_category":{cat:sum(r["category"]==cat for r in rows) for cat in ("acesso","software","hardware","rede","financeiro","outros")},
          "by_priority":{p:sum(r["priority"]==p for r in rows) for p in ("baixa","media","alta","critica")},
        }

    def rows_for_sheets(self) -> list[dict[str, Any]]:
        # O endpoint de planilha exporta SOMENTE dados operacionais sem descrição ou solicitante.
        rows=self.list(100000)
        return [{
          "ticket_id":r["id"], "created_at":r["created_at"],"source":r["source"],
          "status":r["status"],"category":r["final_category"] or r["category"],
          "priority":r["final_priority"] or r["priority"],
          "team":r["final_team"] or r["team"],"triage_mode":r["triage_mode"],
          "latency_ms":r["latency_ms"],
          "review_changed":bool(r["final_category"] and (r["category"]!=r["final_category"] or r["priority"]!=r["final_priority"])),
        } for r in rows]
