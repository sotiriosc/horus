"""Zero-inference reconstruction of a prospectively mandated protocol stop."""
import argparse,collections,hashlib,json,sys,tempfile,subprocess
from pathlib import Path
P=Path('/home/sotiriosc/horus-active-causal-experimentation-v0/research/horus-active-causal-experimentation-v0');sys.path.insert(0,str(P))
from common import *
from receipts import Stream
from campaign import collect
from interface import strict_json
from machines import PROBES
RAW_COMMIT='de596c5a037b4238a39d852066404b5a83f406b1'
def audit(output):
 raw=json.loads(subprocess.check_output(['git','show',RAW_COMMIT+':research/horus-active-causal-experimentation-v0/raw-freeze.json'],cwd=ROOT))
 assert raw['status']=='RAW_PARTIAL_PROTOCOL_FAILURE_UNSCORED'
 private=ASSETS/'private';path=private/'campaign-signed.jsonl'
 assert filehash(path)==raw['private_raw_sha256'] and filehash(private/'worlds.jsonl')==raw['private_worlds_sha256']
 key=(private/'authority.key').read_bytes();stream=Stream(path,key);stream.verify()
 intents={e['record']['id']:e['record'] for e in stream.records if e['kind']=='MODEL_INTENT'}
 responses={e['record']['id']:e['record']['result'] for e in stream.records if e['kind']=='MODEL_RESPONSE'}
 assert set(intents)==set(responses)
 worlds=[json.loads(x) for x in (private/'worlds.jsonl').read_text().splitlines()]
 auth=dict(study='Horus Active Causal Experimentation v0',method_freeze_sha=raw['method_freeze_sha'],world_freeze_sha=raw['world_freeze_sha'],operation='frozen discovery and prediction only; no training',adapter_sha256=ADAPTER_SHA)
 class ReplayWorker:
  calls=0
  def call(self,ident,msgs):
   self.calls+=1;assert intents[ident]['messages']==msgs
   assert intents[ident]['authorization']==auth
   assert intents[ident]['semantic_messages_sha256']==sha(msgs)==responses[ident]['semantic_messages_sha256']
   return responses[ident]
 replay=ReplayWorker()
 with tempfile.TemporaryDirectory() as d:
  reconstructed=Stream(Path(d)/'reconstructed.jsonl',key)
  try:collect(worlds,reconstructed,replay,auth,progress=False)
  except RuntimeError as e:assert str(e)=='Invalid discovery selection; scientific campaign terminated'
  else:raise AssertionError('Mandated failure not reproduced')
  reconstructed.verify();assert reconstructed.path.read_bytes()==path.read_bytes()
 # Independently validate the rendered HF content and token decoding.
 from transformers import AutoTokenizer
 tok=AutoTokenizer.from_pretrained('/mnt/d/horus-research-assets/qwen3-14b-qlora-v0/231c69a380487f6c0e52d02dcf0d5456d1918201',local_files_only=True)
 for ident,r in responses.items():
  rendered=tok.apply_chat_template(intents[ident]['messages'],tokenize=False,add_generation_prompt=True,enable_thinking=False)
  assert hashlib.sha256(rendered.encode()).hexdigest()==r['prompt_sha256']
  assert len(tok.encode(rendered,add_special_tokens=False))==r['prompt_tokens']
  assert tok.decode(r['generated_token_ids'],skip_special_tokens=True)==r['text']
 final=stream.records[-1];assert final['kind']=='PROTOCOL_FAILURE'
 failure_id=final['record']['id'].removesuffix(':failure')
 text=responses[failure_id]['text'];data=json.loads(intents[failure_id]['messages'][1]['content'])
 w=next(w for w in worlds if w['id']==failure_id.split(':')[0])
 selected=strict_json(text)
 assert set(selected)=={'probe'} and type(selected['probe']) is list
 assert all(type(a) is str and a in w['actuators'] for a in selected['probe'])
 ap=tuple(w['actuators'].index(a) for a in selected['probe'])
 assert ap in PROBES and selected['probe'] not in data['allowed_probes']
 reserved=ap in tuple(tuple(p) for p in w['reserved'])
 assert reserved
 assert not any(e['kind']=='EXECUTED_PROBE' and e['record']['id']==failure_id for e in stream.records)
 receipts=[e['record'] for e in stream.records if e['kind']=='EXECUTED_PROBE']
 counts=collections.Counter((r['world_id'],r['arm']) for r in receipts)
 calls=collections.Counter(ident.split(':')[2] for ident in responses)
 discovery_valid=len([k for k in responses if ':discovery:' in k])-1
 report=dict(status='PROTOCOL_FAILURE_CONFIRMED',classification='ACTIVE_CAUSAL_STUDY_TERMINATED_INVALID_DISCOVERY_SELECTION',raw_freeze_commit=RAW_COMMIT,raw_sha256=raw['private_raw_sha256'],failure_call_id=failure_id,failure_category='RESERVED_SEALED_QUERY_SELECTED',invalid_probe_executed=False,reserved_outcome_exposed=False,completed_model_calls=len(responses),valid_active_discovery_choices=discovery_valid,invalid_active_discovery_choices=1,completed_sealed_predictions=calls['sealed'],completed_control_predictions=calls['control-prediction'],executed_discovery_probes=len(receipts),discovery_counts=[dict(world_id=k[0],arm=k[1],executed=v) for k,v in sorted(counts.items())],fully_completed_matched_worlds=sum(counts[w['id'],'P']==12 and counts[w['id'],'A']==12 and sum(ident.startswith(w['id']+':') and ':sealed:' in ident for ident in responses)==10 for w in worlds if w['cohort']=='primary'),planned_primary_worlds=120,planned_control_worlds=40,planned_prediction_endpoints_per_arm=600,actual_prediction_endpoints_by_arm={a:sum(':'+a+':sealed:' in ident for ident in responses) for a in ['P','A']},primary_gate='NOT_EVALUABLE_PROTOCOL_FAILURE',selection_gate='NOT_EVALUABLE_PROTOCOL_FAILURE',control_gate='NOT_EVALUABLE_PROTOCOL_FAILURE',scientific_correctness_and_information_metrics='NOT_SCORED_INCOMPLETE_REGISTERED_POPULATION',receipt_authentication='PASS',byte_identical_execution_receipt_replay='PASS',exact_semantic_prompt_reconstruction='PASS',exact_rendered_template_hash_and_token_decode='PASS',oracle_boundary='PASS',sealing_boundary='PASS',ambiguous_incomplete_requests=0,new_model_calls_during_replay=0,repairs=0,retries=0,substitute_probes=0,training_steps=0,interpretation='This is an interface/protocol failure, not a completed negative comparison of active and passive evidence acquisition.')
 save(output,report);print(canon(report))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);args=a.parse_args();audit(args.output)
