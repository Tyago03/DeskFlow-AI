"""Popula exemplos fictícios pelo baseline; não simula uso real do Qwen."""
from app.config import DB_PATH
from app.schemas import TicketIn
from app.store import Store
from app.triage import baseline_classify

CASES=[
 ("Não consigo acessar a intranet", "Minha conta aparece bloqueada desde hoje e preciso acessar documentos.","Camila (fictícia)"),
 ("Impressora parou", "A impressora do segundo andar apresenta falha de papel constante.","Carlos (fictício)"),
 ("VPN muito lenta", "A conexão VPN cai várias vezes durante a reunião remota.","Lucas (fictício)"),
 ("Dúvida sobre reembolso", "Tenho uma dúvida sobre o reembolso da viagem do mês passado.","Fernanda (fictícia)"),
 ("Instalação de aplicativo", "Preciso instalar um programa de edição no notebook novo.","André (fictício)"),
]

def main():
    store=Store(DB_PATH);store.initialize()
    if store.list():
        print("O banco já contém solicitações. Não vou duplicar dados.");return
    for title,description,requester in CASES:
        ticket=TicketIn(title=title,description=description,requester=requester,source="demo")
        store.insert(ticket,baseline_classify(ticket))
    print("5 solicitações FICTÍCIAS adicionadas; triagem demonstrativa por regras (não IA).")

if __name__=="__main__":main()
