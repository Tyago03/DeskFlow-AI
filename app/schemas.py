from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

Category = Literal["acesso", "software", "hardware", "rede", "financeiro", "outros"]
Priority = Literal["baixa", "media", "alta", "critica"]
Team = Literal["suporte_ti", "infraestrutura", "financeiro", "atendimento_geral"]

class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

class TicketIn(Strict):
    title: str = Field(min_length=5, max_length=150)
    description: str = Field(min_length=12, max_length=3500)
    requester: str = Field(default="Usuário de demonstração", min_length=2, max_length=100)
    source: Literal["web", "n8n", "demo"] = "web"

    @field_validator("title", "description", "requester")
    @classmethod
    def clean_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Campo não pode estar vazio")
        # Exclui caracteres de controle, mas preserva quebras de linha no campo descrição.
        return "".join(c for c in value if c == "\n" or (ord(c) >= 32 and ord(c) != 127)).strip()

class Triage(Strict):
    category: Category
    priority: Priority
    team: Team
    summary: str = Field(min_length=4, max_length=260)
    suggested_reply: str = Field(min_length=10, max_length=1000)
    rationale: str = Field(min_length=4, max_length=500)
    confidence: float = Field(ge=0, le=1)

    @field_validator("summary", "suggested_reply", "rationale")
    @classmethod
    def nonblank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Texto não pode estar vazio")
        return value.strip()

class ReviewIn(Strict):
    decision: Literal["approve", "reject"]
    category: Category
    priority: Priority
    team: Team
    suggested_reply: str = Field(min_length=10, max_length=1000)
    reviewer_note: str = Field(default="", max_length=500)
    reviewer: str = Field(default="Revisor local", min_length=2, max_length=80)

