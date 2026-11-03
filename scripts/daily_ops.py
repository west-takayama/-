"""Run one daily maintenance cycle. Never publish after a failed stage."""
from __future__ import annotations
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'ops/last-run.json'

def load(path,default):
    return json.loads(path.read_text()) if path.exists() else default

def plan_commands(python=sys.executable):
    return [('refresh',[python,'scripts/refresh.py']),('build',[python,'scripts/build.py']),
            ('validate_pages',[python,'-m','unittest','discover','-s','tests','-v']),
            ('validate_behaviour',['node','--test','tests/goal.test.mjs','tests/letters.test.mjs'])]

def execute(commands,runner=subprocess.run):
    steps=[]
    for name,command in commands:
        try:
            result=runner(command,cwd=ROOT,text=True,capture_output=True,timeout=180)
            output=(result.stdout or '')+'\n'+(result.stderr or '')
            skipped=[line.strip() for line in output.splitlines() if 'refresh skipped; retaining snapshot:' in line]
            steps.append({'stage':name,'status':'passed' if result.returncode==0 else 'failed','warnings':skipped})
            if result.returncode:
                print(output[-6000:])
                return steps,False
        except (subprocess.TimeoutExpired,OSError) as error:
            steps.append({'stage':name,'status':'failed','error_type':type(error).__name__})
            return steps,False
    return steps,True

def main():
    previous=load(ROOT/'data/episodes.json',{'episodes':[]})['episodes']
    before={x['id'] for x in previous}
    before_drafts={p.stem for p in (ROOT/'content/blog-drafts').glob('*.json')}
    steps,success=execute(plan_commands())
    after=load(ROOT/'data/episodes.json',{'episodes':[]})['episodes']
    after_drafts={p.stem for p in (ROOT/'content/blog-drafts').glob('*.json')}
    report={'checked_at':datetime.now(ZoneInfo('Asia/Tokyo')).isoformat(timespec='seconds'),
            'timezone':'Asia/Tokyo','status':'passed' if success else 'failed','steps':steps,
            'episode_count':len(after),'latest_episode_id':after[0]['id'] if after else None,
            'new_episode_ids':sorted({x['id'] for x in after}-before),
            'new_blog_draft_ids':sorted(after_drafts-before_drafts),
            'goal':load(ROOT/'data/goal.json',{}),
            'publication_status':'validated_not_published' if success else 'blocked_by_validation',
            'note':'This run never sends messages or publishes. Workflow commits only after all validations pass.'}
    REPORT.parent.mkdir(exist_ok=True)
    tmp=REPORT.with_suffix('.tmp');tmp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');tmp.replace(REPORT)
    summary='## Bridge Radio daily operations\n\n'+f"Result: {report['status']}\n\nEpisodes: {len(after)}; new episode IDs: {len(report['new_episode_ids'])}; new drafts: {len(report['new_blog_draft_ids'])}.\n\n"
    summary+='\n'.join('- '+s['stage']+': '+s['status']+(' (source refresh retained snapshot)' if s.get('warnings') else '') for s in steps)+'\n\nPublication is a separate step; this report does not prove live deployment.\n'
    if os.getenv('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as stream:stream.write(summary)
    print(summary)
    return 0 if success else 1

if __name__=='__main__':sys.exit(main())
