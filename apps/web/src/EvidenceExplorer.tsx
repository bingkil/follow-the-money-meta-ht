import {useState} from 'react';
import {TransactionGraph} from './TransactionGraph';

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
  setRun(data);setSelected('');setPair(null);
 }catch(e){setError((e as Error).message);}finally{setBusy(false);}}
 const [pair,setPair]=useState<[string,string]|null>(null);
 const graph=run?.graph;
 const owner=(id:string)=>graph?.accounts.find(a=>a.id===id)?.owner_id||id;
 const labels=(id:string)=>entities?(graph?.customers.find(c=>c.id===id)?.name||id):id;
 const selectedTransactions=graph?.transactions.filter(t=>pair?((entities?owner(t.source_account):t.source_account)===pair[0]&&(entities?owner(t.target_account):t.target_account)===pair[1]):(!selected||(entities?[owner(t.source_account),owner(t.target_account)]:[t.source_account,t.target_account]).includes(selected)))||[];
 return <section className="panel evidence"><div className="panel-head"><h2>Evidence workspace</h2><div className="filters"><button disabled={busy} onClick={()=>collect()}>Collect evidence</button><button disabled={busy} onClick={()=>collect(true)}>Load saved evidence</button></div></div><p>Deterministic analysis · No AI assessment. Two-hop network, up to 180 days before the alert cutoff.</p>{error&&<p role="alert">{error}</p>}{busy&&<p role="status">Collecting source records…</p>}{run&&graph&&<><div className="toolbar"><button onClick={()=>{setEntities(!entities);setSelected('');setPair(null)}}>{entities?'Show accounts':'Group by legal owner'}</button><button onClick={()=>{setSelected('');setPair(null)}}>Clear selection</button><span>{graph.accounts.length} accounts · {graph.transactions.length} transactions · Saved run {run.id.slice(0,8)}</span></div>
 <TransactionGraph graph={graph} entities={entities} selected={selected}
  onSelect={id=>{setSelected(id);setPair(null)}}
  onEdge={(from,to)=>{setSelected('');setPair([from,to])}}
  onClear={()=>{setSelected('');setPair(null)}}/>
 <p>Drag nodes to arrange the view; pan, zoom or fit using the controls. Select a transfer edge to inspect its records. Dashed edges show documented company relationships.</p>
 {entities&&<><h3>Documented company relationships</h3>{graph.relationships.map(r=><p key={r.id}>{graph.customers.find(c=>c.id===r.source_id)?.name} — {r.kind} → {graph.customers.find(c=>c.id===r.target_id)?.name} <small>{r.id} · {r.source}</small></p>)}<p>Companies remain separate legal entities. These ownership links do not establish account operation or knowledge.</p></>}
 <h3>{pair?`${labels(pair[0])} → ${labels(pair[1])}`:selected?labels(selected):'All displayed accounts'} · Source transfers</h3><div className="table-scroll"><table><thead><tr><th>ID</th><th>From → To</th><th>Date · UTC</th><th>Amount</th></tr></thead><tbody>{selectedTransactions.map(t=><tr key={t.id}><td>{t.id}</td><td>{t.source_account} → {t.target_account}</td><td>{t.timestamp.slice(0,10)}</td><td>{money(t.amount_cents)}</td></tr>)}</tbody></table></div>
 <h3>Tool results and evidence</h3>{run.tools.map(t=><details key={t.execution_id}><summary>{t.tool.replaceAll('_',' ')} · {t.source_ids.length} references</summary><ul>{t.limitations.map(l=><li key={l}>{l}</li>)}</ul><pre>{JSON.stringify(t.result,null,2)}</pre><details><summary>Source references</summary><pre>{t.source_ids.join('\n')}</pre></details></details>)}</>}</section>;
}
