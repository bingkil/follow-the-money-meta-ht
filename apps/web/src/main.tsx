import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';
import {EvidenceExplorer} from './EvidenceExplorer';

type Alert = {id:string;account_id:string;customer:string;score:number;status:string;owner:string;cutoff:string;rule_version:string};
type Transaction = {id:string;source_account:string;target_account:string;amount_cents:number;timestamp:string};
type Detail = {id:string;account_id:string;owner:string;status:string;customer:{name:string;occupation:string};case:{id:string}|null;evidence:{incoming_cents:number;onward_cents:number;distinct_sender_owners:number;score_components:Record<string,number>;transactions:Transaction[];parameters:Record<string,string|number>;limitation:string}};
const money=(n:number)=>new Intl.NumberFormat('en-IE',{style:'currency',currency:'EUR'}).format(n/100);
async function api<T>(path:string, options?:RequestInit):Promise<T>{
 const response=await fetch('/api'+path,{...options,headers:{'Content-Type':'application/json',...options?.headers}});
 if(!response.ok)throw Error(`Request failed (${response.status}). Check the API and request parameters.`);
 return response.json();
}
function App(){
 const [alerts,setAlerts]=useState<Alert[]>([]),[detail,setDetail]=useState<Detail|null>(null);
 const [error,setError]=useState(''),[message,setMessage]=useState(''),[busy,setBusy]=useState(false);
 const [filter,setFilter]=useState(''),[status,setStatus]=useState('All');
 const [cutoff,setCutoff]=useState('2026-11-01'),[notes,setNotes]=useState<{id:string;content:string}[]>([]),[note,setNote]=useState('');
 async function refresh(){setAlerts(await api<Alert[]>('/alerts'));}
 useEffect(()=>{refresh().catch(e=>setError(e.message));},[]);
 async function select(id:string){setBusy(true);setError('');try{
   const result=await api<Detail>('/alerts/'+id);setDetail(result);setNote('');
   setNotes(result.case?await api('/cases/'+result.case.id+'/notes'):[]);
 }catch(e){setError((e as Error).message);}finally{setBusy(false);}}
 async function run(){setBusy(true);setError('');setMessage('');try{
   const result=await api<{matched:number;created:number}>('/detection-runs',{method:'POST',body:JSON.stringify({cutoff:cutoff+'T00:00:00Z'})});
   await refresh();setMessage(`${result.matched} matches · ${result.created} new alerts. Existing alerts retained.`);
 }catch(e){setError((e as Error).message);}finally{setBusy(false);}}
 async function openCase(){if(!detail)return;setBusy(true);try{
   await api('/alerts/'+detail.id+'/case',{method:'POST'});await select(detail.id);
 }catch(e){setError((e as Error).message);}finally{setBusy(false);}}
 async function saveNote(){if(!detail?.case)return;setBusy(true);try{
   await api('/cases/'+detail.case.id+'/notes',{method:'POST',body:JSON.stringify({content:note})});
   setNotes(await api('/cases/'+detail.case.id+'/notes'));setNote('');
 }catch(e){setError((e as Error).message);}finally{setBusy(false);}}
 async function assign(){if(!detail)return;setBusy(true);try{
   await api('/alerts/'+detail.id,{method:'PATCH',body:JSON.stringify({owner:detail.owner,status:detail.status})});
   await refresh();setMessage('Assignment saved.');
 }catch(e){setError((e as Error).message);}finally{setBusy(false);}}
 const visible=alerts.filter(a=>(status==='All'||a.status===status)&&`${a.customer} ${a.account_id}`.toLowerCase().includes(filter.toLowerCase()));
 return <main><header><div className="brand">FTM<span>INVESTIGATION WORKSPACE</span></div><span className="badge">SYNTHETIC DATA</span></header>
 <section><p className="eyebrow">TRANSACTION MONITORING</p><h1>Start with a signal.<br/>Follow the evidence.</h1><p className="intro">Prioritised alerts · Rapid onward movement from multiple senders</p></section>
 <div className="toolbar"><label>Exclusive cutoff · UTC<input type="date" value={cutoff} onChange={e=>setCutoff(e.target.value)}/></label><button disabled={busy||!cutoff} onClick={run}>Run detection</button><span>7-day window · ≥3 sender owners · ≥€1,000 incoming · ≥80% onward within 48h</span></div>
 {error&&<p role="alert">{error}</p>}{message&&<p role="status">{message}</p>}
 <section className="panel"><div className="panel-head"><h2>Alert queue <span className="count">{alerts.length}</span></h2><div className="filters"><input aria-label="Search alerts" placeholder="Search customer or account" value={filter} onChange={e=>setFilter(e.target.value)}/><select aria-label="Filter status" value={status} onChange={e=>setStatus(e.target.value)}>{['All','New','Assigned','Investigating','Resolved'].map(s=><option key={s}>{s}</option>)}</select></div></div><p>Highest priority first. Scores are uncalibrated investigation priorities.</p>
 {!visible.length?<p>No alerts in this view. Seed the fixture, then run detection.</p>:<div className="table-scroll"><table><thead><tr><th>Priority</th><th>Customer / account</th><th>Rule</th><th>Status</th><th>Owner</th><th>Action</th></tr></thead><tbody>{visible.map(a=><tr key={a.id} className={detail?.id===a.id?'selected':''}><td><span className="score">{a.score}</span></td><td>{a.customer}<small>{a.account_id}</small></td><td>{a.rule_version}</td><td>{a.status}</td><td>{a.owner||'Unassigned'}</td><td><button disabled={busy} onClick={()=>select(a.id)}>Inspect alert</button></td></tr>)}</tbody></table></div>}</section>
 {detail&&<section className="panel"><div className="panel-head"><h2>{detail.customer.name} · {detail.account_id}</h2><button onClick={()=>setDetail(null)}>Close</button></div><p>{detail.customer.occupation} · Trigger snapshot preserved from detection.</p><div className="metrics"><article><strong>{money(detail.evidence.incoming_cents)}</strong><span>Incoming</span></article><article><strong>{money(detail.evidence.onward_cents)}</strong><span>Qualifying onward</span></article><article><strong>{detail.evidence.distinct_sender_owners}</strong><span>Sender owners</span></article></div><p>{detail.evidence.limitation}</p>
 <h3>Priority calculation</h3><ul>{Object.entries(detail.evidence.score_components).map(([name,value])=><li key={name}>{name.replaceAll('_',' ')}: {value}</li>)}</ul><details><summary>Rule parameters</summary><pre>{JSON.stringify(detail.evidence.parameters,null,2)}</pre></details>
 <h3>Triggering transactions</h3><div className="table-scroll"><table><thead><tr><th>Evidence ID</th><th>From → To</th><th>Time · UTC</th><th>EUR</th></tr></thead><tbody>{detail.evidence.transactions.map(t=><tr key={t.id}><td>{t.id}</td><td>{t.source_account} → {t.target_account}</td><td>{new Date(t.timestamp).toISOString()}</td><td>{money(t.amount_cents)}</td></tr>)}</tbody></table></div>
 <div className="toolbar"><label>Owner<input value={detail.owner} maxLength={100} onChange={e=>setDetail({...detail,owner:e.target.value})}/></label><label>Status<select value={detail.status} onChange={e=>setDetail({...detail,status:e.target.value})}>{['New','Assigned','Investigating','Resolved'].map(s=><option key={s}>{s}</option>)}</select></label><button disabled={busy} onClick={assign}>Save assignment</button><button disabled={busy||!!detail.case} onClick={openCase}>{detail.case?'Case open':'Open case'}</button><button disabled title="Agent integration is the next development stage">Follow The Money · upcoming</button></div>
 {detail.case&&<><h3>Case notes</h3>{notes.map(n=><p className="note" key={n.id}>{n.content}</p>)}<textarea aria-label="Case note" maxLength={10000} value={note} onChange={e=>setNote(e.target.value)} placeholder="Record an investigation note"/><button disabled={busy||!note.trim()} onClick={saveNote}>Save note</button></>}
 </section>}
 {detail&&<EvidenceExplorer key={detail.id} alertId={detail.id}/>}
 <footer>Local demo · All records fictional. Detection identifies activity for review; it does not establish trafficking or mule activity.</footer></main>;
}
createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>);
