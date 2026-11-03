import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
function setup(stored=null){
 const nodes={};for(const id of ['letter-body','letter-to','letter-name','letter-public','letter-error','letter-save-state','letter-count','letter-clear','letter-options'])nodes[id]={value:'',textContent:'',listeners:{},addEventListener(t,fn){this.listeners[t]=fn},setCustomValidity(v){this.validation=v},setAttribute(){},removeAttribute(){},reportValidity(){return !this.validation},focus(){}};
 nodes['letter-to'].options=['みんなへ','たそ','しゃり'].map(value=>({value,dataset:{memberId:value}}));nodes['letter-to'].value='みんなへ';
 const form={action:'https://docs.google.com/forms/d/e/example/viewform',listeners:{},querySelector(s){return nodes[s.slice(1)]},addEventListener(t,f){this.listeners[t]=f},reportValidity(){return !!nodes['letter-body'].value.trim()&&!!nodes['letter-public'].value},reset(){for(const x of Object.values(nodes))x.value=''}};
 nodes['letter-form']=form;let assigned=null;const events=[];const storage=new Map(stored?[['bridge-letter-draft-v1',JSON.stringify(stored)]]:[]);
 const context={document:{getElementById:id=>nodes[id],querySelectorAll:()=>[]},window:{location:{assign:url=>assigned=url},gtag:(...args)=>events.push(args)},location:{search:''},sessionStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)},URL,URLSearchParams,Date,Event,fetch:async()=>({json:async()=>({episodes:[]})})};
 vm.runInNewContext(readFileSync(new URL('../assets/letters.js',import.meta.url),'utf8'),context);
 return {nodes,form,events,storage,submit(){form.listeners.submit({preventDefault(){}});return assigned}};
}
test('whitespace cannot open the send page',()=>{const app=setup();app.nodes['letter-body'].value='  ';app.nodes['letter-public'].value='はい';assert.equal(app.submit(),null);});
test('publication choice is mandatory',()=>{const app=setup();app.nodes['letter-body'].value='感想です';assert.equal(app.submit(),null);});
test('unsupported recipient is retained in body, not lost',()=>{const app=setup();app.nodes['letter-body'].value='こんにちは & 質問';app.nodes['letter-to'].value='しゃり';app.nodes['letter-public'].value='いいえ';const url=new URL(app.submit());assert.equal(url.searchParams.get('entry.2111815986'),'みんなへ');assert.equal(url.searchParams.get('entry.721706859'),'【しゃり宛て】\nこんにちは & 質問');assert.equal(url.searchParams.get('entry.1377887326'),'いいえ');assert.ok(!JSON.stringify(app.events).includes('こんにちは'));});
test('expired draft is removed, valid draft restored',()=>{assert.equal(setup({body:'old',at:Date.now()-25*3600000}).nodes['letter-body'].value,'');assert.equal(setup({body:'new',at:Date.now()}).nodes['letter-body'].value,'new');});
