"""Frozen source grading with immutable Qwen/Ministral score reuse and three-way matches."""
import argparse,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1];SOURCE=P.parent/'qwen-epistemic-primitive-factorization-v0';MINISTRAL=P.parent/'epistemic-primitive-cross-model-comparator-v0'
sys.path.insert(0,str(SOURCE));spec=importlib.util.spec_from_file_location('preserved_epistemic_scorer',SOURCE/'score.py');source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source);sys.path.pop(0)
FAMILIES=source.FAMILIES;CLASSES=source.CLASSES;grade=source.grade;summarize=source.summarize;raw=source.raw
QWEN_SHA='5dd018b316230b8126c0e6eefe86363d6983f3dc179b934f4b4735119edfd99b';MINISTRAL_SHA='ac6fb003b9bc46d08d8ab558fc98f231392f4542b0697818626ba32d329c20e1'
def load_raw(folder):
 freeze=json.loads((folder/'raw-freeze.json').read_bytes());assert freeze['purpose']=='SCIENTIFIC_GPT_OSS_COMPARATOR_V0','Mock evidence cannot be scored as scientific output'
 for name,want in freeze['sha256'].items():assert hashlib.sha256((folder/'raw'/name).read_bytes()).hexdigest()==want,name
 return json.loads((folder/'raw/execution.json').read_bytes())
def classify(g):
 failed=[f for f in FAMILIES if not g['primitives'][f]['gate']];rg=g['reduction']['gate']
 if failed:category,label='C','SECOND_COMPARATOR_PRIMITIVE_LIMITATIONS'
 elif rg:category,label='A','QWEN_REDUCTION_LIMITATION_SUPPORTED_AGAINST_CAPABLE_COMPARATOR'
 else:category,label='B','SHARED_REDUCTION_LIMITATION_SUPPORTED'
 return dict(category=category,pattern=label,failed_primitives=failed,reduction_pass_despite_primitive_failure=bool(failed and rg),scope='Frozen model/interface comparison, no deployment or intervention claim')
def compare(q,m,g):
 models={'qwen':q,'ministral':m,'gpt_oss':g};lookups={name:{r['render_id']:r for r in model['rows']} for name,model in models.items()};tasks=[]
 for r in g['rows']:
  aligned={name:lookup[r['render_id']] for name,lookup in lookups.items()}
  for row in aligned.values():assert all(row[k]==r[k] for k in ('world_id','pair_id','family','arm','gold'))
  tasks.append(dict(render_id=r['render_id'],world_id=r['world_id'],pair_id=r['pair_id'],family=r['family'],arm=r['arm'],gold=r['gold'],models={name:{k:row[k] for k in ('selected','correct','schema_valid','error_category')} for name,row in aligned.items()}))
 elook={name:{r['world_id']:r for r in model['endpoint_comparisons']} for name,model in models.items()};states=[];groups={key:[] for key in ('all_three_P_correct','Qwen_P_correct_both_comparators_P_wrong','Qwen_and_gpt_oss_P_correct','all_three_P_correct_reduction_answers_differ','Qwen_and_gpt_oss_P_correct_reduction_answers_differ','Qwen_R_wrong_gpt_oss_R_correct','Qwen_R_correct_gpt_oss_R_wrong','all_three_R_wrong','all_three_R_correct')}
 for e in g['endpoint_comparisons']:
  sid=e['world_id'];a={name:lookup[sid] for name,lookup in elook.items()};qr,mr,gr=a['qwen'],a['ministral'],a['gpt_oss'];states.append(dict(world_id=sid,family=e['family'],models=a));allp=all(x['P_correct'] for x in a.values());qgp=qr['P_correct'] and gr['P_correct'];diff=not(qr['R_selected']==mr['R_selected']==gr['R_selected'])
  conditions=[allp,qr['P_correct'] and not mr['P_correct'] and not gr['P_correct'],qgp,allp and diff,qgp and qr['R_selected']!=gr['R_selected'],not qr['R_correct'] and gr['R_correct'],qr['R_correct'] and not gr['R_correct'],all(not x['R_correct'] for x in a.values()),all(x['R_correct'] for x in a.values())]
  for key,condition in zip(groups,conditions):
   if condition:groups[key].append(sid)
 plook={name:{r['pair_id']:r for r in model['pair_comparisons']} for name,model in models.items()};pairs=[dict(pair_id=p['pair_id'],family=p['family'],models={name:lookup[p['pair_id']] for name,lookup in plook.items()}) for p in g['pair_comparisons']]
 primitives={f:{name:model['primitives'][f] for name,model in models.items()} for f in FAMILIES};reduction={name:model['reduction'] for name,model in models.items()};families={f:{name:model['family_comparisons'][f] for name,model in models.items()} for f in FAMILIES}
 return dict(reference_score_sha256=dict(qwen=QWEN_SHA,ministral=MINISTRAL_SHA),tasks=tasks,states=states,pairs=pairs,primitives=primitives,reduction=reduction,families=families,state_categories={key:dict(count=len(xs),members=xs) for key,xs in groups.items()},within_model_joint={name:model['endpoint_joint_descriptive_counts'] for name,model in models.items()},evidence_sufficiency=dict(summary=families['EVIDENCE_SUFFICIENCY'],states=[r for r in states if r['family']=='EVIDENCE_SUFFICIENCY'],pairs=[r for r in pairs if r['family']=='EVIDENCE_SUFFICIENCY']),pairwise_disagreements={left+'_vs_'+right:dict(primitive_answer_states=[r['world_id'] for r in tasks if r['arm']=='P' and r['models'][left]['selected']!=r['models'][right]['selected']],reduction_answer_states=[r['world_id'] for r in tasks if r['arm']=='R' and r['models'][left]['selected']!=r['models'][right]['selected']],primitive_pair_passes=[r['pair_id'] for r in pairs if r['models'][left]['P_pair_pass']!=r['models'][right]['P_pair_pass']],reduction_pair_passes=[r['pair_id'] for r in pairs if r['models'][left]['R_exact_pair_pass']!=r['models'][right]['R_exact_pair_pass']]) for left,right in [('qwen','gpt_oss'),('ministral','gpt_oss'),('qwen','ministral')]})
def score(folder=P):
 execution=load_raw(folder)
 if execution['stop'] or execution['completed_calls']!=112:return dict(status='INVALID_STUDY',execution=execution,findings='NOT_ESTABLISHED_DUE_TO_INVALID_STUDY')
 gold={g['world_id']:g for g in json.loads((SOURCE/'materialized/gold.json').read_bytes())};pairs=json.loads((SOURCE/'materialized/pairs.json').read_bytes());entries=json.loads((folder/'materialized/render-manifest.json').read_bytes())['entries'];rows=[]
 for e in entries:
  want=gold[e['world_id']][e['arm']];task=e['family'] if e['arm']=='P' else source.REDUCTION;r=grade((folder/'raw/finals'/(e['render_id']+'.txt')).read_text(),task,want);r.update(world_id=e['world_id'],pair_id=e['pair_id'],side=e['side'],family=e['family'],arm=e['arm'],render_id=e['render_id'],gold=want);rows.append(r)
 g=summarize(rows,pairs);g['status']='GPT_OSS_EPISTEMIC_COMPARATOR_COMPLETE_V0';g['within_model_interpretation']=g.pop('registered_interpretation');refs=[]
 for directory,want in [(SOURCE,QWEN_SHA),(MINISTRAL,MINISTRAL_SHA)]:
  b=(directory/'scores.json').read_bytes();assert hashlib.sha256(b).hexdigest()==want;refs.append(json.loads(b))
 g.update(matched_comparison=compare(*refs,g),registered_interpretation=classify(g),attempted=execution['attempted_calls'],completed=execution['completed_calls']);return g
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--raw-commit',required=True);ap.add_argument('--out',required=True,type=Path);a=ap.parse_args();rel=str(P.relative_to(ROOT))
 def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
 assert git('merge-base','--is-ancestor',a.raw_commit,'HEAD')==b'';assert git('show',a.raw_commit+':'+rel+'/raw-freeze.json')==(P/'raw-freeze.json').read_bytes();assert not git('ls-tree','--name-only',a.raw_commit,'--',rel+'/scores.json').strip()
 for name in json.loads((P/'raw-freeze.json').read_bytes())['sha256']:assert git('show',a.raw_commit+':'+rel+'/raw/'+name)==(P/'raw'/name).read_bytes()
 result=score();result['raw_commit_before_scoring']=a.raw_commit
 with a.out.open('xb') as f:f.write(raw(result))
 print(json.dumps({k:result[k] for k in ('status','attempted','completed','registered_interpretation') if k in result}))
