"""Direct serialization of prospectively authored states; no compiler or prior responses."""
import argparse,copy,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;SEED=413708629
FAMILIES=['IDENTITY_EQUALITY','CURRENTNESS','KNOWN_VS_UNKNOWN','CONTRADICTION','ALTERNATIVE_COMPLETION_EXISTENCE','OBSERVATION_REQUIREMENT_COMPARISON','EVIDENCE_SUFFICIENCY']
CLASSES=['SUPPORTED_CURRENT_DEFECT','NO_SUPPORTED_DIAGNOSIS','INSUFFICIENT_EVIDENCE','HISTORICAL_DEFECT_NOT_CURRENT','INVALID_OR_CONTRADICTORY_EVIDENCE']
DEFS=['Available current evidence supports a specific active structural or mechanical defect and distinguishes it from materially plausible benign alternatives.','The internally valid evidence is sufficient within the declared contract/input scope and supports no current defect. Unusual or undesirable behavior alone is insufficient.','The evidence is internally valid but a current defect and a materially plausible benign explanation remain observationally indistinguishable.','A defect is demonstrated for an older version, while supplied current mechanisms and observations show it is no longer active within the stated scope.','The supplied evidence package contains incompatible immutable, version, capture or provenance facts and cannot support a valid operational diagnosis.']
REDUCTION='FIVE_CLASS_REDUCTION';ARMS=['P','R']
def raw(x):return (json.dumps(x,indent=2,ensure_ascii=True)+'\n').encode()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True)
def digest(*x):return hashlib.sha256('|'.join(map(str,(SEED,)+x)).encode()).hexdigest()
def pair_id(i):return 'p'+digest('pair',i)[:12]
def state_id(i,side):return 's'+digest('state',i,side)[:12]
SYSTEM_P='Use only the supplied aligned factual state to answer the specified narrow question. Return exactly one JSON object satisfying the response schema. No tools or explanatory prose.'
SYSTEM_R='Use only the supplied bounded evidence and class definitions. Do not invent missing facts or silently reconcile incompatible declarations of one immutable event. Return exactly one JSON object satisfying the response schema. No tools, interventions or solution proposals.'
CLASS_TEXT='Class definitions:\n'+'\n'.join(c+': '+d for c,d in zip(CLASSES,DEFS))+'\n\nReturn only the classification object. No rationale, citations or other prose.'
PATTERNS=[[('P','A'),('R','B'),('P','B'),('R','A')],[('R','A'),('P','B'),('R','B'),('P','A')],[('R','B'),('P','A'),('R','A'),('P','B')],[('P','B'),('R','A'),('P','A'),('R','B')]]
def request_for(state,arm,family,question,schemas):
 # The only factual input is the frozen state. No gold/proof/vector parameter exists.
 schema=schemas[family if arm=='P' else REDUCTION];instruction=question if arm=='P' else CLASS_TEXT
 messages=[{'role':'system','content':SYSTEM_P if arm=='P' else SYSTEM_R},{'role':'user','content':instruction+'\n\nAligned factual state:\n'+raw(state).decode()}]
 neutral={'messages':messages,'response_schema':schema}
 request={'messages':messages,'response_format':{'type':'json_object','schema':schema},'temperature':.2,'top_p':.9,'top_k':40,'min_p':.05,'seed':SEED,'max_tokens':2048,'cache_prompt':False,'stream':False,'chat_template_kwargs':{'enable_thinking':True}}
 return neutral,request

def generate():
 spec=json.loads((P/'case-spec.json').read_bytes());schemas=json.loads((P/'schemas.json').read_bytes());files={};entries=[];gold=[];pairs=[]
 for pair in spec['pairs']:
  i=pair['index'];pid=pair_id(i);family=pair['primitive'];endpoints={}
  for side in 'AB':
   sid=state_id(i,side);state=copy.deepcopy(pair['states'][side]);endpoints[side]=sid;statebytes=raw(state);files['states/'+sid+'.json']=statebytes
   g=pair['offline_gold'][side];gold.append({'world_id':sid,'pair_id':pid,'side':side,'family':family,'P':g['primitives'][family],'R':{'classification':g['classification']},'primitive_vector':g['primitives'],'author_proof':g['author_proof']})
   for arm in ARMS:
    rid=digest('render',sid,arm)[:20];neutral,request=request_for(state,arm,family,spec['questions'][family],schemas)
    files['fixtures/'+rid+'.json']=statebytes;files['neutral/'+rid+'.json']=raw(neutral);files['requests/'+rid+'.json']=raw(request)
    entries.append({'world_id':sid,'pair_id':pid,'family':family,'side':side,'arm':arm,'render_id':rid,'request_path':'requests/'+rid+'.json','request_sha256':hashlib.sha256(raw(request)).hexdigest(),'state_sha256':hashlib.sha256(statebytes).hexdigest()})
  pairs.append({'pair_id':pid,'index':i,'within_family':pair['within_family'],'family':family,'endpoints':endpoints,'identity_flip_field':pair['designated_identity_field'],'semantic_delta':pair['semantic_delta'],'coupling':pair['coupling_audit']})
 schedule=[];last=None
 for epoch in range(4):
  order=sorted(pairs,key=lambda p:digest('epoch',epoch,p['pair_id']))
  if last==order[0]['pair_id']:order=order[1:]+order[:1]
  for pair in order:
   arm,side=PATTERNS[pair['within_family']][epoch];entry=next(e for e in entries if e['pair_id']==pair['pair_id'] and e['arm']==arm and e['side']==side);entry.update(epoch=epoch+1,within_pair_position=epoch+1,call_order=len(schedule)+1);schedule.append(entry['render_id']);last=pair['pair_id']
 files['gold.json']=raw(gold);files['pairs.json']=raw(pairs);files['render-manifest.json']=raw({'seed':SEED,'schedule':schedule,'entries':entries,'patterns':PATTERNS});return files
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True,type=Path);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
 for name,data in generate().items():f=args.out/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
 print('Materialized 56 aligned states, 28 pairs and 112 independent requests; no model calls.')
