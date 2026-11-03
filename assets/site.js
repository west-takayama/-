'use strict';
(() => {
  const $ = s => document.querySelector(s);
  const track = (name, fields = {}) => { if (typeof window.gtag === 'function') window.gtag('event', name, fields); };
  // Form contents and free-text searches are never included in custom analytics.
  document.querySelectorAll('[data-track]').forEach(a => a.addEventListener('click', () => track(a.dataset.track, {destination:new URL(a.href).hostname,placement:a.closest('footer')?'footer':'content'})));
  const bar=$('#player-bar'),audio=$('#site-audio'),title=$('#player-title'),notice=$('#player-notice');
  let sampleEnd=null,activeId='',lastTrigger=null;
  document.querySelectorAll('[data-play]').forEach(button => button.addEventListener('click',async()=>{
    lastTrigger=button;
    document.querySelectorAll('audio').forEach(p=>{if(p!==audio)p.pause();});
    const changed=activeId!==button.dataset.id; activeId=button.dataset.id;
    if(changed)audio.src=button.dataset.play;
    sampleEnd=button.dataset.sample?Number(button.dataset.sample):null;
    if(changed||sampleEnd)audio.currentTime=0;
    title.replaceChildren();const label=document.createElement('small');label.textContent=sampleEnd?'30 SECOND PREVIEW':'NOW PLAYING';
    title.append(label,document.createTextNode(button.dataset.title));title.href=button.dataset.url;
    bar.hidden=false;notice.textContent='';
    try{await audio.play();track(sampleEnd?'sample_start':'audio_start',{episode_id:activeId,placement:'home'});}
    catch{notice.textContent='音声を開始できませんでした。再生ボタンを押すか、各回の配信元リンクからお聴きください。';}
  }));
  if(audio){
    audio.addEventListener('timeupdate',()=>{if(sampleEnd&&audio.currentTime>=sampleEnd){audio.pause();sampleEnd=null;notice.textContent='続きが気になったら、▶ を押してそのまま本編へ。';track('sample_complete',{episode_id:activeId});}});
    audio.addEventListener('error',()=>{notice.textContent='音声を読み込めませんでした。タイトルを押して、各回の配信元リンクからお聴きください。';});
    $('#player-close').addEventListener('click',()=>{audio.pause();bar.hidden=true;lastTrigger?.focus();});
  }
  document.querySelectorAll('audio').forEach(player=>{
    let marks=new Set();player.addEventListener('loadstart',()=>{marks=new Set();});
    player.addEventListener('play',()=>{document.querySelectorAll('audio').forEach(p=>{if(p!==player)p.pause();});if(player.dataset.episodeId&&!marks.has('start')){track('audio_start',{episode_id:player.dataset.episodeId,placement:'episode'});marks.add('start');}});
    player.addEventListener('timeupdate',()=>{if(!Number.isFinite(player.duration)||!player.duration)return;[25,50,75,90].forEach(percent=>{if(player.currentTime/player.duration*100>=percent&&!marks.has(percent)){marks.add(percent);track('audio_progress',{episode_id:player.dataset.episodeId||activeId,percent});}});});
  });
  const search=$('#episode-search');
  if(search){
    let category='すべて';const rows=[...document.querySelectorAll('[data-episode]')],normalize=s=>s.normalize('NFKC').toLowerCase().trim();
    const update=()=>{const words=normalize(search.value).split(/\s+/).filter(Boolean);let count=0;rows.forEach(row=>{const visible=words.every(w=>normalize(row.dataset.search).includes(w))&&(category==='すべて'||row.dataset.topics.split('|').includes(category));row.hidden=!visible;if(visible)count++;});$('#search-count').textContent=`${count}件のエピソード`;$('#empty-search').hidden=count!==0;};
    search.addEventListener('input',update);
    document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{category=button.dataset.filter;document.querySelectorAll('[data-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));update();track('topic_filter',{topic:category});}));
  }
  async function share(button,copyOnly){
    const url=button.dataset.copy||button.dataset.share,status=button.parentElement.querySelector('.share-status');
    try{if(!copyOnly&&navigator.share)await navigator.share({title:button.dataset.shareTitle,url});else{await navigator.clipboard.writeText(url);status.textContent='リンクをコピーしました';}track('episode_share',{method:copyOnly?'copy':'share',episode_id:location.pathname.split('/')[2]||''});}
    catch(err){if(err.name!=='AbortError')status.textContent='このURLをコピーしてください：'+url;}
  }
  document.querySelectorAll('[data-share]').forEach(b=>b.addEventListener('click',()=>share(b,false)));
  document.querySelectorAll('[data-copy]').forEach(b=>b.addEventListener('click',()=>share(b,true)));
  if('serviceWorker' in navigator)navigator.serviceWorker.register('/sw.js',{updateViaCache:'none'}).then(r=>r.update()).catch(()=>{});
})();
