import json
from pathlib import Path
import sys
import tempfile
import unittest
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from goals import parse_goal
from blogs import generate

class GoalTests(unittest.TestCase):
    def test_accepts_quoted_counts_and_preserves_measured_date(self):
        result=parse_goal('現在の再生数,目標,最終更新\n"4,800","10,000",2026.5/29 21:25\n',datetime(2026,11,2,tzinfo=timezone.utc))
        self.assertEqual(result['current'],4800)
        self.assertEqual(result['target'],10000)
        self.assertEqual(result['measured_at'],'2026-05-29T21:25:00+09:00')
        self.assertTrue(result['is_stale'])
    def test_rejects_bad_counts_dates_and_wrong_sheet(self):
        for row in ['-1,10000,2026.5/29 21:25','12.5,10000,2026.5/29 21:25','4800,0,2026.5/29 21:25','4800,10000,2026.2/30 21:25','4800,10000,2099.1/1 00:00','4800,10000,']:
            with self.subTest(row=row),self.assertRaises(ValueError):parse_goal('現在の再生数,目標,最終更新\n'+row)
        with self.assertRaises(ValueError):parse_goal('followers,target,date\n1,2,2026-01-01')
    def test_goal_is_visible_without_javascript(self):
        text=(ROOT/'dist/index.html').read_text()
        goal=json.loads((ROOT/'data/goal.json').read_text())
        self.assertIn(f'id="goal-count">{goal["current"]:,}<span>/ {goal["target"]:,}</span>',text)
        self.assertIn('集計日：'+goal['updated'],text)
        if goal.get('is_stale'):self.assertIn('最新の集計待ち',text)

class BlogTests(unittest.TestCase):
    def test_new_episode_drafts_are_idempotent_and_not_mass_generated(self):
        episodes=json.loads((ROOT/'data/episodes.json').read_text())['episodes']
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            self.assertEqual(generate(episodes,root),[episodes[0]['id']])
            self.assertEqual(generate(episodes,root),[])
            fresh={**episodes[0],'id':'brand-new-episode'}
            self.assertEqual(generate([fresh]+episodes,root),['brand-new-episode'])
            self.assertEqual(len(list((root/'content/blog-drafts').glob('*.json'))),2)
    def test_only_edited_articles_are_published(self):
        articles=json.loads((ROOT/'content/articles.json').read_text())
        for a in articles:
            content=(ROOT/'dist/blog'/a['id']/'index.html').read_text()
            self.assertIn('BlogPosting',content)
            self.assertIn(a['source_note'],content)
        self.assertFalse((ROOT/'dist/content').exists())
        self.assertFalse((ROOT/'dist/ops').exists())
        self.assertFalse((ROOT/'dist/netlify').exists())
    def test_form_and_analytics_keep_private_text_out_of_events(self):
        text=(ROOT/'dist/index.html').read_text()
        self.assertIn('id="letter-form"',text)
        self.assertIn('for="letter-body"',text)
        self.assertIn('id="letter-options"',text)
        self.assertIn('次のGoogleフォームで「送信」を押すと届きます',text)
        self.assertNotIn("gtag('config'",text)
        code=(ROOT/'assets/analytics.js').read_text()
        self.assertIn("if(location.hostname!=='spectacular-cuchufli-3e84ee.netlify.app')return",code)

if __name__=='__main__':unittest.main()
