import json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import engine,admission
from common import *
from receipts import execution,Stream
from scoring import endpoint
from worlds import messages

class AdmissionIntegrationTests(unittest.TestCase):
 def test_raw_receipt_to_all_error_dataset_and_retention_only(self):
  with tempfile.TemporaryDirectory() as d:
   base=Path(d);secret=os.urandom(32);auth=dict(study_id=STUDY_ID,adapter_sha256='adapter',training_eligible_pools=['H1','V1']);cs=[]
   with patch.object(engine,'PRIVATE',base),patch.object(admission,'PRIVATE',base),patch.object(admission,'P',base),patch.object(engine,'key',return_value=secret),patch.object(admission,'key',return_value=secret),patch.object(engine,'authorization',return_value=auth),patch.object(engine,'freeze_commit',return_value='b'*40),patch.object(engine.stack,'identity',return_value='adapter'),patch.object(admission,'raw_commit',return_value='a'*40):
    tape=engine.Tape('harvest1','C0','H1')
    for i in range(3):
     visible=dict(actuators=['A0','B0','C0','D0'],sensors=['E0','F0','G0','H0'],history=[['RESET','0000']],candidate_action='A0');c=dict(id=f'H1-{i}',pool='H1',cycle=1,world_hash=sha(i),family='synthetic',causal_depth=1,delay_length=1,hidden_components=1,visible=visible);cs.append(c);actual={s:1 for s in visible['sensors']};prediction=canon({'next_observation':actual}) if i==2 else 'incorrect response';call=f'batch{i}'
     req=tape.append('REQUEST_BATCH',dict(id=call,case_ids=[c['id']],visible=[visible],messages=[messages(visible)]));tape.append('PREDICTION_BATCH',dict(id=call,request_receipt_sha256=sha(req),outputs=[dict(text=prediction)]))
     record=execution(c,'C0','adapter',visible,'A0',prediction,actual,1,sha(auth));record.update(id=c['id'],call_id=call,output_index=0);tape.append('EXECUTED_TRANSITION',record)
    write_rows(base/'prior-temporal-training-replay.jsonl',[dict(source='prior_temporal_training_replay',case_id='temporal-training',messages=[],target='{}')]*512)
    with patch.object(admission,'cases',return_value=cs):
     scored=admission.score_prediction_tape(tape,'harvest1');first=filehash(base/'C0-H1-scored.jsonl');self.assertEqual(scored,admission.score_prediction_tape(tape,'harvest1'));self.assertEqual(first,filehash(base/'C0-H1-scored.jsonl'))
     data,composition=admission.construct_training(1,{('C0','H1'):tape},scored);self.assertEqual(composition['errors'],2);self.assertEqual(composition['composition'],dict(causal_error=2,causal_correct_replay=2,prior_temporal_training_replay=512));self.assertEqual({x['case_id'] for x in data if x['source']=='causal_error'},{'H1-0','H1-1'});self.assertTrue(all('incorrect response' not in canon(x) for x in data))
    tape.stream.verify()
if __name__=='__main__':unittest.main()
