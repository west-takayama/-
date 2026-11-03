"""Deterministic static site. No browser-time feed proxies or external build packages."""
from __future__ import annotations
from datetime import datetime
from html import escape
import json
from pathlib import Path
import re
import shutil
from original_home import original_home
from letters import letter_form
from goals import GOAL_SOURCE
from blogs import generate
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
BASE = 'https://spectacular-cuchufli-3e84ee.netlify.app'
SPOTIFY = 'https://open.spotify.com/show/7CS0NT2megKVd6CCC1V2EF'
APPLE = 'https://podcasts.apple.com/jp/podcast/id1864707587'
RSS = 'https://anchor.fm/s/10b7b57e4/podcast/rss'
FORM = 'https://docs.google.com/forms/d/e/1FAIpQLSea2bdr7tSewOsgCaq4NtdKIMvv6Krf1y3dvWhX0oqlqd0Lzg/viewform'
INTRO = '2000年代生まれの仲間たちが、恋愛、人間関係、日常のモヤモヤを本音で話す雑談ポッドキャスト。毎週水曜配信。'
SOCIALS = [('Spotify', SPOTIFY), ('Apple Podcasts', APPLE), ('YouTube', 'https://www.youtube.com/@ブリッジラジオ'), ('Instagram', 'https://www.instagram.com/bridge_radio/'), ('TikTok', 'https://www.tiktok.com/@bridgeradio2000'), ('X', 'https://x.com/bridge_radio00s')]
e = escape

def ep_path(item): return '/episodes/' + item['id'] + '/'
def date(item): return datetime.fromisoformat(item['published']).astimezone(ZoneInfo('Asia/Tokyo')).strftime('%Y.%m.%d')
def duration(item): return f"{round(item['duration']/60)}分" if item['duration'] else '音声配信'
def excerpt(item, limit=135):
    text = re.sub(r'^出演[:：][^\n]*\n?', '', item['description']).strip().replace('\n', ' ')
    return text[:limit] + ('…' if len(text)>limit else '')
def metadata(item):
    return f'<div class="meta"><time datetime="{e(item["published"])}">{date(item)}</time><span>{duration(item)}</span><span class="tag">{e(item["topics"][0])}</span></div>'
def link(url, text, cls='button', event='listen_click'):
    return f'<a href="{e(url)}" class="{cls}" target="_blank" rel="noopener noreferrer" data-track="{event}">{e(text)}</a>'
def play(item, sample=False):
    attr = 'data-sample="30"' if sample else ''
    return f'<button class="button primary" type="button" data-play="{e(item["audio"])}" data-title="{e(item["title"])}" data-id="{item["id"]}" data-url="{ep_path(item)}" {attr}>{"▷ 冒頭30秒ためし聴き" if sample else "▶ このサイトで聴く"}</button>'

def row(item):
    return f'''<article class="episode-row" data-episode data-search="{e((item['title']+' '+item['description']+' '+item['cast']).lower())}" data-topics="{e('|'.join(item['topics']))}"><div class="episode-num">{e('#'+item['number'] if item['number'] else 'SP')}</div><div>{metadata(item)}<h3><a href="{ep_path(item)}">{e(item['title'])}</a></h3><span class="meta">{e(item['cast'])}</span></div><a href="{ep_path(item)}" class="row-go" aria-label="{e(item['title'])}を聴く">この回を聴く ↗</a></article>'''

def shell(title, body, path='/', description=INTRO, schema=None):
    canonical = BASE + path
    structured = json.dumps(schema or {'@context':'https://schema.org','@type':'PodcastSeries','name':'ブリッジラジオ 00s','url':BASE+'/', 'description':INTRO,'webFeed':RSS,'image':BASE+'/icon-512.png','inLanguage':'ja','sameAs':[v for _,v in SOCIALS]},ensure_ascii=False).replace('<','\\u003c')
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="google-site-verification" content="093cUHRjF6xnzBV9GE1C8rGVyCU7qL0CWpq1r99fnDg"><link rel="canonical" href="{canonical}"><meta property="og:type" content="website"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{canonical}"><meta property="og:site_name" content="ブリッジラジオ 00s"><meta property="og:locale" content="ja_JP"><meta property="og:image" content="{BASE}/icon-512.png"><meta property="og:image:width" content="512"><meta property="og:image:height" content="512"><meta property="og:image:alt" content="ブリッジラジオ 00s ロゴ"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{BASE}/icon-512.png"><link rel="alternate" type="application/rss+xml" title="ブリッジラジオ 00s" href="{RSS}"><link rel="icon" href="/favicon.ico"><link rel="apple-touch-icon" href="/icon-192.png"><link rel="manifest" href="/manifest.json"><meta name="theme-color" content="#111210"><link rel="stylesheet" href="/assets/site.css"><script type="application/ld+json">{structured}</script><script defer src="/assets/site.js"></script><script defer src="/assets/analytics.js"></script><link rel="stylesheet" href="/assets/letters.css"><script defer src="/assets/letters.js"></script></head><body>
<a class="skip" href="#main">本文へスキップ</a><div class="wrap"><header class="site-header"><a href="/" class="brand"><img src="/icon-192.png" width="46" height="46" alt="">ブリッジラジオ<small>00s</small></a><nav class="nav" aria-label="メインメニュー"><a href="/episodes/">エピソード</a><a href="/#cast" class="desktop-nav">キャスト</a><a href="/#fortune" class="desktop-nav">占い</a><a href="/#fan" class="nav-letter">参加</a></nav></header><main id="main">{body}</main>
<nav class="subpage-nav" aria-label="下部メニュー"><a href="/">🏠<span>ホーム</span></a><a href="/#cast">🎤<span>キャスト</span></a><a href="/#blog">📝<span>ブログ</span></a><a href="/#fan">💌<span>参加</span></a></nav><footer class="footer"><div class="footer-top"><div><a href="/" class="brand">BRIDGE RADIO 00s</a><p>生活の解像度を、少しだけ上げる。</p></div><div class="socials">{''.join(link(url,name,'','follow_click') for name,url in SOCIALS)}</div></div><div class="footer-bottom"><span>© ブリッジラジオ 00s</span><span><a href="/blog/">ブログ</a>　 /　 <a href="/club/">ゆの基地</a>　 /　 <a href="/privacy/">プライバシー</a>　 /　 <a href="{RSS}">RSS</a></span></div></footer></div>
<section class="player-bar" id="player-bar" hidden aria-label="音声プレーヤー"><div class="wrap"><div class="player-inner"><a class="player-title" id="player-title" href="/episodes/"></a><audio id="site-audio" controls preload="none" aria-label="エピソードの音声"></audio><button class="player-close" id="player-close" aria-label="再生を停止して閉じる">×</button></div><p class="player-notice" id="player-notice" role="status"></p></div></section><noscript><p class="no-js-note wrap">各回のページから音声を再生できます。検索や30秒試聴にはJavaScriptを有効にしてください。</p></noscript></body></html>'''

def join(): return '<section class="join-band"><div><h2>そのモヤモヤ、聞かせて。</h2><p>恋愛のこと、仕事のこと、名前のない気持ち。あなたの話が、次のテーマになるかも。</p></div><a class="button" href="/participate/">お便り・テーマを送る ↗</a></section>'


def write(path, content):
    target = OUT / path.lstrip('/'); target.parent.mkdir(parents=True, exist_ok=True); target.write_text(content)

def build():
    snapshot = json.loads((ROOT/'data/episodes.json').read_text()); episodes = snapshot['episodes']
    if not episodes: raise ValueError('Cannot build without episodes')
    cast = json.loads((ROOT/'data/cast.json').read_text())
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(exist_ok=True)
    for name in ('icon-192.png','icon-512.png','ogp.png','favicon.ico','manifest.json','sw.js'):
        shutil.copy2(ROOT/name, OUT/name)
    shutil.copytree(ROOT/'assets', OUT/'assets', dirs_exist_ok=True)
    (OUT/'sounds').mkdir(exist_ok=True)
    for audio in ROOT.glob('yu[0-7].mp3'): shutil.copy2(audio, OUT/'sounds'/audio.name)
    (OUT/'data').mkdir(exist_ok=True)
    shutil.copy2(ROOT/'data/goal.json', OUT/'data/goal.json')
    articles=json.loads((ROOT/'content/articles.json').read_text())
    generate(episodes)
    snapshot=json.loads((ROOT/'data/goal.json').read_text())
    function_data=ROOT/'netlify/functions/lib/goal-snapshot.mjs';function_data.parent.mkdir(parents=True,exist_ok=True)
    function_data.write_text('export const sourceUrl = '+json.dumps(GOAL_SOURCE)+';\nexport const snapshot = '+json.dumps(snapshot,ensure_ascii=False)+';\n')
    write('index.html',original_home(episodes,cast,articles))
    filters = ['すべて','恋愛・人間関係','日常・暮らし','思い出・カルチャー','日々のモヤモヤ']
    archive = '<section class="page-intro"><div class="eyebrow">EPISODES</div><h1 class="page-title">今日、何の話を聴こう。</h1><p>気になる言葉やメンバーから、あなたに合う1本を。</p><div class="search-bar"><label class="skip" for="episode-search">エピソードを検索</label><input type="search" id="episode-search" placeholder="同棲、旅行、たそ…" autocomplete="off"></div><div class="filters">'+''.join(f'<button type="button" class="filter" data-filter="{e(x)}" aria-pressed="{str(i==0).lower()}">{e(x)}</button>' for i,x in enumerate(filters))+f'</div><p class="search-count" id="search-count" role="status">{len(episodes)}件のエピソード</p></section><section aria-label="エピソード一覧">'+''.join(row(x) for x in episodes)+'<p class="empty" id="empty-search" hidden>見つかりませんでした。別の言葉で探してみてください。</p></section>'
    write('episodes/index.html',shell('エピソード一覧｜ブリッジラジオ 00s', archive,'/episodes/'))
    for item in episodes:
        related = sorted((x for x in episodes if x['id'] != item['id']), key=lambda x: (bool(set(item['topics'])&set(x['topics'])), x['published']), reverse=True)[:3]
        body = f'''<div class="episode-layout"><article><nav class="breadcrumb" aria-label="パンくず"><a href="/">ホーム</a>　/　<a href="/episodes/">エピソード</a></nav>{metadata(item)}<h1 class="episode-heading">{e(item['title'])}</h1><p class="meta">{e(item['cast'])}</p><audio class="inline-player" controls preload="none" data-episode-id="{item['id']}" src="{e(item['audio'])}" aria-label="{e(item['title'])}">音声は<a href="{e(item['audio'])}">こちら</a>から聴けます。</audio><div class="share-row"><button class="button small" data-share="{BASE+ep_path(item)}" data-share-title="{e(item['title'])}">この回をシェア ↗</button><button class="button small" data-copy="{BASE+ep_path(item)}">リンクをコピー</button><span class="share-status" role="status"></span></div><div class="description">{e(item['description'])}</div><div class="actions"><a class="button" href="/participate/?episode={item['id']}">この回の感想を送る ↗</a>{link(item['source'],'配信元で聴く ↗')}</div><section class="related"><h2>こんな話も、どうですか。</h2>{''.join(row(x) for x in related)}</section></article><aside class="episode-sidebar"><img src="/icon-512.png" width="160" height="160" alt="ブリッジラジオ 00s" loading="lazy"><h2 style="font-size:17px">次の雑談も、ご一緒に。</h2><p>いつものアプリでフォローすると、新しいエピソードを見つけやすくなります。</p>{link(SPOTIFY,'Spotifyでフォロー','button primary','follow_click')}{link(APPLE,'Apple Podcastsで聴く','button','follow_click')}</aside></div>'''
        schema = {'@context':'https://schema.org','@type':'PodcastEpisode','@id':BASE+ep_path(item),'url':BASE+ep_path(item),'name':item['title'],'description':excerpt(item,500),'datePublished':item['published'],'duration':f"PT{item['duration']}S",'associatedMedia':{'@type':'AudioObject','contentUrl':item['audio'],'encodingFormat':'audio/mpeg'},'partOfSeries':{'@type':'PodcastSeries','name':'ブリッジラジオ 00s','url':BASE+'/'},'inLanguage':'ja','image':BASE+'/icon-512.png'}
        write(ep_path(item)+'index.html',shell(item['title']+'｜ブリッジラジオ 00s',body,ep_path(item),excerpt(item),schema))
    cast_body = '<section class="page-intro"><div class="eyebrow">THE VOICES</div><h1 class="page-title">声の向こうの、僕ら。</h1><p>気になるメンバーから、番組を好きになってもらえたら。</p></section><div class="cast-grid">'+''.join(f'<article class="cast-card" id="{p["id"]}"><span class="cast-icon" aria-hidden="true">{p["icon"]}</span><h2>{p["name"]}</h2><p>{e(p["bio"])}</p><blockquote>「{e(p["quote"])}」</blockquote><a class="button small" href="/participate/?to={p["id"]}">{p["name"]}にお便りを送る ↗</a></article>' for p in cast)+'</div>'+join()
    write('cast/index.html',shell('メンバー紹介｜ブリッジラジオ 00s',cast_body,'/cast/'))
    participate='<section class="page-intro"><div class="eyebrow">YOUR VOICE</div><h1 class="page-title">ひとこと、聞かせて。</h1><p>感想も、質問も、次に聴きたいテーマも。</p></section>'+letter_form(cast)
    write('participate/index.html',shell('お便り・テーマ募集｜ブリッジラジオ 00s',participate,'/participate/'))
    club = '<section class="page-intro"><h1 class="page-title">今日のブリッジ占い</h1><p>いつものホーム画面の占いへ移動します。</p><a class="button primary" href="/#fortune">占いを開く</a></section><script>location.replace("/#fortune")</script>'
    write('club/index.html',shell('今日のブリッジ占い｜ブリッジラジオ 00s',club,'/club/'))
    blogs = json.loads((ROOT/'data/blog.json').read_text()) if (ROOT/'data/blog.json').exists() else []
    article_cards=''.join(f'<article class="blog-item"><div class="meta">{a["published"][:10]} · 読みもの</div><h3><a href="/blog/{a["id"]}/">{e(a["title"])}</a></h3><p>{e(a["description"])}</p><a class="text-link" href="/blog/{a["id"]}/">続きを読む →</a></article>' for a in articles)
    blog='<section class="page-intro"><div class="eyebrow">BLOG</div><h1 class="page-title">声のつづきを、文字で。</h1><p>Podcastの入口と、配信の聴きどころ。</p></section>'+article_cards+'<h2>noteの更新</h2>'+''.join(f'<article class="blog-item"><h3>{link(p["url"],p["title"],"","blog_click")}</h3><p>{e(p["description"])}</p></article>' for p in blogs)
    write('blog/index.html',shell('ブログ・Podcastの聴き方｜ブリッジラジオ 00s',blog,'/blog/'))
    episode_by_id={x['id']:x for x in episodes}
    for a in articles:
        related=[episode_by_id[x] for x in a['episode_ids']]
        article_body='<nav class="breadcrumb"><a href="/blog/">ブログ</a></nav><article><h1 class="episode-heading">'+e(a['title'])+'</h1><p class="meta">'+a['published'][:10]+' · ブリッジラジオ 00s</p><div class="reading">'+''.join('<section><h2>'+e(section['heading'])+'</h2>'+''.join('<p>'+e(p)+'</p>' for p in section['paragraphs'])+'</section>' for section in a['sections'])+'</div><section class="related"><h2>この記事で紹介した回</h2>'+''.join(row(x) for x in related)+'</section><p class="helper">'+e(a['source_note'])+'</p><details class="helper"><summary>参照元</summary>'+''.join(f'<p><a href="{e(url)}" rel="noopener noreferrer">公式配信情報 {i+1} ↗</a></p>' for i,url in enumerate(a['source_urls']))+'</details></article>'+join()
        schema={'@context':'https://schema.org','@type':'BlogPosting','headline':a['title'],'description':a['description'],'datePublished':a['published'],'dateModified':a['published'],'author':{'@type':'Organization','name':'ブリッジラジオ 00s','url':BASE+'/'},'publisher':{'@type':'Organization','name':'ブリッジラジオ 00s','logo':{'@type':'ImageObject','url':BASE+'/icon-512.png'}},'mainEntityOfPage':BASE+'/blog/'+a['id']+'/','image':BASE+'/icon-512.png','inLanguage':'ja'}
        write('blog/'+a['id']+'/index.html',shell(a['title']+'｜ブリッジラジオ 00s',article_body,'/blog/'+a['id']+'/',a['description'],schema))
    picks=[episode_by_id[x] for x in articles[0]['episode_ids']]
    start='<section class="page-intro"><div class="eyebrow">START HERE</div><h1 class="page-title">初めてのPodcast、<br>気になる話から。</h1><p>番組を知らなくても大丈夫。恋愛、旅、子どもの頃の思い出。いまの気分に近い1本を選んでみてください。</p><a class="text-link" href="/blog/podcast-first-listen/">Podcastって何？聴き方を読む →</a></section>'+''.join(row(x) for x in picks)+'<div class="actions"><a class="button primary" href="/episodes/">すべての回から探す</a></div>'+join()
    write('start/index.html',shell('初めてのPodcast・おすすめの入口｜ブリッジラジオ 00s',start,'/start/'))
    privacy = '''<section class="page-intro"><div class="eyebrow">PRIVACY</div><h1 class="page-title">プライバシーについて</h1></section><article class="description"><h2>アクセス解析</h2>このサイトではGoogle Analyticsを利用し、ページの閲覧、音声の再生、配信サービスへの移動などを集計します。Cookie等が利用される場合があります。お便りの本文・ラジオネーム・公開可否、検索欄に入力した内容は、独自の計測イベントには含めません。<h2>音声の再生</h2>再生操作をすると、配信元の音声ファイルを読み込みます。配信サービス側で再生に関する情報が処理される場合があります。<h2>お便り</h2>お便りはGoogleフォームで受け付けます。確認画面へ進むと入力内容がGoogleに渡ります。番組内での紹介は選択された公開可否に従います。<h2>ブラウザー内の保存</h2>占いの結果はブラウザー内に保存します。お便りの下書きは同じタブに一時保存し、24時間を過ぎたデータは再訪時に削除します。「下書きを消す」から消すこともできます。確認画面へ進むまでは運営者へ送信しません。<h2>お問い合わせ</h2><a href="mailto:bridgeradio.2000@gmail.com">bridgeradio.2000@gmail.com</a></article>'''
    write('privacy/index.html',shell('プライバシー｜ブリッジラジオ 00s',privacy,'/privacy/'))
    write('404.html',shell('ページが見つかりません｜ブリッジラジオ 00s','<section class="page-intro"><h1 class="page-title">この道は、行き止まり。</h1><p>エピソード一覧から、聴きたい話を探してみてください。</p><a class="button primary" href="/episodes/">エピソードを探す</a></section>','/404.html'))
    paths=['/','/start/','/episodes/','/cast/','/blog/','/privacy/']+[ep_path(x) for x in episodes]+['/blog/'+a['id']+'/' for a in articles]
    write('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{e(BASE+p)}</loc></url>' for p in paths)+'</urlset>')
    write('robots.txt',f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
    write('data/episodes.json',json.dumps({'episodes':[{'id':x['id'],'title':x['title'],'path':ep_path(x)} for x in episodes]},ensure_ascii=False))
    write('data/cast.json',json.dumps([{'id':p['id'],'name':p['name'],'icon':p['icon']} for p in cast],ensure_ascii=False))
    # Public, source-grounded copy for publishing; never invent dialogue or timestamps.
    latest = episodes[0]; promo = ROOT/'promotion'; promo.mkdir(exist_ok=True)
    (promo/'latest.json').write_text(json.dumps({'episode_id':latest['id'],'published':latest['published'],'title':latest['title'],'url':BASE+ep_path(latest),'caption':f"🎙 ブリッジラジオ 00s\n{latest['title']}\n\n{excerpt(latest,180)}\n\n本編を聴く：{BASE+ep_path(latest)}?utm_source=social&utm_medium=organic&utm_campaign=episode_{latest['id']}\n\n#ブリッジラジオ #ポッドキャスト",'source':'Published episode title and description from the official RSS feed.','status':'draft'},ensure_ascii=False,indent=2)+'\n')
    print(f'Built {len(episodes)} episode pages, archive, sitemap, and promotion draft')

if __name__=='__main__': build()
