"""Keep the original homepage's presentation and fortune; add bounded improvements."""
from datetime import datetime
from email.utils import parsedate_to_datetime
from html import escape as e
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo
from letters import letter_form
ROOT=Path(__file__).resolve().parents[1]
BASE='https://spectacular-cuchufli-3e84ee.netlify.app'

def path(item):return '/episodes/'+item['id']+'/'
def day(item):return datetime.fromisoformat(item['published']).astimezone(ZoneInfo('Asia/Tokyo')).strftime('%Y.%m.%d')
def replace_once(source,old,new):
    if source.count(old)!=1:raise ValueError('Expected one original marker: '+old[:100])
    return source.replace(old,new,1)
def original_home(episodes,cast,articles=None):
    s=(ROOT/'index.html').read_text()
    # Original style block, logo, typography, sections, navigation and fortune stay intact.
    s=s.replace('<body>','<body class="br-home">\n<h1 class="br-visually-hidden">ブリッジラジオ 00s</h1>',1)
    schema=json.dumps({'@context':'https://schema.org','@type':'PodcastSeries','name':'ブリッジラジオ 00s','url':BASE+'/','webFeed':'https://anchor.fm/s/10b7b57e4/podcast/rss','inLanguage':'ja','image':BASE+'/icon-512.png'},ensure_ascii=False).replace('<','\\u003c')
    s=s.replace('</head>',f'<link rel="canonical" href="{BASE}/"><meta property="og:image" content="{BASE}/icon-512.png"><meta name="twitter:image" content="{BASE}/icon-512.png"><link rel="stylesheet" href="/assets/home-additions.css"><script type="application/ld+json">{schema}</script><script defer src="/assets/site.js"></script><script defer src="/assets/home.js"></script></head>',1)
    s=re.sub(r'<!-- Google Analytics -->.*?<!-- Google Search Console -->', '<script defer src="/assets/analytics.js"></script>\n<!-- Google Search Console -->',s,count=1,flags=re.S)
    s=s.replace('</head>','<link rel="stylesheet" href="/assets/letters.css"><script defer src="/assets/letters.js"></script></head>',1)
    latest=episodes[0]
    extra=f'''<details class="br-listen"><summary>🎧 最新回をこのサイトで聴く</summary><div class="br-listen-body"><p>{e(latest['title'])}</p><button class="btn-main br-compact" data-play="{e(latest['audio'])}" data-title="{e(latest['title'])}" data-id="{latest['id']}" data-url="{path(latest)}" data-sample="30">▶ 冒頭30秒を試聴</button><a class="btn-sub br-compact" href="{path(latest)}">この回を詳しく見る・本編を聴く →</a><a class="br-text-link" href="/episodes/">全エピソードを検索する →</a></div></details>'''
    marker='    </div>\n  </section>\n\n  <!-- NEWS -->'
    s=replace_once(s,marker,extra+'\n'+marker)
    news=''.join(f'<a class="news-item" href="{path(x)}"><span class="news-date">{day(x)}</span><span class="news-title">新エピソード公開：{e(x["title"])}</span><span class="news-arrow">→</span></a>' for x in episodes[:3])
    s=re.sub(r'(<div class="news-list" id="news-list">).*?(\n    </div>)',lambda m:m[1]+news+m[2],s,count=1,flags=re.S)
    rows=''.join(f'<a class="ep-item" href="{path(x)}"><div class="ep-info"><div class="ep-title">{e(x["title"])}</div><div class="ep-meta">{day(x)} · {round(x["duration"]/60)} MIN</div></div><span class="ep-play">▶</span></a>' for x in episodes[:6])
    s=re.sub(r'(<div class="ep-list" id="ep-list">).*?(\n    </div>)',lambda m:m[1]+rows+m[2],s,count=1,flags=re.S)
    s=s.replace('<div class="ep-list" id="ep-list">','<a class="btn-sub br-search-link" href="/episodes/">🔎 キーワード・テーマから探す</a>\n<div class="ep-list" id="ep-list">',1)
    blogs=json.loads((ROOT/'data/blog.json').read_text())
    blogrows=[]
    for article in articles or []:
        blogrows.append(f'<a class="blog-card" href="/blog/{article["id"]}/"><div class="blog-thumb">📝</div><div class="blog-body"><div class="blog-date">{article["published"][:10]} · 読みもの</div><div class="blog-title">{e(article["title"])}</div><div class="blog-excerpt">{e(article["description"][:70])}…</div><div class="blog-more">続きを読む →</div></div></a>')
    for i,b in enumerate(blogs):
        d=parsedate_to_datetime(b['published']).astimezone(ZoneInfo('Asia/Tokyo')).strftime('%Y.%m.%d')
        blogrows.append(f'<a class="blog-card" href="{e(b["url"])}" target="_blank" rel="noopener noreferrer"><div class="blog-thumb">{["📝","🎙️","🌉","💭","✨"][i%5]}</div><div class="blog-body"><div class="blog-date">{d}</div><div class="blog-title">{e(b["title"])}</div><div class="blog-excerpt">{e(b["description"][:60])}…</div><div class="blog-more">続きを読む →</div></div></a>')
    s=re.sub(r'(<div class="blog-list" id="blog-list">).*?(\n    </div>)',lambda m:m[1]+''.join(blogrows)+m[2],s,count=1,flags=re.S)
    # Server-built content keeps the same cards, without browser-side proxy dependencies.
    s=re.sub(r'// NEWS LOADER.*?// SCROLL REVEAL','// News and blog are rendered from validated snapshots.\n\n// SCROLL REVEAL',s,count=1,flags=re.S)
    s=re.sub(r'// EPISODE LOADER.*?// PWA: Service Worker 登録','// Episodes are rendered from validated RSS snapshots.\n\n// PWA: Service Worker 登録',s,count=1,flags=re.S)
    start=s.index('  const GOAL_CSV =',s.index('async function loadGoal()'))
    end=s.index('    const pct =',start)
    s=s[:start]+'''  try {
    let res;
    if (location.hostname === 'spectacular-cuchufli-3e84ee.netlify.app') {
      try { res = await fetch('/.netlify/functions/goal', {signal:AbortSignal.timeout(10000)}); if (!res.ok) res = null; } catch {}
    }
    if (!res) res = await fetch('/data/goal.json');
    if (!res.ok) throw new Error('goal snapshot unavailable');
    const data = await res.json();
    const current = Number(data.current);
    const target = Number(data.target);
    const updated = data.updated || '';
    const age = Date.now() - Date.parse(data.measured_at || '');
    document.getElementById('goal-status').textContent = data.fallback || data.is_stale || age > 14*86400000 ? '最新の集計待ちです。表示は最後に確認できた記録です。' : '公開目標シートの記録を表示しています。';
    if (!Number.isFinite(current) || !Number.isFinite(target) || target <= 0) throw new Error('invalid goal');
'''+s[end:]
    # Keep the participation panel's visual components; remove fabricated totals.
    s=s.replace("onclick=\"switchFanTab('vote')\">🗳️ 投票", "onclick=\"switchFanTab('vote')\">🗳️ テーマ募集")
    a=s.index('    <!-- VOTE -->');b=s.index('  </section>',a)
    topics=['友達関係のモヤモヤ','働くことへの本音','好きなものを好きと言う勇気']
    s=s[:a]+'''    <!-- THEME REQUEST -->
    <div class="fan-panel" id="fan-vote"><div class="sec-label">NEXT TOPIC</div><h2 class="sec-title" style="margin-bottom:6px;">みんなに聞いてみた</h2><p class="sec-body" style="margin-bottom:24px;">次回のテーマ、どれが聴きたい？選んでお便りとして送ってね。</p><div class="vote-card"><div class="vote-question">次に聴きたい話を選んでね</div><div class="vote-options">'''+''.join(f'<button class="vote-opt br-topic" type="button" onclick="requestTopic(\'{x}\')"><span class="vote-circle"></span><span class="vote-text">「{x}」</span><span>→</span></button>' for x in topics)+'''</div><p class="br-help">テーマを選ぶとお便り欄に下書きが入ります。確認画面で送信すると番組へ届きます。</p></div></div>
'''+s[b:]
    s=re.sub(r'// VOTE\n.*?// TOAST','// Theme requests are delivered through the existing letter form.\n// TOAST',s,count=1,flags=re.S)
    # Keep the original participation panel, with one shared, simpler form.
    start=s.index('      <div class="form-group">',s.index('<!-- LETTER -->'))
    end=s.index('    <!-- THEME REQUEST -->',start)
    s=s[:start]+letter_form(cast)+'\n    </div>\n\n'+s[end:]
    for p in cast:s=s.replace("letterTarget: '"+p['id']+"'","letterTarget: '"+p['name']+"'")
    s=re.sub(r'function submitLetter\(\) \{.*?\n\}', "function submitLetter() { document.getElementById('letter-form').requestSubmit(); }",s,count=1,flags=re.S)
    s=replace_once(s,"  event.target.classList.add('active');", "  const tabs = document.querySelectorAll('.fan-tab');\n  const active = tabs[id === 'letter' ? 0 : 1];\n  if (active) active.classList.add('active');")
    goal=json.loads((ROOT/'data/goal.json').read_text())
    current,target=goal['current'],goal['target'];remain=max(target-current,0);pct=min(round(current/target*100),100)
    s=s.replace('id="goal-updated">読み込み中…',f'id="goal-updated">集計日：{e(goal["updated"])}')
    s=s.replace('id="goal-count">－<span>/ －</span>',f'id="goal-count">{current:,}<span>/ {target:,}</span>')
    s=s.replace('id="goal-target">目標まで読み込み中…',f'id="goal-target">目標 {target:,} 回まであと {remain:,} 回！')
    s=s.replace('id="goal-pct">－%',f'id="goal-pct">{pct}%')
    s=s.replace('id="goal-remain">あと－回',f'id="goal-remain">あと{remain:,}回')
    s=s.replace('id="goal-bar"','id="goal-bar" style="width:'+str(pct)+'%"')
    s=s.replace('<div class="goal-actions">','<p class="br-help" id="goal-status" role="status">'+('最新の集計待ちです。表示は最後に確認できた記録です。' if goal.get('is_stale') else '公開目標シートの記録を表示しています。')+'</p><div class="goal-actions">',1)
    s=s.replace('`最終更新：${updated}`','`集計日：${updated}`')
    s=s.replace("document.getElementById('goal-updated').textContent = '読み込めませんでした';", "document.getElementById('goal-status').textContent = '再取得できなかったため、保存済みの記録を表示しています。';")
    s=s.replace('  <!-- NEWS -->','  <div class="section" style="padding-top:0;padding-bottom:0"><a class="btn-sub br-search-link" href="/start/">🌱 Podcastが初めての方へ</a></div>\n  <!-- NEWS -->',1)
    # Source audio is provided at the exact path the original fortune expects.
    player='''<section class="player-bar" id="player-bar" hidden aria-label="音声プレーヤー"><div class="wrap"><div class="player-inner"><a class="player-title" id="player-title" href="/episodes/"></a><audio id="site-audio" controls preload="none" aria-label="エピソードの音声"></audio><button class="player-close" id="player-close" aria-label="再生を停止して閉じる">×</button></div><p class="player-notice" id="player-notice" role="status"></p></div></section>'''
    s=s.replace('</body>',player+'\n</body>',1)
    s=s.replace("navigator.serviceWorker.register('sw.js')", "navigator.serviceWorker.register('/sw.js', { updateViaCache: 'none' })")
    return s
