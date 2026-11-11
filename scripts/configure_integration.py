"""Salva credencial de n8n em .env local; nunca exibe ou publica o segredo."""
from pathlib import Path
import secrets
import os

ROOT=Path(__file__).resolve().parent.parent
ENV=ROOT/".env"

def main():
    if ENV.exists():
        print("Arquivo .env já existe. Não vou sobrescrever suas configurações.")
        print("Para regenerar, faça backup e remova .env manualmente.")
        return 0
    if input("Gerar chave local para integração n8n? [S/n] ").strip().lower() in ("n","nao","não"):
        return 0
    key=secrets.token_urlsafe(32)
    body=("# Configuração LOCAL: nunca commitar\n"
          "DESKFLOW_MODEL=qwen3:4b-instruct\n"
          "DESKFLOW_DEMO_MODE=0\n"
          f"DESKFLOW_INGEST_KEY={key}\n")
    fd=os.open(ENV,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(fd,"w",encoding="utf-8") as output:
        output.write(body)
    print("Credencial salva em .env (fora do Git).")
    print("Para configurar no n8n, abra o .env LOCALMENTE e copie apenas o valor DESKFLOW_INGEST_KEY")
    print("para uma credencial Header Auth com nome X-DeskFlow-Key.")
    return 0

if __name__=="__main__":raise SystemExit(main())
