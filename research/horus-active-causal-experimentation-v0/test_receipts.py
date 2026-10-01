import tempfile,json
from pathlib import Path
from receipts import Stream,experiment
from common import *
from study_stats import mcnemar,paired_sign,control_order
from interface import parse_probe
with tempfile.TemporaryDirectory() as d:
 p=Path(d)/'synthetic.jsonl';s=Stream(p,b'non-production-synthetic-key-0000')
 before=[];obs=[{'S':1}];after=[dict(experiment=1,probe=['K'],observations=obs)]
 r=experiment(dict(id='SYNTHETIC',world_hash=sha('SYNTHETIC')),'A',1,['K'],obs,before,after,{'S':0},{'synthetic':True})
 s.append('EXECUTED_PROBE',r);obs[0]['S']=0
 assert s.records[0]['record']['complete_observed_trace']==[{'S':1}]
 assert s.verify()==s.records
 text=p.read_text();p.write_text(text.replace('SYNTHETIC','TAMPERED'))
 try:Stream(p,s.secret)
 except Exception:pass
 else:raise AssertionError('Tampered receipt authenticated')
assert mcnemar([False]*6,[True]*6)['p']==.03125
assert paired_sign([1]*7)['p']==.0078125
assert paired_sign([0]*120)['p']==1
try:parse_probe('{"probe":["K"],"probe":["K"]}',[['K']])
except ValueError:pass
else:raise AssertionError('Duplicate key accepted')
assert control_order(['invalid','{"predicted_observations":[{"S":0},{"S":0},{"S":1}]}'],['S'],{'S':1})==[1,0]
save(P/'receipt-tests.json',dict(status='PASS',preserved_horus_authentication=True,mutable_input_snapshot=True,tampering_rejected=True,exact_test_known_values=True,duplicate_json_keys_rejected=True,control_ties_deterministic=True,model_calls=0))
print('Receipt authentication, tampering, strict JSON, exact statistics and control ordering PASS.')
