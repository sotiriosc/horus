"""Score raw FINAL strings only. Never import/read transport or private reasoning."""
import json,re
from collections import Counter
from pathlib import Path
import jsonschema
from world_generator import CLASSES,D,H,U,T,X
P=Path(__file__).resolve().parent

def strict_json(raw):
 if type(raw) is not str:raise ValueError('Only a raw final-channel string is accepted')
 def unique(pairs):
  out={}
  for k,v in pairs:
   if k in out:raise ValueError('Duplicate JSON member')
   out[k]=v
  return out
 def reject_constant(value):raise ValueError('Non-JSON numeric constant')
 return json.loads(raw,object_pairs_hook=unique,parse_constant=reject_constant)

def all_strings(v):
 if isinstance(v,str):yield v
 elif isinstance(v,list):
  for x in v:yield from all_strings(x)
 elif isinstance(v,dict):
  for k,x in v.items():yield k;yield from all_strings(x)

def score_rendering(raw,gold,case,schema):
 result=dict(schema_valid=False,ids_valid=False,classification=None,classification_correct=False,localized=False,evidence_grounded=False,invented_ids=[])
 try:v=strict_json(raw)
 except (ValueError,TypeError,json.JSONDecodeError):return result
 if isinstance(v,dict) and v.get('classification') in CLASSES:result['classification']=v['classification']
 evidence={r['id'] for r in case['records']};components={r['id'] for r in case['components']}
 all_ids={s for s in all_strings(case) if re.fullmatch(r'z[0-9a-f]{16}',s)}
 result['invented_ids']=sorted({i for t in all_strings(v) for i in re.findall(r'\bz[0-9a-f]{16}\b',t)}-all_ids)
 try:jsonschema.validate(v,schema)
 except jsonschema.ValidationError:return result
 result['schema_valid']=True
 evidence={r['id'] for r in case['records']};components={r['id'] for r in case['components']}
 all_ids={s for s in all_strings(case) if re.fullmatch(r'z[0-9a-f]{16}',s)}
 # Class-specific slots must refer to the correct ID category, not just an existing label.
 bad=set(v['evidence_ids'])-evidence;bad|=set(v['affected_component_ids'])-components
 mechanism=v['causal_mechanism']
 if mechanism:
  bad|={mechanism[k] for k in ('contract_evidence_id','cause_evidence_id','effect_evidence_id','decisive_evidence_id')}-evidence
 for text in all_strings(v):bad|=set(re.findall(r'\bz[0-9a-f]{16}\b',text))-all_ids
 result['invented_ids']=sorted(bad);result['ids_valid']=not bad
 result['classification_correct']=not bad and v['classification']==gold['classification']
 cited=set(v['evidence_ids'])
 result['evidence_grounded']=result['classification_correct'] and set(gold['required_evidence'])<=cited
 if gold['classification']==D:
  witnesses=[gold['mechanism_witness'],*gold.get('mechanism_alternatives',[])]
  result['localized']=result['classification_correct'] and v['affected_component_ids']==gold['affected_components'] and mechanism is not None and any(all(type(mechanism[k]) is type(want) and mechanism[k]==want for k,want in witness.items()) and {v for k,v in witness.items() if k.endswith('_evidence_id')}<=cited for witness in witnesses)
 return result

def score_benchmark(raw_finals,grading,rendered,schema,protocol,violations=()):
 """No auditors/critic corrections accepted. Exactly one raw string per scheduled rendering."""
 if violations or set(raw_finals)!=set(grading) or any(type(v) is not str for v in raw_finals.values()):
  return dict(classification='INVALID_STUDY',violations=list(violations) or ['Output inventory/type differs from frozen schedule'])
 per={rid:score_rendering(raw_finals[rid],row['gold'],rendered[rid],schema) for rid,row in grading.items()}
 groups={}
 for rid,row in grading.items():groups.setdefault(row['case_id'],[]).append(rid)
 if len(groups)!=20 or any(len(v)!=4 for v in groups.values()):return dict(classification='INVALID_STUDY',violations=['Frozen grading inventory corrupt'])
 semantic={}
 for cid,ids in groups.items():
  rows=[per[rid] for rid in ids];klass=grading[ids[0]]['gold']['classification']
  semantic[cid]=dict(gold_classification=klass,classification_correct=sum(r['classification_correct'] for r in rows)>=3,localized=sum(r['localized'] for r in rows)>=3,evidence_grounded=sum(r['evidence_grounded'] for r in rows)>=3,consistent=all(r['schema_valid'] and r['ids_valid'] for r in rows) and len({r['classification'] for r in rows})==1,avoids_current=all(r['classification']!=D for r in rows),render_ids=sorted(ids))
 def count(klass,field):return sum(v[field] for v in semantic.values() if v['gold_classification']==klass)
 healthy_fp=sum(r['classification']==D for rid,r in per.items() if grading[rid]['gold']['classification']==H)
 historical_fp=sum(r['classification']==D for rid,r in per.items() if grading[rid]['gold']['classification']==T)
 pairs=[]
 for pair in protocol['matched_pairs']:
  # Both endpoints must be correct in >=3/4, and at least 3 of four matched A/B x order cells must both be correct.
  left,right=pair['left'],pair['right'];paired_cells=[]
  for label in ('A','B'):
   for order in (1,2):
    l=next(k for k,r in grading.items() if r['case_id']==left and r['label_map']==label and r['order']==order)
    r=next(k for k,row in grading.items() if row['case_id']==right and row['label_map']==label and row['order']==order)
    paired_cells.append(per[l]['classification_correct'] and per[r]['classification_correct'])
  pairs.append(dict(pair_id=pair['pair_id'],correct_direction=semantic[left]['classification_correct'] and semantic[right]['classification_correct'] and sum(paired_cells)>=3,correct_cells=sum(paired_cells)))
 measured=dict(semantic_classification_min=sum(v['classification_correct'] for v in semantic.values()),current_defect_classification_min=count(D,'classification_correct'),current_defect_localization_min=count(D,'localized'),healthy_semantic_avoid_current=count(H,'avoids_current'),healthy_rendering_current_false_positives_max=healthy_fp,historical_semantic_avoid_current=count(T,'avoids_current'),historical_rendering_current_false_positives_max=historical_fp,insufficient_classification_min=count(U,'classification_correct'),invalid_classification_min=count(X,'classification_correct'),counterfactual_pairs_min=sum(p['correct_direction'] for p in pairs),representation_consistent_min=sum(v['consistent'] for v in semantic.values()),evidence_grounded_semantics_min=sum(v['evidence_grounded'] for v in semantic.values()),invented_ids_max=sum(bool(r['invented_ids']) for r in per.values()))
 gates={k:(measured[k]<=v if k.endswith('_max') else measured[k]>=v) for k,v in protocol['mandatory_gates'].items()}
 factors={}
 for label in ('A','B'):
  ids=[rid for rid,row in grading.items() if row['label_map']==label];factors['labels_'+label]=dict(correct=sum(per[i]['classification_correct'] for i in ids),total=len(ids))
 for order in (1,2):
  ids=[rid for rid,row in grading.items() if row['order']==order];factors['order_'+str(order)]=dict(correct=sum(per[i]['classification_correct'] for i in ids),total=len(ids))
 disagreements=dict(label_map=0,presentation_order=0)
 for cid in groups:
  lookup={(r['label_map'],r['order']):per[rid] for rid,r in grading.items() if r['case_id']==cid}
  for order in (1,2):disagreements['label_map']+=lookup['A',order]['classification']!=lookup['B',order]['classification']
  for label in ('A','B'):disagreements['presentation_order']+=lookup[label,1]['classification']!=lookup[label,2]['classification']
 return dict(classification='BLIND_DIAGNOSTIC_CAPABILITY_SUPPORTED_V0' if all(gates.values()) else 'BLIND_DIAGNOSTIC_CAPABILITY_NOT_ESTABLISHED_V0',measured=measured,gates=gates,semantic_cases=semantic,renderings=per,matched_pairs=pairs,factor_accuracy=factors,factor_classification_disagreements=disagreements,scientific_unit='semantic case; 20 designed units, not 80 independent samples',prose_scoring='Unscored descriptive output. Structured localization uses frozen contract/cause/effect witnesses; no semantic auditor repairs answers.')
