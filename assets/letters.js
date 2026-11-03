'use strict';
(() => {
  const form=document.getElementById('letter-form');if(!form)return;
  const body=form.querySelector('#letter-body'),to=form.querySelector('#letter-to'),name=form.querySelector('#letter-name'),pub=form.querySelector('#letter-public'),error=document.getElementById('letter-error'),state=document.getElementById('letter-save-state'),count=document.getElementById('letter-count');
  const key='bridge-letter-draft-v1',maxAge=24*60*60*1000;
  const track=(event)=>{if(typeof window.gtag==='function')window.gtag('event',event,{type:'google_form'});};
  function update(){count.textContent=`${body.value.length} / 1500`;body.setCustomValidity('');body.removeAttribute('aria-invalid');error.textContent='';}
  function save(){update();try{sessionStorage.setItem(key,JSON.stringify({body:body.value,to:to.value,name:name.value,public:pub.value,at:Date.now()}));state.textContent='このタブに下書きを一時保存しています（24時間まで）。';}catch{state.textContent='このブラウザーでは下書きを保存できません。';}}
  try{const old=JSON.parse(sessionStorage.getItem(key)||'null');if(old&&Date.now()-old.at<maxAge){body.value=String(old.body||'').slice(0,1500);name.value=String(old.name||'').slice(0,40);if([...to.options].some(o=>o.value===old.to))to.value=old.to;if(['はい','いいえ'].includes(old.public))pub.value=old.public;state.textContent='このタブの下書きを復元しました。';}else sessionStorage.removeItem(key);}catch{}
  update();let started=false;
  form.addEventListener('input',()=>{if(!started){track('letter_start');started=true;}save();});form.addEventListener('change',save);
  document.querySelectorAll('[data-letter-prompt],[data-topic]').forEach(button=>button.addEventListener('click',()=>{const text=button.dataset.letterPrompt||'話してほしいテーマ：'+button.dataset.topic+'\n';if(!body.value.includes(text.trim()))body.value=(text+'\n'+body.value).slice(0,1500);save();body.focus();}));
  document.getElementById('letter-clear').addEventListener('click',()=>{form.reset();try{sessionStorage.removeItem(key);}catch{}update();state.textContent='下書きを消しました。';body.focus();});
  const params=new URLSearchParams(location.search);
  const chosen=[...to.options].find(o=>o.dataset.memberId===params.get('to'));if(chosen){to.value=chosen.value;document.getElementById('letter-options').open=true;}
  if(params.get('episode'))fetch('/data/episodes.json').then(r=>r.json()).then(data=>{const ep=data.episodes.find(x=>x.id===params.get('episode'));if(ep&&!body.value){body.value=`「${ep.title}」の感想\n\n`;save();}}).catch(()=>{});
  form.addEventListener('submit',event=>{event.preventDefault();error.textContent='';if(!body.value.trim()){body.setCustomValidity('メッセージを一言、入力してください。');body.setAttribute('aria-invalid','true');body.reportValidity();return;}body.setCustomValidity('');if(!form.reportValidity())return;
    const supported=['たそ','いが','こうち','しゅう','みんなへ'],target=supported.includes(to.value)?to.value:'みんなへ';
    const message=(target!==to.value?`【${to.value}宛て】\n`:'')+body.value.trim();
    const url=new URL(form.action);url.search=new URLSearchParams({usp:'pp_url','entry.1204434679':name.value.trim(),'entry.2111815986':target,'entry.721706859':message,'entry.1377887326':pub.value}).toString();
    save();track('letter_form_open');window.location.assign(url.toString());
  });
})();
