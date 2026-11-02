import {useState} from 'react';

type Account={id:string;owner_id:string;branch_id:string};
type Customer={id:string;name:string;kind:string};
type Tx={id:string;source_account:string;target_account:string;amount_cents:number;timestamp:string};
type Graph={accounts:Account[];customers:Customer[];transactions:Tx[];relationships:{id:string;source_id:string;target_id:string;kind:string;source:string}[]};
type Tool={execution_id:string;tool:string;source_ids:string[];limitations:string[];result:unknown};
type Run={id:string;mode:string;tools:Tool[];graph:Graph};
const money=(v:number)=>new Intl.NumberFormat('en-IE',{style:'currency',currency:'EUR'}).format(v/100);
export function EvidenceExplorer({alertId}:{alertId:string}){
 const [run,setRun]=useState<Run|null>(null),[error,setError]=useState(''),[busy,setBusy]=useState(false),[entities,setEntities]=useState(false),[selected,setSelected]=useState('');
 async function collect(reuse=false){setBusy(true);setError('');try{
  const r=await fetch(`/api/alerts/${alertId}/evidence`,reuse?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({max_hops:2})});
  if(!r.ok)throw Error('Evidence collection failed');
  const result=await r.json();const data=reuse?result[0]:result;
  if(!data)throw Error('No saved evidence run yet.');
  setRun(data);setSelected('');
 }catch(e){setError((e as Error).message);}finally{setBusy(false);}}
 const graph=run?.graph;
 const owner=(id:string)=>graph?.accounts.find(a=>a.id===id)?.owner_id||id;
 const ids=graph?(entities?[...new Set(graph.accounts.map(a=>a.owner_id))]:graph.accounts.map(a=>a.id)):[];
 const labels=(id:string)=>entities?(graph?.customers.find(c=>c.id===id)?.name||id):id;
 const pos=(id:string)=>{const i=ids.indexOf(id);const angle=2*Math.PI*i/Math.max(ids.length,1)-Math.PI/2;return {x:480+365*Math.cos(angle),y:300+230*Math.sin(angle)}};
 const edges=new Map<string,{from:string;to:string;amount:number;count:number}>();
 graph?.transactions.forEach(t=>{const from=entities?owner(t.source_account):t.source_account,to=entities?owner(t.target_account):t.target_account;if(from===to)return;const k=from+'|'+to;const old=edges.get(k)||{from,to,amount:0,count:0};old.amount+=t.amount_cents;old.count++;edges.set(k,old)});
 const selectedTransactions=graph?.transactions.filter(t=>!selected||(entities?[owner(t.source_account),owner(t.target_account)]:[t.source_account,t.target_account]).includes(selected))||[];
 return <section className="panel evidence"><div className="panel-head"><h2>Evidence workspace</h2><div className="filters"><button disabled={busy} onClick={()=>collect()}>Collect evidence</button><button disabled={busy} onClick={()=>collect(true)}>Load saved evidence</button></div></div><p>Deterministic analysis · No AI assessment. Two-hop network, up to 180 days before the alert cutoff.</p>{error&&<p role="alert">{error}</p>}{busy&&<p role="status">Collecting source records…</p>}{run&&graph&&<><div className="toolbar"><button onClick={()=>{setEntities(!entities);setSelected('')}}>{entities?'Show accounts':'Group by legal owner'}</button><button onClick={()=>setSelected('')}>Clear selection</button><span>{graph.accounts.length} accounts · {graph.transactions.length} transactions · Saved run {run.id.slice(0,8)}</span></div>
 <div className="table-scroll"><svg viewBox="0 0 960 600" role="img" aria-label="Observed transaction network" style={{minWidth:650,width:'100%',maxHeight:620}}><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="24" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#5b7d92"/></marker></defs>{[...edges.values()].map(e=>{const a=pos(e.from),b=pos(e.to);return <line key={e.from+'|'+e.to} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={selected&&[e.from,e.to].includes(selected)?'#e5bc79':'#3b586c'} strokeWidth={selected&&[e.from,e.to].includes(selected)?3:1.5} markerEnd="url(#arrow)"><title>{labels(e.from)} → {labels(e.to)}: {money(e.amount)} across {e.count} transfers</title></line>})}{ids.map(id=>{const p=pos(id);return <g key={id} role="button" tabIndex={0} aria-label={'Select '+labels(id)} onClick={()=>setSelected(id)} onKeyDown={e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();setSelected(id)}}} style={{cursor:'pointer'}}><circle cx={p.x} cy={p.y} r={selected===id?19:14} fill={selected===id?'#e5bc79':'#63c8c5'}/><text x={p.x} y={p.y+32} textAnchor="middle" fill="#e9edf4" fontSize={11}>{labels(id)}</text></g>})}</svg></div>
 {entities&&<><h3>Documented company relationships</h3>{graph.relationships.map(r=><p key={r.id}>{graph.customers.find(c=>c.id===r.source_id)?.name} — {r.kind} → {graph.customers.find(c=>c.id===r.target_id)?.name} <small>{r.id} · {r.source}</small></p>)}<p>Companies remain separate legal entities. These ownership links do not establish account operation or knowledge.</p></>}
 <h3>{selected?labels(selected):'All displayed accounts'} · Source transfers</h3><div className="table-scroll"><table><thead><tr><th>ID</th><th>From → To</th><th>Date · UTC</th><th>Amount</th></tr></thead><tbody>{selectedTransactions.map(t=><tr key={t.id}><td>{t.id}</td><td>{t.source_account} → {t.target_account}</td><td>{t.timestamp.slice(0,10)}</td><td>{money(t.amount_cents)}</td></tr>)}</tbody></table></div>
 <h3>Tool results and evidence</h3>{run.tools.map(t=><details key={t.execution_id}><summary>{t.tool.replaceAll('_',' ')} · {t.source_ids.length} references</summary><ul>{t.limitations.map(l=><li key={l}>{l}</li>)}</ul><pre>{JSON.stringify(t.result,null,2)}</pre><details><summary>Source references</summary><pre>{t.source_ids.join('\n')}</pre></details></details>)}</>}</section>;
}
