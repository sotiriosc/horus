"""Comparator-only grading using unchanged source functions and published Qwen scores."""
import argparse,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1];SOURCE=ROOT/'research/qwen-epistemic-primitive-factorization-v0'
sys.path.insert(0,str(SOURCE))
spec=importlib.util.spec_from_file_location('preserved_epistemic_scorer',SOURCE/'score.py');source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
sys.path.pop(0)
FAMILIES=source.FAMILIES;CLASSES=source.CLASSES;grade=source.grade;summarize=source.summarize;raw=source.raw
QWEN_SHA='5dd018b316230b8126c0e6eefe86363d6983f3dc179b934f4b4735119edfd99b'
def load_raw(folder):
 freeze=json.loads((folder/'raw-freeze.json').read_bytes());assert freeze['purpose']=='SCIENTIFIC_CROSS_MODEL_COMPARATOR_V0','Mock evidence cannot be scored as scientific output'
 for name,want in freeze['sha256'].items():assert hashlib.sha256((folder/'raw'/name).read_bytes()).hexdigest()==want,name
 return json.loads((folder/'raw/execution.json').read_bytes())
def classify(c,shared_errors):
 failed=[f for f in FAMILIES if not c['primitives'][f]['gate']];rg=c['reduction']['gate']
 if not failed and rg:category,label='A','QWEN_SPECIFIC_REDUCTION_LIMITATION_SUPPORTED_UNDER_FROZEN_COMPARATOR'
 elif failed and rg:category,label='D','MIXED_PRIMITIVE_REDUCTION_PATTERN'
 elif failed:category,label='C','COMPARATOR_PRIMITIVE_LIMITATIONS'
 elif shared_errors>=8:category,label='B','SHARED_REDUCTION_DIFFICULTY_SUPPORTED'
 else:category,label='E','REDUCTION_DIFFICULTY_WITH_DIFFERENT_ERROR_PATTERN'
 return dict(category=category,pattern=label,failed_primitives=failed,shared_reduction_errors=shared_errors,similarity_rule='At least 8 of the 15 published Qwen reduction-error states also incorrect for comparator; descriptive majority, not significance')
def compare(q,c):
 qr={r['render_id']:r for r in q['rows']};tasks=[]
 for r in c['rows']:
  old=qr[r['render_id']];assert all(old[k]==r[k] for k in ('world_id','pair_id','family','arm','gold'))
  tasks.append(dict(render_id=r['render_id'],world_id=r['world_id'],pair_id=r['pair_id'],family=r['family'],arm=r['arm'],gold=r['gold'],qwen_selected=old['selected'],comparator_selected=r['selected'],qwen_correct=old['correct'],comparator_correct=r['correct'],qwen_schema_valid=old['schema_valid'],comparator_schema_valid=r['schema_valid'],answers_differ=old['selected']!=r['selected'],correctness_differs=old['correct']!=r['correct']))
 qe={e['world_id']:e for e in q['endpoint_comparisons']};states=[]
 groups={k:[] for k in ('both_P_correct_both_R_correct','both_P_correct_both_R_wrong','both_P_correct_only_Qwen_R_wrong','both_P_correct_only_comparator_R_wrong','primitive_answers_differ','reduction_answers_differ')}
 for e in c['endpoint_comparisons']:
  old=qe[e['world_id']];states.append(dict(world_id=e['world_id'],family=e['family'],qwen=old,comparator=e))
  if old['P_correct'] and e['P_correct']:
   k='both_P_correct_'+('both_R_correct' if old['R_correct'] and e['R_correct'] else 'both_R_wrong' if not old['R_correct'] and not e['R_correct'] else 'only_Qwen_R_wrong' if not old['R_correct'] else 'only_comparator_R_wrong');groups[k].append(e['world_id'])
  if old['P_selected']!=e['P_selected']:groups['primitive_answers_differ'].append(e['world_id'])
  if old['R_selected']!=e['R_selected']:groups['reduction_answers_differ'].append(e['world_id'])
 qp={x['pair_id']:x for x in q['pair_comparisons']};pairs=[]
 for x in c['pair_comparisons']:
  old=qp[x['pair_id']];pairs.append(dict(pair_id=x['pair_id'],family=x['family'],qwen=old,comparator=x,P_pass_differs=old['P_pair_pass']!=x['P_pair_pass'],P_transition_differs=old['P_selected_transition']!=x['P_selected_transition'],R_pass_differs=old['R_exact_pair_pass']!=x['R_exact_pair_pass'],R_transition_differs=old['R_selected_transition']!=x['R_selected_transition']))
 primitive={}
 for f in FAMILIES:
  primitive[f]=dict(qwen=q['primitives'][f],comparator=c['primitives'][f],endpoint_answer_disagreements=[r['world_id'] for r in tasks if r['family']==f and r['arm']=='P' and r['answers_differ']],endpoint_correctness_disagreements=[r['world_id'] for r in tasks if r['family']==f and r['arm']=='P' and r['correctness_differs']],pair_pass_disagreements=[r['pair_id'] for r in pairs if r['family']==f and r['P_pass_differs']],pair_transition_disagreements=[r['pair_id'] for r in pairs if r['family']==f and r['P_transition_differs']])
 shared=[r['world_id'] for r in tasks if r['arm']=='R' and not r['qwen_correct'] and not r['comparator_correct']]
 return dict(source_score_sha256=QWEN_SHA,tasks=tasks,states=states,pairs=pairs,primitives=primitive,reduction=dict(qwen=q['reduction'],comparator=c['reduction'],class_correct_differences={cl:c['reduction']['per_class'][cl]['correct']-q['reduction']['per_class'][cl]['correct'] for cl in CLASSES},shared_error_states=shared),state_categories={k:dict(count=len(v),members=v) for k,v in groups.items()},qwen_joint=q['endpoint_joint_descriptive_counts'],comparator_joint=c['endpoint_joint_descriptive_counts'],evidence_sufficiency=dict(qwen=q['family_comparisons']['EVIDENCE_SUFFICIENCY'],comparator=c['family_comparisons']['EVIDENCE_SUFFICIENCY'],states=[x for x in states if x['family']=='EVIDENCE_SUFFICIENCY'],pairs=[x for x in pairs if x['family']=='EVIDENCE_SUFFICIENCY']),registered_interpretation=classify(c,len(shared)))
def score(folder=P):
 execution=load_raw(folder)
 if execution['stop'] or execution['completed_calls']!=112:return dict(status='INVALID_STUDY',execution=execution,findings='NOT_ESTABLISHED_DUE_TO_INVALID_STUDY')
 gold={g['world_id']:g for g in json.loads((SOURCE/'materialized/gold.json').read_bytes())};pairs=json.loads((SOURCE/'materialized/pairs.json').read_bytes());entries=json.loads((folder/'materialized/render-manifest.json').read_bytes())['entries'];rows=[]
 for e in entries:
  want=gold[e['world_id']][e['arm']];task=e['family'] if e['arm']=='P' else source.REDUCTION;r=grade((folder/'raw/finals'/(e['render_id']+'.txt')).read_text(),task,want);r.update(world_id=e['world_id'],pair_id=e['pair_id'],side=e['side'],family=e['family'],arm=e['arm'],render_id=e['render_id'],gold=want);rows.append(r)
 c=summarize(rows,pairs);c['status']='MINISTRAL_CROSS_MODEL_COMPARATOR_COMPLETE_V0';c['within_model_interpretation']=c.pop('registered_interpretation');qb=(SOURCE/'scores.json').read_bytes();assert hashlib.sha256(qb).hexdigest()==QWEN_SHA;q=json.loads(qb);matched=compare(q,c);c.update(matched_comparison=matched,registered_interpretation=matched['registered_interpretation'],attempted=execution['attempted_calls'],completed=execution['completed_calls']);return c
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--raw-commit',required=True);ap.add_argument('--out',required=True,type=Path);a=ap.parse_args();rel=str(P.relative_to(ROOT))
 def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
 assert git('merge-base','--is-ancestor',a.raw_commit,'HEAD')==b'';assert git('show',a.raw_commit+':'+rel+'/raw-freeze.json')==(P/'raw-freeze.json').read_bytes();assert not git('ls-tree','--name-only',a.raw_commit,'--',rel+'/scores.json').strip()
 for name in json.loads((P/'raw-freeze.json').read_bytes())['sha256']:assert git('show',a.raw_commit+':'+rel+'/raw/'+name)==(P/'raw'/name).read_bytes()
 result=score();result['raw_commit_before_scoring']=a.raw_commit
 with a.out.open('xb') as f:f.write(raw(result))
 print(json.dumps({k:result[k] for k in ('status','attempted','completed','registered_interpretation') if k in result}))
