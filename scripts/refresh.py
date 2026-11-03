"""Refresh public podcast/note metadata; preserve the last good snapshot on errors."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from goals import GOAL_SOURCE, parse_goal
ROOT = Path(__file__).resolve().parents[1]
RSS = 'https://anchor.fm/s/10b7b57e4/podcast/rss'
NOTE = 'https://note.com/bridge_radio2000/rss'
ITUNES = '{http://www.itunes.com/dtds/podcast-1.0.dtd}'

class PlainText(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.blocked = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.blocked += 1
        if tag in ('p', 'br', 'li', 'div', 'h2', 'h3'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.blocked = max(0, self.blocked - 1)
        if tag in ('p', 'li', 'div'): self.parts.append('\n')
    def handle_data(self, data):
        if not self.blocked: self.parts.append(data)

def plain(value):
    p = PlainText(); p.feed(value or '')
    return '\n'.join(x.strip() for x in ''.join(p.parts).splitlines() if x.strip())

def safe_url(value):
    p = urlparse(value or '')
    return value if p.scheme == 'https' and p.netloc and not p.username else ''

def fetch(url):
    with urlopen(Request(url, headers={'User-Agent': 'BridgeRadioSite/2.0'}), timeout=30) as response:
        data = response.read(6_000_001)
        if len(data) > 6_000_000: raise ValueError('Feed exceeds size limit')
        return data

def parse_feed(data, now=None):
    if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
        raise ValueError('Unexpected XML declaration')
    channel = ET.fromstring(data).find('channel')
    if channel is None or 'ブリッジラジオ' not in (channel.findtext('title') or ''):
        raise ValueError('Unexpected podcast feed')
    now = now or datetime.now(timezone.utc)
    episodes, seen = [], set()
    for item in channel.findall('item'):
        title = plain(item.findtext('title'))
        guid = item.findtext('guid') or item.findtext('link')
        enc = item.find('enclosure')
        audio = safe_url(enc.get('url', '')) if enc is not None else ''
        if not title or not guid or not audio: continue
        published = parsedate_to_datetime(item.findtext('pubDate'))
        if published.tzinfo is None: published = published.replace(tzinfo=timezone.utc)
        if published > now: continue
        key = hashlib.sha256(guid.encode()).hexdigest()[:12]
        if key in seen: continue
        seen.add(key)
        description = plain(item.findtext('description'))
        description = re.split(r'▼感想|▼お便り|▼番組リンク', description)[0].strip()
        cast = re.search(r'^出演[:：]\s*([^\n]+)', description)
        duration = (item.findtext(ITUNES + 'duration') or '0').strip()
        try:
            seconds = 0
            for part in duration.split(':'): seconds = seconds * 60 + int(part)
        except ValueError: seconds = 0
        number = re.search(r'[#＃]\s*(\d+)', title)
        topics = [label for label, pattern in [
            ('恋愛・人間関係', '同棲|恋愛|デート|マッチング|モテ|友達|人間関係|結婚'),
            ('日常・暮らし', '旅行|旅|ホテル|沖縄|サイゼ|寿司|睡眠|ご飯|料理|ジム|買い物'),
            ('思い出・カルチャー', '学校|運動会|映画|野球|サッカー|ゲーム|平成|音楽|アニメ')]
            if re.search(pattern, title)] or ['日々のモヤモヤ']
        episodes.append({'id': key, 'title': title, 'number': number.group(1) if number else '',
            'description': description, 'cast': cast.group(1).strip() if cast else '',
            'published': published.isoformat(), 'duration': seconds, 'audio': audio,
            'source': safe_url(item.findtext('link')), 'topics': topics,
            'explicit': item.findtext(ITUNES + 'explicit') == 'true'})
    episodes.sort(key=lambda e: (e['published'], e['id']), reverse=True)
    if not episodes: raise ValueError('No published audio episodes; old snapshot retained')
    return {'show': channel.findtext('title'), 'feed': RSS, 'episodes': episodes}

def save_json(path, value):
    text = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    if path.exists() and path.read_text() == text: return False
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp'); temp.write_text(text); temp.replace(path)
    return True

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--feed-file'); args = parser.parse_args()
    snapshot = parse_feed(Path(args.feed_file).read_bytes() if args.feed_file else fetch(RSS))
    old_path = ROOT / 'data/episodes.json'
    if old_path.exists():
        old = json.loads(old_path.read_text())
        if len(snapshot['episodes']) < len(old['episodes']) * .5:
            raise ValueError('Feed unexpectedly lost over half its episodes; retained old snapshot')
    save_json(old_path, snapshot)
    try:
        note = ET.fromstring(fetch(NOTE))
        posts = [{'title': plain(i.findtext('title')), 'url': safe_url(i.findtext('link')),
                  'description': plain(i.findtext('description'))[:180],
                  'published': i.findtext('pubDate')} for i in note.findall('./channel/item')[:5]]
        if posts: save_json(ROOT / 'data/blog.json', posts)
    except Exception as exc:
        print('note refresh skipped; retaining snapshot:', type(exc).__name__)
    try:
        save_json(ROOT/'data/goal.json', parse_goal(fetch(GOAL_SOURCE)))
    except Exception as exc:
        print('Goal refresh skipped; retaining snapshot:', type(exc).__name__)
    print(f"Validated {len(snapshot['episodes'])} published episodes")

if __name__ == '__main__': main()
