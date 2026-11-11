"""Verificação preventiva de material para publicação. Heurística, não auditoria completa."""
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parent.parent
FORBIDDEN=(".env","data/",".venv/","reports/","evaluation/results/","__pycache__/",".git/")
PATTERNS=[
 re.compile(r"\bgh[pousr]_[A-Za-z0-9]{25,}\b"),
 re.compile(r"\bgithub_pat_[A-Za-z0-9_]{25,}\b"),
 re.compile(r"\bsk-[A-Za-z0-9_-]{30,}\b"),
 re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
 re.compile(r"(?i)DESKFLOW_INGEST_KEY\s*=\s*[A-Za-z0-9_-]{24,}"),
]

def files_to_check():
    p=subprocess.run(["git","ls-files","--cached","-z"],cwd=ROOT,capture_output=True)
    if p.returncode==0 and p.stdout:
        return [Path(s.decode("utf-8")) for s in p.stdout.split(b"\0") if s]
    ignored={".git",".venv","venv","data","reports","__pycache__",".pytest_cache"}
    return [f.relative_to(ROOT) for f in ROOT.rglob("*")
            if f.is_file()
            and not any(part in ignored for part in f.relative_to(ROOT).parts)
            and f.relative_to(ROOT).parts[:2] != ("evaluation", "results")]

def main():
    issues=[]
    for rel in files_to_check():
        s=rel.as_posix()
        if (s != ".env.example" and any(s==p or s.startswith(p) for p in FORBIDDEN)): issues.append(s+": arquivo local ou secreto");continue
        if rel.suffix.lower() in {".db",".sqlite3",".key",".pem"}: issues.append(s+": extensão sensível");continue
        file=ROOT/rel
        if not file.exists(): continue
        if file.stat().st_size>2_000_000: issues.append(s+": arquivo muito grande para revisão");continue
        if file.suffix.lower() in {".py",".json",".js",".md",".yml",".yaml",".txt",".bat",".html",".css",".toml",".example"}:
            content=file.read_text(encoding="utf-8",errors="replace")
            if any(pattern.search(content) for pattern in PATTERNS):issues.append(s+": padrão de segredo detectado")
    if issues:
        print("BLOQUEADO. Revise:")
        for issue in issues:print("-",issue)
        return 1
    print("Verificação heurística sem alertas nos arquivos selecionados. Isto não substitui revisão humana.")
    return 0

if __name__=="__main__":sys.exit(main())
