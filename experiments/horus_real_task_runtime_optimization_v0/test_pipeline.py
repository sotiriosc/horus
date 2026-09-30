"""Entire synthetic pipeline, no runtime/model/network calls, no scientific evidence."""
import contextlib,io,json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from . import worker,postflight
from .runtime import PUBLIC as SOURCE,write,sha
from .score import summarize,gates

class PipelineTest(unittest.TestCase):
 def test_full_pipeline_and_authentication_replay(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);public=root/'research/horus-real-task-runtime-optimization-v0';private=root/'private';shutil.copytree(SOURCE,public)
   # Test-only reference values, never scientific reference or Memory.
   ref=dict(status='PASS',workloads={f'P{p}-{j}':dict(reference_seconds=10,output_sha256=sha(b'{}')) for p in range(4) for j in range(3)})
   write(public/'references.json',ref);write(public/'lineage.json',dict(remote_refs={},local_refs={},latest_base='SYNTHETIC'))
   def measure(action,w,request,reference,path):
    path.mkdir(parents=True);m=dict(action=action,valid=True,wall_seconds={'HOLD':10,'ADVANCE':5,'RETREAT':12}[action],error=None,resource_violation=False,output_sha256=sha(b'{}'),output_bytes=2,finish_reason='stop',prompt_tokens=1,completion_tokens=1,timings={},launch_seconds=1,full_gpu_residency=True,peak_vram_mib=1000,reference_match=True,structural_valid=True,executor_total_seconds=1)
    write(path/'execution-measurement.json',m);(path/'execution-final.txt').write_bytes(b'{}');write(path/'termination.json',dict(exit_status=-15));return m
   class Client:
    def generate(self,r):
     p=json.loads(r['prompt']);positive=[a for a,v in p['grounded_assessments'].items() if any(x['consequence']==1 for x in v.get('recent_window',[]))]
     return dict(raw_output=json.dumps({'selected_action':positive[0] if positive else 'HOLD'}),transport_error=None,response_metadata={'prompt_eval_count':1,'eval_count':1})
   def git(args,**kw):
    if args[1]=='show':return (public/'references.json').read_bytes()
    if args[1] in ('ls-remote','for-each-ref'):return b''
    if args[1]=='ls-tree':return b'initial.py\n'
    raise AssertionError(args)
   with contextlib.ExitStack() as stack:
    for module in (worker,postflight):
     for name,value in [('PUBLIC',public),('PRIVATE',private),('ROOT',root),('guard',lambda _:dict(status='PASS'))]:stack.enter_context(patch.object(module,name,value))
    stack.enter_context(patch.object(worker,'measure_action',measure));stack.enter_context(patch.object(worker,'ModelClient',Client));stack.enter_context(patch.object(worker,'park_ordinary',lambda:None));stack.enter_context(patch('subprocess.check_output',side_effect=git));stack.enter_context(patch('socket.socket.connect',side_effect=AssertionError('network forbidden')))
    with contextlib.redirect_stdout(io.StringIO()):
     worker.stage('SYNTHETIC',0);worker.stage('SYNTHETIC',1);postflight.main('SYNTHETIC')
   rows=[json.loads(f.read_text()) for f in (public/'raw').glob('*.json')];arms={a:summarize([r for r in rows if r['arm']==a]) for a in 'ABC'}
   self.assertEqual(len(rows),72);self.assertEqual(arms['A']['E_acquisitions'],4);self.assertEqual(arms['B']['E_acquisitions'],0)
   self.assertEqual(gates(arms,True)['classification'],'E_ADDS_REAL_TASK_BENEFIT')
   self.assertEqual(json.loads((public/'postflight.json').read_text())['authorization_events'],48)
if __name__=='__main__':unittest.main()
