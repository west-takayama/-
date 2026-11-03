import subprocess
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from daily_ops import execute,plan_commands

class DailyOperationsTests(unittest.TestCase):
    def test_failed_refresh_never_builds_or_publishes(self):
        called=[]
        def runner(command,**kwargs):
            called.append(command);return subprocess.CompletedProcess(command,1,'unavailable','')
        steps,success=execute(plan_commands(),runner)
        self.assertFalse(success);self.assertEqual(len(called),1);self.assertEqual(steps[-1]['stage'],'refresh')
    def test_validation_failure_stops_remaining_steps(self):
        def runner(command,**kwargs):return subprocess.CompletedProcess(command,1 if 'unittest' in command else 0,'','')
        steps,success=execute(plan_commands(),runner)
        self.assertFalse(success);self.assertEqual(len(steps),3)
    def test_source_warning_is_visible_despite_success(self):
        def runner(command,**kwargs):return subprocess.CompletedProcess(command,0,'Goal refresh skipped; retaining snapshot: TimeoutError','')
        steps,success=execute([('refresh',['refresh'])],runner)
        self.assertTrue(success);self.assertTrue(steps[0]['warnings'])
    def test_timeout_does_not_advance(self):
        def runner(command,**kwargs):raise subprocess.TimeoutExpired(command,180)
        steps,success=execute(plan_commands(),runner)
        self.assertFalse(success);self.assertEqual(len(steps),1);self.assertEqual(steps[0]['error_type'],'TimeoutExpired')

if __name__=='__main__':unittest.main()
