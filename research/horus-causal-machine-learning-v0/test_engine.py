import json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import engine
from common import canon,sha,STUDY_ID
from receipts import Stream
from dsl import Circuit
class FakeTokenizer:
 def encode(self,s,add_special_tokens=False):return list(s.encode())
class EngineTests(unittest.TestCase):
 def test_wrong_durable_response_is_reused_without_retry(self):
  with tempfile.TemporaryDirectory() as d:
   secret=os.urandom(32);auth={'study_id':STUDY_ID}
   def infer(model,tok,requests,enabled):
    import hashlib
    return [dict(text='wrong malformed response',prompt_sha256=hashlib.sha256(canon(x).encode()).hexdigest()) for x in requests]
   with patch.object(engine,'PRIVATE',Path(d)),patch.object(engine,'key',return_value=secret),patch.object(engine,'authorization',return_value=auth),patch.object(engine,'freeze_commit',return_value='a'*40),patch.object(engine.stack,'identity',return_value='model'),patch.object(engine.stack.runtime,'prompt',side_effect=lambda tok,m:canon(m)),patch.object(engine.stack.runtime,'infer',side_effect=infer) as call:
    tape=engine.Tape('harvest1','C0','H1');msg=[[dict(role='user',content='synthetic qualification fixture')]];visible=[{'actuators':['A0'],'sensors':['S0'],'history':[['RESET','0']],'candidate_action':'A0'}]
    one=tape.predict(None,FakeTokenizer(),'batch',['x'],msg,visible);two=tape.predict(None,FakeTokenizer(),'batch',['x'],msg,visible);self.assertEqual(one,two);self.assertEqual(call.call_count,1)
    visible[0]['history'].append(['A0','1']);tape.stream.verify() # snapshots do not change with live histories
    tape2=engine.Tape('harvest1','C0','H1');original=[dict(visible[0],history=[['RESET','0']])];self.assertEqual(tape2.predict(None,FakeTokenizer(),'batch',['x'],msg,original),one);self.assertEqual(call.call_count,1)
 def test_signed_record_is_snapshot_of_mutable_inputs(self):
  with tempfile.TemporaryDirectory() as d:
   stream=Stream(Path(d)/'stream.jsonl',os.urandom(32));record={'history':[]};stream.append('REQUEST',record);record['history'].append('later');self.assertEqual(stream.verify()[0]['record']['history'],[])
if __name__=='__main__':unittest.main()
