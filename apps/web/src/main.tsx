import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';
type Overview = {counts: Record<string,number>; accounts: {id:string;owner:string;kind:string;branch_id:string;balance_cents:number}[]};
function App(){
 const [data,setData]=useState<Overview|null>(null);
 const [error,setError]=useState('');
 useEffect(()=>{const controller=new AbortController(); fetch('/api/overview',{signal:controller.signal}).then(r=>{if(!r.ok)throw Error('API unavailable');return r.json()}).then(setData).catch(e=>{if(e.name!=='AbortError')setError('Cannot reach the API. Check that the backend is running.');});return ()=>controller.abort();},[]);
 return <main><header><div className="brand">FTM<span>INVESTIGATION WORKSPACE</span></div><span className="badge">SYNTHETIC DATA</span></header><section><p className="eyebrow">FOLLOW THE MONEY</p><h1>Every connection starts<br/>with evidence.</h1><p className="intro">Development foundation · Explore the source accounts behind our fictional collection network.</p></section>{error&&<p role="alert">{error}</p>}{!data&&!error&&<p role="status">Loading source data…</p>}{data&&<><div className="metrics">{Object.entries(data.counts).map(([key,value])=><article key={key}><strong>{value}</strong><span>{key}</span></article>)}</div><section className="panel"><h2>Source accounts</h2><p>Account owners remain distinct from company ownership relationships.</p>{data.accounts.length===0?<p>Run the seed command to create synthetic source records.</p>:<div className="table-scroll"><table><thead><tr><th>Account</th><th>Legal owner</th><th>Type</th><th>Branch</th><th>Balance · EUR</th></tr></thead><tbody>{data.accounts.map(a=><tr key={a.id}><td>{a.id}</td><td>{a.owner}</td><td>{a.kind}</td><td>{a.branch_id}</td><td>{new Intl.NumberFormat('en-IE',{style:'currency',currency:'EUR'}).format(a.balance_cents/100)}</td></tr>)}</tbody></table></div>}</section></>}<footer>Foundation build. Monitoring, investigation agents and case decisions are upcoming stages.</footer></main>;
}
createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>);
