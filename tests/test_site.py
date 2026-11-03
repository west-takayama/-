from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import re
from pathlib import Path
import sys
import unittest
from urllib.parse import urlparse, unquote
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from refresh import parse_feed, plain, safe_url

class Document(HTMLParser):
    def __init__(self,text):
        super().__init__();self.links=[];self.meta={};self.canonical=[];self.ids=[];self.h1=0;self.scripts=[];self.in_schema=False
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='h1':self.h1+=1
        if a.get('id'):self.ids.append(a['id'])
        if tag in ('a','link') and a.get('href'):self.links.append(a['href'])
        if tag in ('img','script') and a.get('src'):self.links.append(a['src'])
        if tag=='meta':self.meta[a.get('property',a.get('name',''))]=a.get('content')
        if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
        if tag=='script' and a.get('type')=='application/ld+json':self.in_schema=True
    def handle_endtag(self,tag):
        if tag=='script':self.in_schema=False
    def handle_data(self,data):
        if self.in_schema:self.scripts.append(json.loads(data))

class FeedTests(unittest.TestCase):
    def feed(self,items):return ('<rss><channel><title>ブリッジラジオ</title>'+items+'</channel></rss>').encode()
    def item(self,guid='one',date='Mon, 02 Nov 2026 00:00:00 GMT',url='https://example.com/audio.mp3'):
        return f'<item><title>テスト #1</title><guid>{guid}</guid><pubDate>{date}</pubDate><enclosure url="{url}"/><description>&lt;script&gt;bad()&lt;/script&gt;&lt;p&gt;内容&lt;/p&gt;</description></item>'
    def test_published_only_and_duplicate_guids(self):
        parsed=parse_feed(self.feed(self.item()+self.item()+self.item('future','Tue, 03 Nov 2026 00:00:00 GMT')),datetime(2026,11,2,12,tzinfo=timezone.utc))
        self.assertEqual(len(parsed['episodes']),1)
        self.assertEqual(parsed['episodes'][0]['description'],'内容')
    def test_no_unsafe_media_urls_or_empty_feeds(self):
        with self.assertRaises(ValueError):parse_feed(self.feed(self.item(url='javascript:alert(1)')))
        with self.assertRaises(ValueError):parse_feed(b'<rss><channel><title>Other show</title></channel></rss>')
        with self.assertRaises(ValueError):parse_feed(b'<!DOCTYPE rss><rss/>')
        self.assertEqual(safe_url('https://user:pass@example.com/'),'')
    def test_plain_text_keeps_paragraphs_and_escapes(self):
        self.assertEqual(plain('<p>A &amp; B</p><p>C</p>'),'A & B\nC')

class SiteTests(unittest.TestCase):
    def test_original_home_design_and_fortune_preserved(self):
        original=(ROOT/'index.html').read_text()
        built=(ROOT/'dist/index.html').read_text()
        # The homepage's established design and the full fortune are user requirements.
        for start,end in [('<style>','</style>'),('<!-- HOROSCOPE -->','<!-- GOAL TRACKER -->'),('// DAILY QUOTE','// GOAL TRACKER')]:
            expected=original.split(start,1)[1].split(end,1)[0]
            actual=built.split(start,1)[1].split(end,1)[0]
            self.assertEqual(actual,expected)
        original_nav=re.search(r'<nav class="nav".*?</nav>',original,re.S)
        self.assertIsNotNone(original_nav)
        self.assertIn(original_nav.group(),built)
        self.assertIn('const MAX_DRAWS = 3;',built)
        self.assertEqual((ROOT/'ogp.png').read_bytes(),(ROOT/'dist/ogp.png').read_bytes())
        for i in range(8):
            self.assertEqual((ROOT/f'yu{i}.mp3').read_bytes(),(ROOT/f'dist/sounds/yu{i}.mp3').read_bytes())

    def test_every_internal_link_and_metadata(self):
        pages=list((ROOT/'dist').rglob('*.html'))
        self.assertGreater(len(pages),10)
        for file in pages:
            with self.subTest(page=str(file.relative_to(ROOT))):
                text=file.read_text();doc=Document(text)
                self.assertEqual(doc.h1,1)
                self.assertEqual(len(doc.canonical),1)
                self.assertTrue(doc.meta.get('description'))
                self.assertTrue(doc.meta.get('og:image'))
                self.assertEqual(len(doc.ids),len(set(doc.ids)))
                self.assertTrue(doc.scripts)
                for href in doc.links:
                    p=urlparse(href)
                    if p.scheme or p.netloc or not p.path:continue
                    local=ROOT/'dist'/unquote(p.path.lstrip('/')) if p.path.startswith('/') else file.parent/unquote(p.path)
                    if local.is_dir():local=local/'index.html'
                    self.assertTrue(local.exists(),f'Broken internal link {href} on {file}')
    def test_episode_pages_match_feed_and_sitemap(self):
        episodes=json.loads((ROOT/'data/episodes.json').read_text())['episodes']
        sitemap=ET.parse(ROOT/'dist/sitemap.xml')
        locs={x.text for x in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
        for item in episodes:
            page=ROOT/'dist/episodes'/item['id']/'index.html'
            doc=Document(page.read_text());schema=doc.scripts[0]
            self.assertEqual(schema['name'],item['title'])
            self.assertEqual(schema['associatedMedia']['contentUrl'],item['audio'])
            self.assertIn(doc.canonical[0],locs)
    def test_no_fictional_vote_totals_or_proxy_dependencies(self):
        for path in (ROOT/'dist').rglob('*.html'):
            text=path.read_text()
            for bad in ['128票','203票','api.allorigins','corsproxy.io','rss2json.com']:
                self.assertNotIn(bad,text)
    def test_public_output_excludes_source_and_private_material(self):
        for name in ['.git','scripts','tests','files.zip','.env','.github']:
            self.assertFalse((ROOT/'dist'/name).exists())

if __name__=='__main__':unittest.main()
