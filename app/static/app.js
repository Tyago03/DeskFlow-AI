const $ = selector => document.querySelector(selector);
const safeText = (element, text) => { element.textContent = String(text ?? ""); return element; };
const CATEGORIES = {acesso:"Acesso",software:"Software",hardware:"Hardware",rede:"Rede",financeiro:"Financeiro",outros:"Outros"};
const PRIORITIES = {baixa:"Baixa",media:"Média",alta:"Alta",critica:"Crítica"};
const TEAMS = {suporte_ti:"Suporte de TI",infraestrutura:"Infraestrutura",financeiro:"Financeiro",atendimento_geral:"Atendimento geral"};
const STATUSES = {pending:"Aguardando",approved:"Aprovado",rejected:"Rejeitado"};
let tickets = [];
let active = null;
let toastHandle;
function toast(message, error = false) {const el=$("#toast");safeText(el,message);el.className="toast show"+(error?" error":"");clearTimeout(toastHandle);toastHandle=setTimeout(()=>el.className="toast",5000)}
async function api(path, options={}) {
  let response;
  try {response=await fetch(path,{cache:"no-store",...options,headers:{...(options.body?{"Content-Type":"application/json"}:{}),...(options.headers||{})}})}
  catch {throw Error("Não consegui conectar ao servidor DeskFlow.")}
  let data;
  try { data=await response.json() } catch { throw Error("Resposta inválida do servidor.") }
  if(!response.ok) throw Error(data.detail || "Falha inesperada.");
  return data;
}
function el(tag,cls,txt) {const node=document.createElement(tag); if(cls)node.className=cls; if(txt!==undefined)safeText(node,txt); return node}
function chip(text,cls) {return el("span","pill "+cls,text)}
function fmtDate(v){try{return new Date(v).toLocaleString("pt-BR",{day:"2-digit",month:"short",hour:"2-digit",minute:"2-digit"})}catch{return String(v)}}
function ticketRow(t){
  const tr=el("tr","ticket-row");tr.tabIndex=0;
  tr.setAttribute("aria-label", "Revisar solicitação "+t.title);
  const main=el("td");main.append(el("span","ticket-title",t.title),el("span","ticket-subtitle",t.id+" · "+fmtDate(t.created_at)));
  const c=el("td");c.append(chip(CATEGORIES[t.category]||t.category,"category-pill"));
  const p=el("td");p.append(chip(PRIORITIES[t.priority]||t.priority,"priority-"+t.priority));
  const s=el("td");s.append(chip(STATUSES[t.status]||t.status,"status-"+t.status));
  const src=el("td","source-label",t.source==="n8n"?"n8n":t.source==="demo"?"Demo":"Web");
  tr.append(main,c,p,s,src);
  tr.addEventListener("click",()=>openReview(t));
  tr.addEventListener("keydown",ev=>{if(ev.key==="Enter"||ev.key===" "){ev.preventDefault();openReview(t)}});
  return tr;
}
function renderTickets(){
  const status=$("#filter-status").value;
  const list=tickets.filter(t=>status==="all"||t.status===status);
  const body=$("#tickets-body");body.replaceChildren();
  if(!list.length){const row=el("tr");const cell=el("td","empty","Não há solicitações neste filtro.");cell.colSpan=5;row.append(cell);body.append(row);return;}
  for(const t of list)body.append(ticketRow(t));
}
function fillSelect(select,options,value){select.replaceChildren();for(const [id,label] of Object.entries(options)){const opt=el("option",null,label);opt.value=id;select.append(opt)}select.value=value;}
function openReview(t){
 active=t;
 safeText($("#dialog-title"),t.status==="pending"?"Revisar triagem":"Detalhes da triagem");
 safeText($("#dialog-subtitle"),t.status==="pending"?"A IA apenas sugeriu. Ajuste antes de aprovar.":"Registro já revisado; edições estão desativadas.");
 const summary=$("#review-summary");summary.replaceChildren();summary.append(el("h4",null,t.title),el("p",null,t.description),el("small",null,"Solicitante: "+t.requester+" · Origem: "+t.source));
 const reason=el("p","reason","Justificativa: "+t.rationale);summary.append(reason);
 summary.append(el("small",null,"Modo: "+(t.triage_mode==="ollama"?"Ollama (IA local)":"Baseline determinística")+" · Latência: "+t.latency_ms+" ms"));
 fillSelect($("#review-category"),CATEGORIES,t.final_category||t.category);
 fillSelect($("#review-priority"),PRIORITIES,t.final_priority||t.priority);
 fillSelect($("#review-team"),TEAMS,t.final_team||t.team);
 $("#review-reply").value=t.final_reply||t.suggested_reply;
 $("#review-note").value=t.reviewer_note||"";
 const pending=t.status==="pending";
 $("#review-form").querySelectorAll("input,textarea,select,button").forEach(input=>input.disabled=!pending);
 $("#review-form").querySelector(".dialog-actions").hidden=!pending;
 $("#review-modal").showModal();
}
async function submitReview(decision){if(!active)return;const id=active.id;
 const data={decision,category:$("#review-category").value,priority:$("#review-priority").value,team:$("#review-team").value,
 suggested_reply:$("#review-reply").value,reviewer_note:$("#review-note").value,reviewer:"Revisor local"};
 const buttons=[$("#approve-ticket"),$("#reject-ticket")];buttons.forEach(b=>b.disabled=true);
 try{await api("/api/tickets/"+encodeURIComponent(id)+"/review",{method:"POST",body:JSON.stringify(data)});$("#review-modal").close();toast(decision==="approve"?"Solicitação aprovada após revisão.":"Solicitação rejeitada.");await load();}
 catch(error){toast(error.message,true);buttons.forEach(b=>b.disabled=false)}
}
async function load(){
 const [list,metrics,system]=await Promise.all([api("/api/tickets"),api("/api/metrics"),api("/api/system")]);
 tickets=list.items;renderTickets();
 safeText($("#metric-total"),metrics.total);
 safeText($("#metric-pending"),metrics.pending);
 safeText($("#metric-override"),metrics.override_rate_percent===null?"—":metrics.override_rate_percent.toLocaleString("pt-BR")+"%");
 safeText($("#metric-latency"),metrics.average_llm_latency_ms===null?"—":(metrics.average_llm_latency_ms/1000).toLocaleString("pt-BR",{maximumFractionDigits:1})+" s");
 const st=$("#system-status");const demo=system.mode==="baseline_demo";
 st.className="system-pill"+(demo||system.ollama_online===false?" warning":"");
 safeText(st,demo?"Modo demonstração · sem IA":system.ollama_online?"● IA local ativa":"Ollama indisponível");
}
$("#refresh").addEventListener("click",()=>load().catch(e=>toast(e.message,true)));
$("#filter-status").addEventListener("change",renderTickets);
$("#new-ticket-form").addEventListener("submit",async ev=>{
 ev.preventDefault();const button=$("#submit-ticket");button.disabled=true;safeText(button,"Analisando…");
 const data={title:$("#request-title").value,description:$("#request-description").value,requester:$("#requester").value,source:"web"};
 try{await api("/api/tickets",{method:"POST",body:JSON.stringify(data)});$("#request-title").value="";$("#request-description").value="";toast("Triagem salva. Falta revisão humana.");await load();location.hash="requests"}
 catch(error){toast(error.message,true)}finally{button.disabled=false;safeText(button,"Analisar solicitação ✧")}
});
$("#review-form").addEventListener("submit",ev=>{ev.preventDefault();submitReview("approve")});
$("#reject-ticket").addEventListener("click",()=>submitReview("reject"));
load().catch(e=>toast(e.message,true));
