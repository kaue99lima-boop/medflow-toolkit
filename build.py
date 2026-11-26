import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'data_generator'))
from generate_data import gen_all
HERE = os.path.dirname(os.path.abspath(__file__))
DEMO = gen_all()

CSS = r'''
:root{--ink:#1f2a37;--mut:#6b7280;--line:#e5e7eb;--bg:#f6f7f9;--pri:#0f766e;--pri2:#ccfbf1;--red:#b91c1c;--yel:#b45309;--grn:#15803d}
*{box-sizing:border-box}body{margin:0;font:14px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:var(--ink);background:var(--bg)}
header{background:#fff;border-bottom:1px solid var(--line);padding:14px 24px;display:flex;align-items:center;gap:14px;flex-wrap:wrap}
header h1{font-size:18px;margin:0}header .tag{background:var(--pri2);color:var(--pri);border-radius:99px;padding:2px 10px;font-size:12px;font-weight:600}
header a{margin-left:auto;color:var(--pri);text-decoration:none;font-size:13px}
main{max-width:1180px;margin:18px auto;padding:0 18px}
.card{background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin-bottom:14px}
.card h2{font-size:14px;margin:0 0 10px}
.row{display:flex;gap:12px;flex-wrap:wrap;align-items:end}.row label{display:flex;flex-direction:column;font-size:12px;color:var(--mut);gap:3px}
input,select,button{font:inherit;padding:6px 9px;border:1px solid #cbd5e1;border-radius:7px;background:#fff}
button{cursor:pointer;background:var(--pri);color:#fff;border-color:var(--pri);font-weight:600}button.sec{background:#fff;color:var(--pri)}button.sm{padding:2px 8px;font-size:12px}
button.dng{background:#fff;color:var(--red);border-color:#fca5a5}
table{border-collapse:collapse;width:100%;font-size:13px}th,td{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left}th{background:#f1f5f9;font-size:12px;color:#475569}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}tr.tot td{font-weight:700;background:#f8fafc}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:14px}.kpi{background:#fff;border:1px solid var(--line);border-radius:10px;padding:10px 12px}
.kpi b{display:block;font-size:20px}.kpi span{font-size:12px;color:var(--mut)}
.pill{padding:1px 8px;border-radius:99px;font-size:11px;font-weight:700}.p-red{background:#fee2e2;color:var(--red)}.p-yel{background:#fef3c7;color:var(--yel)}.p-grn{background:#dcfce7;color:var(--grn)}.p-gry{background:#e5e7eb;color:#374151}
.tabs{display:flex;gap:6px;margin-bottom:12px}.tabs button{background:#fff;color:var(--ink);border-color:var(--line)}.tabs button.on{background:var(--pri);color:#fff;border-color:var(--pri)}
.hint{color:var(--mut);font-size:12px}.hide{display:none}.empty{padding:30px;text-align:center;color:var(--mut)}
.sheet{background:#fff;border:1px solid var(--line);border-radius:10px;padding:22px 26px}.sheet h3{margin:0 0 2px;font-size:18px}
@media print{body{background:#fff}header,.noprint,.card.noprint{display:none!important}main{margin:0;max-width:none}.sheet{border:0;padding:0}}
'''

COMMON = r'''
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const money=n=>'$'+Number(n||0).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
const money0=n=>'$'+Math.round(Number(n||0)).toLocaleString('en-US');
const num=v=>{const x=parseFloat(v);return isNaN(x)?0:x};
const brDate=s=>{if(!s)return'';const [y,m,d]=s.slice(0,10).split('-');return d+'/'+m+'/'+y};
const today=()=>new Date().toISOString().slice(0,10);
function parseCSV(t){const rows=[];let row=[],f='',q=false;for(let i=0;i<t.length;i++){const c=t[i];if(q){if(c=='"'){if(t[i+1]=='"'){f+='"';i++}else q=false}else f+=c}else if(c=='"')q=true;else if(c==','){row.push(f);f=''}else if(c=='\n'||c=='\r'){if(c=='\r'&&t[i+1]=='\n')i++;row.push(f);f='';rows.push(row);row=[]}else f+=c}
if(f!==''||row.length){row.push(f);rows.push(row)}const h=rows.shift().map(s=>s.trim());return rows.filter(r=>r.length>1||r[0]).map(r=>Object.fromEntries(h.map((k,i)=>[k,(r[i]??'').trim()])))}
function toCSV(cols,rows){const q=v=>{v=String(v??'');return /[",\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v};return [cols.join(',')].concat(rows.map(r=>cols.map(c=>q(r[c])).join(','))).join('\n')}
function download(name,text){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type:'text/csv;charset=utf-8'}));a.download=name;a.click()}
const store={get:(k,d)=>{try{return JSON.parse(localStorage.getItem(k))??d}catch(e){return d}},set:(k,v)=>{try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}};
/* Carregador: botão de demonstração + upload de CSV por arquivo */
function loader(el,specs,onReady){
  const DATA={};
  el.innerHTML='<h2>1. Dados</h2><div class="row"><button id="ld-demo">Usar dados de demonstração</button>'+specs.map(s=>'<label>'+esc(s.label)+' ('+s.file+')<input type="file" accept=".csv" data-k="'+s.key+'"></label>').join('')+'</div><p class="hint" id="ld-msg">Todos os dados de demonstração são fictícios. Para usar os seus, carregue CSVs com as colunas descritas no README.</p>';
  const check=()=>{if(specs.every(s=>DATA[s.key])){$('#ld-msg',el).textContent='Dados carregados: '+specs.map(s=>s.key+' ('+DATA[s.key].length+' linhas)').join(' · ');onReady(DATA)}};
  $('#ld-demo',el).onclick=()=>{specs.forEach(s=>DATA[s.key]=parseCSV(DEMO[s.file]));check()};
  $$('input[type=file]',el).forEach(i=>i.onchange=()=>{const f=i.files[0];if(!f)return;const r=new FileReader();r.onload=()=>{DATA[i.dataset.k]=parseCSV(r.result);check()};r.readAsText(f)});
}
function bars(vals,labels,o={}){const W=o.w||640,H=o.h||200,p=28,n=vals.length,mx=Math.max(...vals.map(Math.abs),1),bw=(W-2*p)/n,zero=H-p-(Math.min(0,...vals)<0?(-Math.min(...vals)/ (mx*2))*(H-2*p):0);
 let s='<svg viewBox="0 0 '+W+' '+H+'" width="100%" style="max-width:'+W+'px">';const hasNeg=Math.min(...vals)<0,base=hasNeg?H/2:H-p,sc=(hasNeg?(H/2-p):(H-2*p))/mx;
 vals.forEach((v,i)=>{const h=Math.abs(v)*sc,x=p+i*bw+bw*.15,y=v>=0?base-h:base,c=(o.colors&&o.colors[i])||(v<0?'#b91c1c':'#0f766e');
 s+='<rect x="'+x+'" y="'+y+'" width="'+bw*.7+'" height="'+Math.max(h,1)+'" rx="3" fill="'+c+'"/><text x="'+(x+bw*.35)+'" y="'+(v>=0?y-4:y+h+11)+'" font-size="10" text-anchor="middle" fill="#374151">'+(o.fmt?o.fmt(v):Math.round(v))+'</text><text x="'+(x+bw*.35)+'" y="'+(H-8)+'" font-size="10" text-anchor="middle" fill="#6b7280">'+esc(labels[i])+'</text>'});
 return s+'<line x1="'+p+'" x2="'+(W-p)+'" y1="'+base+'" y2="'+base+'" stroke="#cbd5e1"/></svg>'}
'''

def page(title, sub, body, js, files):
    demo = {f: DEMO[f] for f in files}
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · MedFlow Toolkit</title><style>{CSS}</style></head><body>
<header><h1>{title}</h1><span class="tag">dados fictícios</span><span class="hint">{sub}</span><a href="../index.html">← MedFlow Toolkit</a></header><main>{body}</main>
<script>const DEMO={json.dumps(demo, ensure_ascii=False)};{COMMON}{js}</script></body></html>'''

# ---------------- 1. Estado de conta
estado_body = '''<div class="card noprint" id="ld"></div><div class="card noprint hide" id="ctl"><h2>2. Filtros</h2><div class="row"><label>Pagador<select id="payer"></select></label><label>De<input type="date" id="d1"></label><label>Até<input type="date" id="d2"></label><label><span>&nbsp;</span><span><input type="checkbox" id="open" checked> somente não pagas</span></label>
<button id="print">Imprimir / PDF</button><button class="sec" id="csv">Baixar CSV</button><button class="sec" id="save">Salvar no histórico</button></div></div>
<div id="out"></div><div class="card noprint hide" id="histc"><h2>Histórico de estados emitidos (neste navegador)</h2><div id="hist"></div></div>'''
estado_js = r'''
let R=[],ref='';
loader($('#ld'),[{key:'billing',file:'billing.csv',label:'Contas'}],D=>{R=D.billing.map(r=>({...r,amount:num(r.amount)}));ref=R.map(r=>r.service_date).sort().pop();
 const payers=[...new Set(R.map(r=>r.payer))].sort();$('#payer').innerHTML=payers.map(p=>'<option>'+esc(p)+'</option>').join('');
 $('#d1').value=R.map(r=>r.service_date).sort()[0];$('#d2').value=ref;$('#ctl').classList.remove('hide');$('#histc').classList.remove('hide');render();hist()});
function sel(){return R.filter(r=>r.payer==$('#payer').value&&r.service_date>=$('#d1').value&&r.service_date<=$('#d2').value&&(!$('#open').checked||r.status!='paga')).sort((a,b)=>a.service_date<b.service_date?-1:1)}
function render(){const L=sel(),tot=L.reduce((s,r)=>s+r.amount,0);
 const ag=[['0–30 dias',0,30],['31–60 dias',31,60],['61–90 dias',61,90],['> 90 dias',91,1e9]].map(([n,a,b])=>{const x=L.filter(r=>{const d=(new Date(ref)-new Date(r.service_date))/864e5;return d>=a&&d<=b});return[n,x.length,x.reduce((s,r)=>s+r.amount,0)]});
 const byLine={};L.forEach(r=>byLine[r.service_line]=(byLine[r.service_line]||0)+r.amount);
 $('#out').innerHTML=L.length?`<div class="sheet"><h3>Estado de conta</h3><div class="hint">${esc($('#payer').value)} · período ${brDate($('#d1').value)} a ${brDate($('#d2').value)} · emitido em ${brDate(today())} · Hospital Demo</div>
 <div class="kpis" style="margin-top:12px"><div class="kpi"><b>${L.length}</b><span>contas</span></div><div class="kpi"><b>${money0(tot)}</b><span>valor total</span></div><div class="kpi"><b>${money0(L.filter(r=>r.status=='rejeitada').reduce((s,r)=>s+r.amount,0))}</b><span>rejeitadas</span></div></div>
 <table><thead><tr><th>Conta</th><th>Data</th><th>Paciente</th><th>Serviço</th><th>Situação</th><th class="n">Valor</th></tr></thead><tbody>${L.map(r=>`<tr><td>${esc(r.account_id)}</td><td>${brDate(r.service_date)}</td><td>${esc(r.patient_code)}</td><td>${esc(r.service_line)}</td><td>${esc(r.status)}</td><td class="n">${money(r.amount)}</td></tr>`).join('')}<tr class="tot"><td colspan="5">Total</td><td class="n">${money(tot)}</td></tr></tbody></table>
 <h3 style="font-size:14px;margin-top:18px">Antiguidade (referência ${brDate(ref)})</h3><table style="max-width:480px"><thead><tr><th>Faixa</th><th class="n">Contas</th><th class="n">Valor</th></tr></thead><tbody>${ag.map(a=>`<tr><td>${a[0]}</td><td class="n">${a[1]}</td><td class="n">${money(a[2])}</td></tr>`).join('')}</tbody></table>
 <h3 style="font-size:14px;margin-top:18px">Por serviço</h3><table style="max-width:480px"><tbody>${Object.entries(byLine).map(([k,v])=>`<tr><td>${esc(k)}</td><td class="n">${money(v)}</td></tr>`).join('')}</tbody></table></div>`:'<div class="card empty">Nenhuma conta para os filtros escolhidos.</div>'}
['payer','d1','d2','open'].forEach(i=>$('#'+i).addEventListener('change',render));
$('#print').onclick=()=>window.print();
$('#csv').onclick=()=>download('estado_de_conta_'+$('#payer').value.replace(/\s+/g,'_')+'.csv',toCSV(['account_id','patient_code','service_date','payer','service_line','amount','status'],sel()));
function hist(){const h=store.get('mf_estado',[]);$('#hist').innerHTML=h.length?'<table><thead><tr><th>Emitido</th><th>Pagador</th><th>Período</th><th class="n">Contas</th><th class="n">Total</th><th></th></tr></thead><tbody>'+h.map((x,i)=>`<tr><td>${brDate(x.at)}</td><td>${esc(x.payer)}</td><td>${brDate(x.d1)}–${brDate(x.d2)}</td><td class="n">${x.n}</td><td class="n">${money(x.total)}</td><td><button class="dng sm" data-i="${i}">remover</button></td></tr>`).join('')+'</tbody></table>':'<div class="hint">Nada salvo ainda.</div>';$$('#hist button').forEach(b=>b.onclick=()=>{const h=store.get('mf_estado',[]);h.splice(+b.dataset.i,1);store.set('mf_estado',h);hist()})}
$('#save').onclick=()=>{const L=sel(),h=store.get('mf_estado',[]);h.unshift({at:today(),payer:$('#payer').value,d1:$('#d1').value,d2:$('#d2').value,n:L.length,total:L.reduce((s,r)=>s+r.amount,0)});store.set('mf_estado',h.slice(0,30));hist()};
'''

# ---------------- 2. Orçamento
orc_body = '''<div class="card noprint" id="ld"></div><div class="card noprint hide" id="ctl"><h2>2. Montar orçamento</h2><div class="row"><label>Paciente (código)<input id="pat" value="P0000"></label><label>Médico<select id="doc"></select></label><label>Pacote<select id="pkg"></select></label><label>Margem sobre o custo (%)<input id="mg" type="number" value="35" style="width:90px"></label><label>Desconto (%)<input id="ds" type="number" value="0" style="width:80px"></label><label>Validade (dias)<input id="va" type="number" value="15" style="width:80px"></label></div>
<div class="row" style="margin-top:10px"><label>Adicionar item<select id="add"></select></label><button class="sec" id="addb">Adicionar</button><button id="print">Emitir PDF</button><button class="sec" id="save">Salvar no histórico</button></div></div>
<div id="out"></div><div class="card noprint hide" id="histc"><h2>Histórico de orçamentos (neste navegador)</h2><div id="hist"></div></div>'''
orc_js = r'''
let CAT={},PK={},DOCS=[],LINES=[];
loader($('#ld'),[{key:'catalog',file:'catalog.csv',label:'Catálogo'},{key:'packages',file:'packages.csv',label:'Pacotes'},{key:'doctors',file:'doctors.csv',label:'Médicos'}],D=>{
 CAT={};D.catalog.forEach(r=>CAT[r.item_id]={...r,unit_cost:num(r.unit_cost)});PK={};D.packages.forEach(r=>{(PK[r.package_name]=PK[r.package_name]||[]).push({item_id:r.item_id,qty:num(r.qty)})});DOCS=D.doctors;
 $('#doc').innerHTML=DOCS.map(d=>'<option>'+esc(d.doctor_name)+'</option>').join('');$('#pkg').innerHTML=Object.keys(PK).map(k=>'<option>'+esc(k)+'</option>').join('');
 $('#add').innerHTML=Object.values(CAT).map(c=>`<option value="${c.item_id}">${esc(c.category)} · ${esc(c.description)}</option>`).join('');
 $('#ctl').classList.remove('hide');$('#histc').classList.remove('hide');setPkg();hist()});
function setPkg(){LINES=(PK[$('#pkg').value]||[]).map(l=>({...l}));render()}
$('#pkg').onchange=setPkg;['pat','doc','mg','ds','va'].forEach(i=>$('#'+i).addEventListener('input',render));
$('#addb').onclick=()=>{const id=$('#add').value,l=LINES.find(x=>x.item_id==id);l?l.qty++:LINES.push({item_id:id,qty:1});render()};
function calc(){const m=num($('#mg').value)/100,d=num($('#ds').value)/100;const rows=LINES.map(l=>{const c=CAT[l.item_id],cost=c.unit_cost*l.qty,price=cost*(1+m);return{...l,c,cost,price}});const cost=rows.reduce((s,r)=>s+r.cost,0),gross=rows.reduce((s,r)=>s+r.price,0),total=gross*(1-d);return{rows,cost,gross,total,margin:total?(total-cost)/total:0}}
function render(){if(!LINES)return;const q=calc();
 $('#out').innerHTML=`<div class="sheet"><h3>Orçamento cirúrgico · ${esc($('#pkg').value)}</h3><div class="hint">Hospital Demo · paciente ${esc($('#pat').value)} · ${esc($('#doc').value)} · emitido em ${brDate(today())} · válido por ${esc($('#va').value)} dias</div>
 <table style="margin-top:12px"><thead><tr><th>Categoria</th><th>Item</th><th class="n">Qtd</th><th class="n noprint">Custo</th><th class="n">Valor</th><th class="noprint"></th></tr></thead><tbody>${q.rows.map((r,i)=>`<tr><td>${esc(r.c.category)}</td><td>${esc(r.c.description)}</td><td class="n"><input class="noprint" type="number" min="0" value="${r.qty}" data-i="${i}" style="width:60px"><span class="hide">${r.qty}</span></td><td class="n noprint">${money(r.cost)}</td><td class="n">${money(r.price)}</td><td class="noprint"><button class="dng sm" data-r="${i}">×</button></td></tr>`).join('')}
 <tr class="tot"><td colspan="4" class="noprint"></td><td>Subtotal</td><td class="n">${money(q.gross)}</td></tr><tr><td colspan="4" class="noprint"></td><td>Desconto ${num($('#ds').value)}%</td><td class="n">−${money(q.gross-q.total)}</td></tr><tr class="tot"><td colspan="4" class="noprint"></td><td>TOTAL</td><td class="n">${money(q.total)}</td></tr></tbody></table>
 <p class="hint noprint">Custo total ${money(q.cost)} · margem sobre o preço final ${(q.margin*100).toFixed(1)}%</p></div>`;
 $$('#out input[data-i]').forEach(i=>i.oninput=()=>{LINES[+i.dataset.i].qty=num(i.value);render2()});$$('#out button[data-r]').forEach(b=>b.onclick=()=>{LINES.splice(+b.dataset.r,1);render()})}
function render2(){const el=document.activeElement,i=el&&el.dataset.i;render();if(i!=null){const n=$('#out input[data-i="'+i+'"]');n&&n.focus()}}
$('#print').onclick=()=>window.print();
function hist(){const h=store.get('mf_orc',[]);$('#hist').innerHTML=h.length?'<table><thead><tr><th>Data</th><th>Paciente</th><th>Pacote</th><th>Médico</th><th class="n">Total</th><th></th></tr></thead><tbody>'+h.map((x,i)=>`<tr><td>${brDate(x.at)}</td><td>${esc(x.pat)}</td><td>${esc(x.pkg)}</td><td>${esc(x.doc)}</td><td class="n">${money(x.total)}</td><td><button class="dng sm" data-i="${i}">remover</button></td></tr>`).join('')+'</tbody></table>':'<div class="hint">Nada salvo ainda.</div>';$$('#hist button').forEach(b=>b.onclick=()=>{const h=store.get('mf_orc',[]);h.splice(+b.dataset.i,1);store.set('mf_orc',h);hist()})}
$('#save').onclick=()=>{const h=store.get('mf_orc',[]);h.unshift({at:today(),pat:$('#pat').value,pkg:$('#pkg').value,doc:$('#doc').value,total:calc().total});store.set('mf_orc',h.slice(0,30));hist()};
'''

# ---------------- 3. Supply
sup_body = '''<div class="card noprint" id="ld"></div><div id="app" class="hide"><div class="tabs noprint"><button class="on" data-t="p">Painel de estoque</button><button data-t="o">Ordens de compra <span id="cnt"></span></button></div>
<div id="tp"><div class="card noprint"><h2>Parâmetros</h2><div class="row"><label>Janela de consumo (dias)<input id="win" type="number" value="90" style="width:90px"></label><label>Crítico (< dias)<input id="tr" type="number" value="5" style="width:80px"></label><label>Atenção (< dias)<input id="ty" type="number" value="10" style="width:80px"></label><label>Meta de cobertura (dias)<input id="tg" type="number" value="45" style="width:90px"></label><label>Almoxarifado<select id="wh"></select></label><label>Situação<select id="st"><option value="">Todas</option><option>Crítico</option><option>Atenção</option><option>OK</option><option>Excesso</option><option>Sem consumo</option></select></label><button id="gen">Gerar solicitação de compra</button></div><p class="hint">Cobertura = estoque ÷ consumo médio diário. A solicitação inclui itens com cobertura ≤ prazo do fornecedor + 5 dias e repõe até a meta. Digite a contagem física para ajustar o estoque.</p></div><div class="kpis" id="kp"></div><div class="card"><div id="tb"></div></div></div>
<div id="to" class="hide"><div class="card noprint"><div class="row"><button id="pall">Imprimir ordens</button><button class="sec" id="ocsv">Exportar CSV</button><span class="hint">Uma ordem por fornecedor. Você pode editar quantidades ou remover linhas antes de imprimir.</span></div></div><div id="pos"></div></div></div>'''
sup_js = r'''
let S=[],C={},REQ=[],COUNT={},refDate='';
loader($('#ld'),[{key:'stock',file:'stock.csv',label:'Estoque'},{key:'consumption',file:'consumption.csv',label:'Consumo'}],D=>{
 S=D.stock.map(r=>({...r,stock_qty:num(r.stock_qty),unit_cost:num(r.unit_cost),lead:num(r.lead_time_days)}));C={};const dates=D.consumption.map(r=>r.date).sort();refDate=dates[dates.length-1];
 D.consumption.forEach(r=>{(C[r.sku]=C[r.sku]||[]).push([r.date,num(r.qty)])});
 $('#wh').innerHTML='<option value="">Todos</option>'+[...new Set(S.map(s=>s.warehouse))].map(w=>'<option>'+esc(w)+'</option>').join('');$('#app').classList.remove('hide');COUNT={};REQ=[];draw()});
$$('.tabs button').forEach(b=>b.onclick=()=>{$$('.tabs button').forEach(x=>x.classList.toggle('on',x==b));$('#tp').classList.toggle('hide',b.dataset.t!='p');$('#to').classList.toggle('hide',b.dataset.t!='o');if(b.dataset.t=='o')pos()});
['win','tr','ty','tg','wh','st'].forEach(i=>$('#'+i).addEventListener('change',draw));
function metrics(){const w=num($('#win').value)||90,cut=new Date(new Date(refDate)-w*864e5).toISOString().slice(0,10),tr=num($('#tr').value),ty=num($('#ty').value),tg=num($('#tg').value);
 return S.map(s=>{const tot=(C[s.sku]||[]).filter(x=>x[0]>cut).reduce((a,x)=>a+x[1],0),avg=tot/w,eff=COUNT[s.sku]!=null?COUNT[s.sku]:s.stock_qty,cov=avg>0?eff/avg:Infinity;
  const stt=avg==0?'Sem consumo':cov<tr?'Crítico':cov<ty?'Atenção':cov<=tg?'OK':'Excesso',dd=(new Date(s.expiry_date)-new Date(refDate))/864e5;return{...s,avg,eff,cov,stt,value:eff*s.unit_cost,exp30:dd<=30,tg}})}
const pc={'Crítico':'p-red','Atenção':'p-yel','OK':'p-grn','Excesso':'p-gry','Sem consumo':'p-gry'};
function draw(){let M=metrics();const k=n=>M.filter(m=>m.stt==n).length,fin=M.filter(m=>isFinite(m.cov));
 $('#kp').innerHTML=`<div class="kpi"><b>${money0(M.reduce((a,m)=>a+m.value,0))}</b><span>valor em estoque</span></div><div class="kpi"><b>${fin.length?Math.round(fin.reduce((a,m)=>a+m.cov,0)/fin.length):'-'}</b><span>cobertura média (dias)</span></div><div class="kpi"><b style="color:var(--red)">${k('Crítico')}</b><span>críticos</span></div><div class="kpi"><b style="color:var(--yel)">${k('Atenção')}</b><span>em atenção</span></div><div class="kpi"><b>${k('Excesso')}</b><span>em excesso</span></div><div class="kpi"><b>${M.filter(m=>m.exp30).length}</b><span>vencem em ≤ 30 dias</span></div>`;
 const w=$('#wh').value,st=$('#st').value;M=M.filter(m=>(!w||m.warehouse==w)&&(!st||m.stt==st)).sort((a,b)=>a.cov-b.cov);
 $('#tb').innerHTML='<table><thead><tr><th>SKU</th><th>Item</th><th>ABC</th><th>Almox.</th><th class="n">Estoque</th><th class="n">Contagem</th><th class="n">Consumo/dia</th><th class="n">Cobertura</th><th>Situação</th><th>Validade</th></tr></thead><tbody>'+M.slice(0,200).map(m=>`<tr><td>${m.sku}</td><td>${esc(m.description)}</td><td>${m.abc_class}</td><td>${esc(m.warehouse)}</td><td class="n">${m.stock_qty}</td><td class="n"><input type="number" min="0" data-s="${m.sku}" value="${COUNT[m.sku]??''}" style="width:70px"></td><td class="n">${m.avg.toFixed(1)}</td><td class="n">${isFinite(m.cov)?m.cov.toFixed(1)+' d':'∞'}</td><td><span class="pill ${pc[m.stt]}">${m.stt}</span></td><td>${brDate(m.expiry_date)}${m.exp30?' ⚠':''}</td></tr>`).join('')+'</tbody></table>'+(M.length>200?'<p class="hint">Mostrando 200 de '+M.length+'. Use os filtros.</p>':'');
 $$('#tb input').forEach(i=>i.onchange=()=>{COUNT[i.dataset.s]=i.value===''?undefined:num(i.value);if(i.value==='')delete COUNT[i.dataset.s];draw()})}
$('#gen').onclick=()=>{const M=metrics(),tg=num($('#tg').value);REQ=[];M.filter(m=>m.avg>0&&m.cov<=m.lead+5).forEach(m=>{const q=Math.ceil(tg*m.avg-m.eff);if(q>0)REQ.push({sku:m.sku,description:m.description,supplier:m.supplier,lead:m.lead,qty:q,unit_cost:m.unit_cost,urgent:m.stt=='Crítico'})});$('#cnt').textContent='('+REQ.length+')';$$('.tabs button')[1].click()};
function pos(){const g={};REQ.forEach((r,i)=>(g[r.supplier]=g[r.supplier]||[]).push({...r,i}));let n=0;
 $('#pos').innerHTML=REQ.length?Object.entries(g).sort().map(([sup,L])=>{n++;const t=L.reduce((a,l)=>a+l.qty*l.unit_cost,0),eta=new Date(Date.now()+Math.max(...L.map(l=>l.lead))*864e5).toISOString().slice(0,10);
  return `<div class="sheet" style="margin-bottom:14px;page-break-after:always"><h3>Ordem de compra OC-${String(n).padStart(4,'0')} · ${esc(sup)}</h3><div class="hint">Hospital Demo · emitida em ${brDate(today())} · entrega prevista até ${brDate(eta)}${L.some(l=>l.urgent)?' · <b style="color:var(--red)">contém itens urgentes</b>':''}</div>
  <table style="margin-top:10px"><thead><tr><th>SKU</th><th>Item</th><th class="n">Qtd</th><th class="n">Unit.</th><th class="n">Total</th><th></th></tr></thead><tbody>${L.map(l=>`<tr><td>${l.sku}</td><td>${esc(l.description)}${l.urgent?' <span class="pill p-red">URGENTE</span>':''}</td><td class="n"><input class="noprint" type="number" min="0" value="${l.qty}" data-i="${l.i}" style="width:70px"><span class="hide">${l.qty}</span></td><td class="n">${money(l.unit_cost)}</td><td class="n">${money(l.qty*l.unit_cost)}</td><td class="noprint"><button class="dng sm" data-r="${l.i}">×</button></td></tr>`).join('')}<tr class="tot"><td colspan="4">Total da ordem</td><td class="n">${money(t)}</td><td class="noprint"></td></tr></tbody></table></div>`}).join(''):'<div class="card empty">Nenhuma solicitação. Gere pela aba "Painel de estoque".</div>';
 $$('#pos input').forEach(i=>i.onchange=()=>{REQ[+i.dataset.i].qty=num(i.value);pos()});$$('#pos button').forEach(b=>b.onclick=()=>{REQ.splice(+b.dataset.r,1);$('#cnt').textContent='('+REQ.length+')';pos()})}
$('#pall').onclick=()=>window.print();
$('#ocsv').onclick=()=>download('ordens_de_compra.csv',toCSV(['supplier','sku','description','qty','unit_cost','total','urgent'],REQ.map(r=>({...r,total:(r.qty*r.unit_cost).toFixed(2),urgent:r.urgent?'sim':'nao'})).sort((a,b)=>a.supplier<b.supplier?-1:1)));
'''

# ---------------- 4. Forecast
fc_body = '''<div class="card noprint" id="ld"></div><div id="app" class="hide"><div class="card noprint"><h2>2. Premissas</h2><div class="row"><label>Ajuste do ritmo de receita (%)<input id="a1" type="number" value="0" style="width:100px"></label><label>Ajuste de custos fixos (%)<input id="a2" type="number" value="0" style="width:100px"></label><label>Ajuste de variáveis (% da receita, p.p.)<input id="a3" type="number" value="0" step="0.5" style="width:100px"></label><button class="sec" id="csv">Exportar CSV</button><button id="print">Imprimir / PDF</button></div>
<p class="hint">Receita: ritmo diário do mês parcial × dias do mês. Fixos: último mês fechado. Variáveis: média dos 3 últimos meses fechados em % da receita.</p></div><div id="out"></div></div>'''
fc_js = r'''
let P=[];
loader($('#ld'),[{key:'pl',file:'pl.csv',label:'P&L mensal'}],D=>{P=D.pl.map(r=>({...r,amount:num(r.amount),days:num(r.days_elapsed)}));$('#app').classList.remove('hide');draw()});
['a1','a2','a3'].forEach(i=>$('#'+i).addEventListener('input',draw));
let LAST=[];
function draw(){const months=[...new Set(P.map(r=>r.month))].sort(),cur=months[months.length-1],closed=months.slice(0,-1),last=closed[closed.length-1],l3=closed.slice(-3);
 const sum=(m,f)=>P.filter(r=>r.month==m&&f(r)).reduce((a,r)=>a+r.amount,0),days=P.find(r=>r.month==cur&&r.days)?.days||1,[y,mo]=cur.split('-').map(Number),dim=new Date(y,mo,0).getDate();
 const revCur=sum(cur,r=>r.kind=='receita'),proj=revCur/days*dim*(1+num($('#a1').value)/100);
 const lines=[...new Set(P.filter(r=>r.kind!='receita').map(r=>r.line))],kind=l=>P.find(r=>r.line==l).kind,rows=[];
 lines.forEach(l=>{const k=kind(l),prev=sum(last,r=>r.line==l),act=sum(cur,r=>r.line==l);let p;
  if(k=='fixo')p=prev*(1+num($('#a2').value)/100);else{const pct=l3.reduce((a,m)=>a+sum(m,r=>r.line==l),0)/l3.reduce((a,m)=>a+sum(m,r=>r.kind=='receita'),0);p=proj*(pct+num($('#a3').value)/100/ (lines.filter(x=>kind(x)=='variavel').length))}
  rows.push({line:l,kind:k,prev,act,proj:p})});
 const costP=rows.reduce((a,r)=>a+r.proj,0),costPrev=rows.reduce((a,r)=>a+r.prev,0),revPrev=sum(last,r=>r.kind=='receita'),res=proj-costP,resPrev=revPrev-costPrev;LAST=[{line:'Receita',kind:'receita',prev:revPrev,act:revCur,proj},...rows,{line:'Resultado',kind:'resultado',prev:resPrev,act:'',proj:res}];
 const hist=closed.map(m=>sum(m,r=>r.kind=='receita')-sum(m,r=>r.kind!='receita')),labs=closed.map(m=>m.slice(5)).concat([cur.slice(5)+'*']);
 const v=(a,b)=>b?((a/b-1)*100).toFixed(1)+'%':'-';
 $('#out').innerHTML=`<div class="kpis"><div class="kpi"><b>${money0(proj)}</b><span>receita projetada ${cur}</span></div><div class="kpi"><b>${money0(costP)}</b><span>custos projetados</span></div><div class="kpi"><b style="color:${res<0?'var(--red)':'var(--grn)'}">${money0(res)}</b><span>resultado projetado</span></div><div class="kpi"><b>${(res/proj*100).toFixed(1)}%</b><span>margem projetada</span></div></div>
 <div class="sheet"><h3>Forecast do mês ${cur}</h3><div class="hint">Hospital Demo · ${days} de ${dim} dias realizados · valores em US$</div><table style="margin-top:10px"><thead><tr><th>Linha</th><th>Tipo</th><th class="n">Último fechado (${last})</th><th class="n">Realizado parcial</th><th class="n">Projeção</th><th class="n">Var. vs. fechado</th></tr></thead><tbody>${LAST.map(r=>`<tr class="${r.kind=='resultado'||r.kind=='receita'?'tot':''}"><td>${esc(r.line)}</td><td>${r.kind}</td><td class="n">${money0(r.prev)}</td><td class="n">${r.act===''?'':money0(r.act)}</td><td class="n">${money0(r.proj)}</td><td class="n">${v(r.proj,r.prev)}</td></tr>`).join('')}</tbody></table>
 <h3 style="font-size:14px;margin-top:18px">Resultado mensal (fechados e projeção *)</h3>${bars(hist.concat([res]),labs,{fmt:x=>Math.round(x/1000)+'k',colors:hist.map(x=>x<0?'#b91c1c':'#0f766e').concat(['#f59e0b'])})}</div>`}
$('#print').onclick=()=>window.print();
$('#csv').onclick=()=>download('forecast.csv',toCSV(['line','kind','prev','act','proj'],LAST.map(r=>({...r,prev:Math.round(r.prev),act:r.act===''?'':Math.round(r.act),proj:Math.round(r.proj)}))));
'''

# ---------------- 5. Pagos a médicos
pg_body = '''<div class="card noprint" id="ld"></div><div class="card noprint hide" id="ctl"><h2>2. Extrato</h2><div class="row"><label>Médico<select id="doc"></select></label><label>Ano<select id="yr"></select></label><label>Mês<select id="mo"><option value="">Todos</option></select></label><button id="print">Baixar PDF</button><button class="sec" id="csv">Baixar CSV</button></div></div><div id="out"></div>'''
pg_js = r'''
let P=[];
loader($('#ld'),[{key:'pay',file:'doctor_payments.csv',label:'Pagamentos'}],D=>{P=D.pay.map(r=>({...r,amount:num(r.amount)}));
 $('#doc').innerHTML=[...new Set(P.map(r=>r.doctor_name))].sort().map(d=>'<option>'+esc(d)+'</option>').join('');
 $('#yr').innerHTML=[...new Set(P.map(r=>r.procedure_date.slice(0,4)))].sort().map(y=>'<option>'+y+'</option>').join('');
 $('#mo').innerHTML='<option value="">Todos</option>'+['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'].map((m,i)=>'<option value="'+String(i+1).padStart(2,'0')+'">'+m+'</option>').join('');
 $('#ctl').classList.remove('hide');draw()});
['doc','yr','mo'].forEach(i=>$('#'+i).addEventListener('change',draw));
function sel(){return P.filter(r=>r.doctor_name==$('#doc').value&&r.procedure_date.slice(0,4)==$('#yr').value&&(!$('#mo').value||r.procedure_date.slice(5,7)==$('#mo').value)).sort((a,b)=>a.procedure_date<b.procedure_date?-1:1)}
function draw(){const L=sel(),ap=L.filter(r=>r.status=='aprovado').reduce((a,r)=>a+r.amount,0),pe=L.filter(r=>r.status!='aprovado').reduce((a,r)=>a+r.amount,0),bm={};
 L.forEach(r=>{const m=r.procedure_date.slice(5,7);(bm[m]=bm[m]||[0,0,0]);bm[m][0]++;bm[m][r.status=='aprovado'?1:2]+=r.amount});
 $('#out').innerHTML=L.length?`<div class="sheet"><h3>Extrato de honorários · ${esc($('#doc').value)}</h3><div class="hint">Hospital Demo · ${$('#yr').value}${$('#mo').value?'/'+$('#mo').value:''} · emitido em ${brDate(today())}</div>
 <div class="kpis" style="margin-top:12px"><div class="kpi"><b>${L.length}</b><span>procedimentos</span></div><div class="kpi"><b>${money0(ap)}</b><span>aprovado</span></div><div class="kpi"><b style="color:var(--yel)">${money0(pe)}</b><span>pendente</span></div><div class="kpi"><b>${money0(ap+pe)}</b><span>total realizado</span></div></div>
 <table><thead><tr><th>Data</th><th>Procedimento</th><th>Paciente</th><th>Situação</th><th>Pago em</th><th class="n">Valor</th></tr></thead><tbody>${L.map(r=>`<tr><td>${brDate(r.procedure_date)}</td><td>${esc(r.procedure)}</td><td>${esc(r.patient_code)}</td><td><span class="pill ${r.status=='aprovado'?'p-grn':'p-yel'}">${esc(r.status)}</span></td><td>${brDate(r.payment_date)}</td><td class="n">${money(r.amount)}</td></tr>`).join('')}<tr class="tot"><td colspan="5">Total</td><td class="n">${money(ap+pe)}</td></tr></tbody></table>
 ${!$('#mo').value?`<h3 style="font-size:14px;margin-top:18px">Resumo por mês</h3><table style="max-width:560px"><thead><tr><th>Mês</th><th class="n">Proc.</th><th class="n">Aprovado</th><th class="n">Pendente</th></tr></thead><tbody>${Object.entries(bm).sort().map(([m,v])=>`<tr><td>${m}</td><td class="n">${v[0]}</td><td class="n">${money(v[1])}</td><td class="n">${money(v[2])}</td></tr>`).join('')}</tbody></table>`:''}</div>`:'<div class="card empty">Sem lançamentos para o filtro.</div>'}
$('#print').onclick=()=>window.print();
$('#csv').onclick=()=>download('extrato_'+$('#doc').value.replace(/\s+/g,'_')+'.csv',toCSV(['payment_id','doctor_name','procedure_date','procedure','patient_code','amount','status','payment_date'],sel()));
'''

tools = [
 ('01_estado_de_conta.html', 'Estado de conta por pagador', 'Gera o extrato de contas por pagador, com antiguidade, PDF e histórico', estado_body, estado_js, ['billing.csv']),
 ('02_gerador_de_orcamento.html', 'Gerador de orçamento cirúrgico', 'Pacotes, margem e desconto; emite orçamento em PDF', orc_body, orc_js, ['catalog.csv', 'packages.csv', 'doctors.csv']),
 ('03_supply_estoque_e_compras.html', 'Supply: estoque e ordens de compra', 'Semáforo de cobertura, contagem física e ordens por fornecedor', sup_body, sup_js, ['stock.csv', 'consumption.csv']),
 ('04_forecast_pl.html', 'Forecast do P&L do mês', 'Projeção do mês em curso com premissas ajustáveis', fc_body, fc_js, ['pl.csv']),
 ('05_extrato_pagamentos_medicos.html', 'Extrato de pagamentos a médicos', 'Detalhe por médico, ano e mês, aprovado vs. pendente', pg_body, pg_js, ['doctor_payments.csv']),
]
os.makedirs(os.path.join(HERE, 'tools'), exist_ok=True)
for fn, t, s, b, j, f in tools:
    open(os.path.join(HERE, 'tools', fn), 'w', encoding='utf-8').write(page(t, s, b, j, f))
idx = '''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MedFlow Toolkit</title><style>''' + CSS + '''.g{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}.g a{text-decoration:none;color:inherit}.g .card{height:100%}.g h2{font-size:16px;color:var(--pri)}</style></head><body><header><h1>MedFlow Toolkit</h1><span class="tag">dados fictícios</span></header><main><p>Ferramentas de gestão hospitalar que rodam inteiras no navegador (HTML único, sem servidor). Cada uma abre com dados de demonstração gerados artificialmente; também aceita CSVs próprios.</p><div class="g">''' + ''.join(f'<a href="tools/{fn}"><div class="card"><h2>{t}</h2><p>{s}.</p></div></a>' for fn, t, s, b, j, f in tools) + '''</div></main></body></html>'''
open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8').write(idx)
print('built', len(tools))
