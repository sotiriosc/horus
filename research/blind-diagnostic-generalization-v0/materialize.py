"""Materialize fixed cases after Method Freeze. No inference client is implemented."""
from pathlib import Path
from copy import deepcopy
import argparse,hashlib,json,subprocess,sys
from world_generator import STUDY,generate,derive,digest,PAIRS,CLASSES
from renderer import render,replace
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
DECLARED_PAIR_PATHS={
 ('d1','h1'):['/records/4/data/used_config','/records/5/data/returned_value','/records/6/data/captured_event_data/returned_value'],
 ('d2','t1'):['/records/1/data/current_version','/records/6/data/deployment_version'],
 ('d3','h2'):['/records/4/data/record_owner'],
 ('d4','h3'):['/records/4/data/publication_fields','/records/5/data/attempt_total_after','/records/6/data/captured_event_data/attempt_total_after'],
 ('d5','u1'):['/records/4/data/entries/1/operation_token','/records/4/data/key_column'],
 ('d6','h4'):['/records/4/data/comparison_result','/records/4/data/implemented_comparator','/records/5/data/command_issued','/records/6/data/captured_event_data/command_issued']}

def encoded(v):return (json.dumps(v,indent=2,ensure_ascii=True)+'\n').encode()
def bundle(seed):
 protocol=json.loads((P/'protocol.json').read_text());schema=json.loads((P/'diagnostic-schema.json').read_text());cfg=json.loads((P/'model-runtime.json').read_text())['configuration']
 cases,pairs=generate(seed);files={};grades={};entries=[]
 for pair in pairs:assert pair['changed_paths']==DECLARED_PAIR_PATHS[pair['left_spec'],pair['right_spec']]
 for case in cases:
  cid=case['case_id'];files['worlds/'+cid+'.json']=encoded(case['world'])
  for label in ('A','B'):
   for order in (1,2):
    rid=derive(seed,'render/'+cid+'/'+label+'/'+str(order)).hex()[:20]
    public,mapping=render(case['world'],seed,cid,label,order)
    # Manual replacement, not format(), because the fixed template contains no dynamic executable expressions.
    user=protocol['user_prompt_template'].replace('{definitions}',json.dumps(protocol['ontology'],separators=(',',':'))).replace('{case}',json.dumps(public,separators=(',',':')))
    req={k:cfg[k] for k in ('temperature','top_p','top_k','min_p','seed','max_tokens','cache_prompt','stream','chat_template_kwargs')}
    req.update(messages=[dict(role='system',content=protocol['system_prompt']),dict(role='user',content=user)],response_format=dict(type='json_object',schema=schema))
    prompt_bytes=sum(len(x['content'].encode()) for x in req['messages'])
    # Conservative byte bound; includes serialized schema and a template reserve. No tokenizer/server call.
    reserved=prompt_bytes+len(json.dumps(schema).encode())+cfg['max_tokens']+512
    assert reserved<=cfg['context'],('context reservation',reserved)
    files['rendered/'+rid+'.json']=encoded(public);files['requests/'+rid+'.json']=encoded(req)
    grades[rid]=dict(case_id=cid,label_map=label,order=order,gold=replace(case['gold'],mapping),mapping=mapping)
    entries.append(dict(render_id=rid,case_id=cid,label_map=label,order=order,request_path='requests/'+rid+'.json',request_sha256=hashlib.sha256(files['requests/'+rid+'.json']).hexdigest(),case_sha256=hashlib.sha256(files['rendered/'+rid+'.json']).hexdigest(),conservative_context_reservation=reserved))
 files['grading.json']=encoded(grades)
 files['case-manifest.json']=encoded(dict(semantic_case_count=len(cases),class_distribution={c:sum(x['gold']['classification']==c for x in cases) for c in CLASSES},cases=[{k:v for k,v in c.items() if k!='world'} for c in cases]))
 files['matched-pairs.json']=encoded(pairs)
 schedule=sorted((e['render_id'] for e in entries),key=lambda rid:derive(seed,'schedule/'+rid))
 files['render-manifest.json']=encoded(dict(rendering_count=len(entries),future_calls=len(entries),schedule=schedule,entries=entries))
 return files

def main():
 a=argparse.ArgumentParser();a.add_argument('--method-commit',required=True);args=a.parse_args()
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip();assert head==args.method_commit
 # Every method byte must already exist in that commit; no materialization-time edits.
 for path in P.iterdir():
  if path.is_file():assert subprocess.check_output(['git','show',head+':'+str(path.relative_to(ROOT))],cwd=ROOT)==path.read_bytes()
 out=P/'materialized';assert not out.exists(),'Never overwrite a case materialization'
 data=bundle(STUDY);assert data==bundle(STUDY),'Regeneration mismatch'
 out.mkdir()
 for name,raw in sorted(data.items()):
  path=out/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
 manifest=dict(method_commit=head,seed_string=STUDY,model_calls=0,sha256={name:hashlib.sha256(raw).hexdigest() for name,raw in sorted(data.items())})
 (P/'freeze-manifest.json').write_bytes(encoded(manifest))
 print(json.dumps(dict(materialized_files=len(data),model_calls=0,method_commit=head)))
if __name__=='__main__':main()
