import assert from 'node:assert/strict';
import {test, after} from 'node:test';
import {readFile, writeFile, mkdtemp, mkdir, rm} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
import {transform} from 'esbuild';

// Exercise the actual TSX model builder in Node; browser-only stylesheet is omitted.
const source=(await readFile(new URL('../src/TransactionGraph.tsx',import.meta.url),'utf8'))
 .replace("import '@xyflow/react/dist/style.css';",'');
const cache=new URL('../node_modules/.cache/',import.meta.url);
await mkdir(cache,{recursive:true});
const dir=await mkdtemp(new URL('ftm-graph-',cache));
const compiled=await transform(source,{loader:'tsx',format:'esm',jsx:'automatic'});
const file=dir+'/graph.mjs';await writeFile(file,compiled.code);
const {buildGraph}=await import(pathToFileURL(file).href);
after(()=>rm(dir,{recursive:true,force:true}));
const graph={
 accounts:[{id:'a1',owner_id:'person'},{id:'a2',owner_id:'person'},{id:'b',owner_id:'company'},{id:'w',owner_id:'worker'}],
 customers:[{id:'person',name:'Person',kind:'person'},{id:'company',name:'Company',kind:'business'},{id:'worker',name:'Worker',kind:'person'}],
 relationships:[{id:'r',source_id:'person',target_id:'company',kind:'owns',source:'KYC'}],
 transactions:[{id:'t1',source_account:'w',target_account:'a1',amount_cents:1000},{id:'t2',source_account:'w',target_account:'a2',amount_cents:2000},{id:'t3',source_account:'a1',target_account:'a2',amount_cents:500},{id:'t4',source_account:'a2',target_account:'b',amount_cents:2500}],
};
test('legal-owner grouping preserves corporate identity and excludes internal transfers',()=>{
 const model=buildGraph(graph,true);
 assert.equal(model.nodes.length,3);
 const transfers=model.edges.filter(e=>e.data.kind==='transfer');
 assert.equal(transfers.length,2);
 assert.equal(transfers.find(e=>e.source==='worker').label,'€30.00 · 2 transfers');
 assert.equal(transfers.find(e=>e.source==='person').target,'company');
 assert.equal(model.edges.find(e=>e.data.kind==='relationship').data.source,'KYC');
 assert.equal(model.edges.some(e=>e.source===e.target),false);
});
test('account view retains internal transfer and uses deterministic positions without mutating evidence',()=>{
 const before=JSON.stringify(graph);
 const first=buildGraph(graph,false),second=buildGraph(graph,false);
 assert.equal(first.nodes.length,4);
 assert.equal(first.edges.length,4);
 assert.deepEqual(first.nodes.map(n=>n.position),second.nodes.map(n=>n.position));
 assert.equal(JSON.stringify(graph),before);
 assert.equal(first.edges.some(e=>e.source==='a1'&&e.target==='a2'),true);
});
