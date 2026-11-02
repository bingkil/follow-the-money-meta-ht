import {useEffect, useMemo, useState} from 'react';
import {ReactFlow, Background, Controls, MiniMap, MarkerType, Position,
  applyNodeChanges, type Node, type Edge, type NodeChange} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

export type EvidenceGraph = {
 accounts:{id:string;owner_id:string;branch_id:string}[];
 customers:{id:string;name:string;kind:string}[];
 transactions:{id:string;source_account:string;target_account:string;amount_cents:number;timestamp:string}[];
 relationships:{id:string;source_id:string;target_id:string;kind:string;source:string}[];
};
const money=(value:number)=>new Intl.NumberFormat('en-IE',{style:'currency',currency:'EUR'}).format(value/100);

export function buildGraph(graph:EvidenceGraph,entities:boolean){
 const owner=new Map(graph.accounts.map(a=>[a.id,a.owner_id]));
 const customers=new Map(graph.customers.map(c=>[c.id,c]));
 const ids=entities?graph.customers.map(c=>c.id):graph.accounts.map(a=>a.id);
 const totals=new Map<string,{from:string;to:string;amount:number;count:number}>();
 for(const tx of graph.transactions){
  const from=entities?owner.get(tx.source_account)!:tx.source_account;
  const to=entities?owner.get(tx.target_account)!:tx.target_account;
  if(from===to)continue;
  const key=JSON.stringify([from,to]);
  const entry=totals.get(key)||{from,to,amount:0,count:0};
  entry.amount+=tx.amount_cents;entry.count++;totals.set(key,entry);
 }
 // Deterministic topological columns. Cyclic leftovers get a final column.
 const degree=new Map(ids.map(id=>[id,0]));
 const levels=new Map(ids.map(id=>[id,0]));
 for(const e of totals.values())degree.set(e.to,(degree.get(e.to)||0)+1);
 const queue=ids.filter(id=>degree.get(id)===0).sort();
 const done=new Set<string>();
 while(queue.length){const id=queue.shift()!;done.add(id);
  for(const e of totals.values())if(e.from===id){
   levels.set(e.to,Math.max(levels.get(e.to)||0,(levels.get(id)||0)+1));
   degree.set(e.to,degree.get(e.to)!-1);if(degree.get(e.to)===0)queue.push(e.to);
  }
 }
 const last=Math.max(0,...levels.values())+1;
 ids.filter(id=>!done.has(id)).forEach(id=>levels.set(id,last));
 const rows=new Map<number,number>();
 const nodes:Node[]=ids.sort().map(id=>{
  const level=levels.get(id)||0,row=rows.get(level)||0;rows.set(level,row+1);
  const customer=customers.get(entities?id:owner.get(id)!);
  const count=graph.accounts.filter(a=>a.owner_id===id).length;
  return {id,position:{x:level*330,y:row*125},
   data:{label:<div><strong>{entities?customer?.name:id}</strong><small>{entities?`${customer?.kind} · ${count} observed account${count===1?'':'s'}`:customer?.name}</small></div>},
   sourcePosition:Position.Right,targetPosition:Position.Left,
   style:{width:245,background:'#172637',color:'#e9edf4',border:'1px solid #63c8c5',borderRadius:9},
   ariaLabel:entities?customer?.name:id};
 });
 const edges:Edge[]=[...totals.entries()].map(([id,e])=>({id:'transfer:'+id,source:e.from,target:e.to,
  label:`${money(e.amount)} · ${e.count} transfers`,data:{kind:'transfer'},
  type:'smoothstep',markerEnd:{type:MarkerType.ArrowClosed,color:'#65bdbb'},
  style:{stroke:'#65bdbb'},labelStyle:{fill:'#e9edf4',fontSize:11},
  labelBgStyle:{fill:'#172637'},labelBgPadding:[6,4],interactionWidth:20}));
 if(entities)for(const r of graph.relationships){
  if(!ids.includes(r.source_id)||!ids.includes(r.target_id))continue;
  edges.push({id:'relationship:'+r.id,source:r.source_id,target:r.target_id,label:r.kind,
   data:{kind:'relationship',source:r.source},type:'smoothstep',
   style:{stroke:'#c6ab7c',strokeDasharray:'5 5'},
   markerEnd:{type:MarkerType.ArrowClosed,color:'#c6ab7c'},
   labelStyle:{fill:'#f4ce96'},labelBgStyle:{fill:'#172637'}});
 }
 return {nodes,edges};
}

export function TransactionGraph({graph,entities,selected,onSelect,onEdge,onClear}:{
 graph:EvidenceGraph;entities:boolean;selected:string;onSelect:(id:string)=>void;
 onEdge:(from:string,to:string)=>void;onClear:()=>void;
}){
 const model=useMemo(()=>buildGraph(graph,entities),[graph,entities]);
 const [nodes,setNodes]=useState<Node[]>(model.nodes);
 useEffect(()=>setNodes(model.nodes),[model]);
 const changes=(items:NodeChange[])=>setNodes(current=>applyNodeChanges(items,current));
 return <div className="transaction-flow" aria-label="Observed transaction network">
  <ReactFlow key={entities?'entities':'accounts'} nodes={nodes.map(n=>({...n,selected:n.id===selected}))}
   edges={model.edges} onNodesChange={changes} onNodeClick={(_,node)=>onSelect(node.id)}
   onEdgeClick={(_,edge)=>{if(edge.data?.kind==='transfer')onEdge(edge.source,edge.target)}}
   onPaneClick={onClear} fitView fitViewOptions={{padding:.2}} minZoom={.15} maxZoom={2}
   nodesConnectable={false} edgesReconnectable={false} deleteKeyCode={null}
   colorMode="dark" aria-label="Transaction network: select accounts or transfer edges">
   <Background color="#2b4053" gap={24}/><Controls showInteractive={false}/>
   <MiniMap pannable zoomable nodeColor="#63c8c5"/>
  </ReactFlow>
 </div>;
}
