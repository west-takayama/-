"""Draft new-episode notes from verified RSS metadata, once per episode ID."""
import hashlib
import json
from pathlib import Path
from refresh import save_json
ROOT=Path(__file__).resolve().parents[1]

def make_draft(episode):
    description=episode['description']
    digest=hashlib.sha256((episode['title']+'\n'+description).encode()).hexdigest()
    return {'episode_id':episode['id'],'source_hash':digest,'status':'draft','title':episode['title']+'｜配信ノート','source_url':episode['source'],'published_at_source':episode['published'],'cast':episode['cast'],'summary_source':description,'editorial_instructions':'公式概要にある事実だけを使い、聴くきっかけになる導入・2〜3個の見どころ・本人の体験を尋ねる問い・本編リンクを含む記事にする。音声未確認の発言、時刻、結論、体験、再生数を創作しない。概要の言い換えだけなら公開せず下書きに残す。','body':f"{episode['title']}\n\n今回の配信は、{episode['cast'] or 'ブリッジラジオのメンバー'}がお届けします。\n\n{description}\n\nあなたなら、どんなことを感じますか？感想や次に聴きたいテーマをお便りで教えてください。\n\n本編：/episodes/{episode['id']}/"}

def generate(episodes,root=ROOT):
    state_path=root/'data/blog-state.json'
    state=json.loads(state_path.read_text()) if state_path.exists() else {'known_ids':[]}
    known=set(state['known_ids']);fresh=[p for p in episodes if p['id'] not in known]
    # Do not turn an existing archive into 99 repetitive articles on first setup.
    if not known:fresh=episodes[:1]
    generated=[]
    for episode in fresh:
        file=root/'content/blog-drafts'/f"{episode['id']}.json"
        if not file.exists():save_json(file,make_draft(episode));generated.append(episode['id'])
    save_json(state_path,{'known_ids':sorted(known|{p['id'] for p in episodes})})
    return generated

if __name__=='__main__':
    episodes=json.loads((ROOT/'data/episodes.json').read_text())['episodes']
    print('New blog drafts:',len(generate(episodes)))
