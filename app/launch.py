"""Iniciador local com navegador; sem abrir a aplicação na internet."""
import os
import socket
import threading
import time
import urllib.request
import webbrowser
import uvicorn


def main():
    host="0.0.0.0" if os.getenv("DESKFLOW_ALLOW_DOCKER", "0")=="1" else "127.0.0.1"
    port=int(os.getenv("DESKFLOW_PORT","8000"))
    if port<1024 or port>65535:
        raise SystemExit("Porta inválida")
    with socket.socket() as check:
        try:
            check.bind(("127.0.0.1",port))
        except OSError:
            raise SystemExit(f"A porta {port} está ocupada.")
    url=f"http://127.0.0.1:{port}"
    running=threading.Event()
    def opener():
        for _ in range(60):
            if running.is_set(): return
            try:
                with urllib.request.urlopen(url+"/api/health",timeout=1) as r:
                    if r.status==200:
                        webbrowser.open(url)
                        return
            except OSError:
                pass
            time.sleep(0.3)
    threading.Thread(target=opener,daemon=True).start()
    print("DeskFlow AI: "+url)
    if host=="0.0.0.0":
        print("ATENÇÃO: escuta em interfaces de rede para receber n8n. Restrinja o firewall e não exponha a internet.")
    print("Pressione Ctrl+C para parar.")
    try:
        uvicorn.run("app.api:app",host=host,port=port,log_level="warning")
    finally:
        running.set()

if __name__=="__main__":
    main()
