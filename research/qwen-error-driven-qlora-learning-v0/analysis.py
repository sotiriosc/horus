"""Frozen parsing, all-error admission, replay, paired statistics and hard gates."""
import copy,itertools,json,math,random
from collections import Counter,defaultdict
from data import *
REGRESSION_METRIC={'clear_YES':'joint','clear_NO':'joint','contradiction_independent':'joint','current_determinate':'current_violation','all_prior_determinate':'prior_violation','schema':'schema'}

def parse(text):
 def strict(pairs):
  d={}
  for k,v in pairs:
   if k in d:raise ValueError('duplicate key')
   d[k]=v
  return d
 try:
  x=json.loads(text,object_pairs_hook=strict)
  if not isinstance(x,dict) or set(x)!=set(FIELDS) or any(x[k] not in VALUES for k in FIELDS):return None
  return x
 except (ValueError,TypeError):return None

def score(cs,outputs):
 assert [c['id'] for c in cs]==[o['id'] for o in outputs]
 scored=[]
 for c,o in zip(cs,outputs):
  pred=parse(o['text']);scored.append(dict(id=c['id'],prediction=pred,gold=c['gold'],schema=pred is not None,joint=pred==c['gold'],**{k:pred is not None and pred[k]==c['gold'][k] for k in FIELDS}))
 return scored

def stratified_replay(correct,count,seed):
 if count==0:return []
 if not correct:raise RuntimeError('No correct examples available for mandatory correct replay; cannot proceed with prescribed learning design')
 groups=defaultdict(list)
 for c in correct:groups['/'.join(c['gold'][k] for k in FIELDS)].append(c)
 rng=random.Random(seed)
 for k in sorted(groups):rng.shuffle(groups[k])
 indices=Counter();out=[];keys=sorted(groups)
 # Equal round-robin across nonempty gold strata, cycling with replacement where necessary.
 for i in range(count):
  k=keys[i%len(keys)];out.append(groups[k][indices[k]%len(groups[k])]);indices[k]+=1
 return out

def construct_training(harvest,neighbors,scored,cycle,previous=None):
 byid={c['id']:c for c in harvest};errors=[byid[s['id']] for s in scored if not s['joint']];correct=[byid[s['id']] for s in scored if s['joint']]
 if not errors:raise RuntimeError('No verified harvest errors: error-driven update is not defined')
 errids={c['id'] for c in errors};selected_neighbors=[];seen={c['semantic_signature'] for c in errors}
 for n in neighbors:
  if n['parent'] in errids and n['semantic_signature'] not in seen:selected_neighbors.append(n);seen.add(n['semantic_signature'])
 replay=stratified_replay(correct,len(errors),SEED+cycle*100)
 entries=[dict(source=source,case_id=c['id'],target=canonical(c['gold'])) for source,cs in [('error',errors),('counterfactual',selected_neighbors),('correct_replay',replay)] for c in cs]
 if cycle==2:
  assert previous
  # Exactly 512 retained D1 exposures, stratified over correct targets, with replacement if needed.
  groups=defaultdict(list)
  for e in previous:groups[e['target']].append(e)
  rng=random.Random(SEED+201)
  for k in sorted(groups):rng.shuffle(groups[k])
  keys=sorted(groups);idx=Counter()
  for i in range(512):
   k=keys[i%len(keys)];e=copy.deepcopy(groups[k][idx[k]%len(groups[k])]);idx[k]+=1;e['source']='cycle1_retained_replay';entries.append(e)
 return entries,dict(harvest=len(harvest),errors=len(errors),correct=len(correct),composition=dict(Counter(e['source'] for e in entries)),total_exposures_per_epoch=len(entries),unique_case_ids=len({e['case_id'] for e in entries}),replay_sampling='equal round-robin nonempty joint-gold strata with replacement',all_errors_admitted=errids.issubset({e['case_id'] for e in entries if e['source']=='error'}))

def paired(a,b,metric='joint'):
 assert len(a)==len(b) and len(a)>0 and [x['id'] for x in a]==[x['id'] for x in b]
 n=len(a);table=Counter((x[metric],y[metric]) for x,y in zip(a,b));loss=table[True,False];gain=table[False,True];disc=loss+gain
 p=min(1.,2*sum(math.comb(disc,i) for i in range(min(loss,gain)+1))/2**disc) if disc else 1.
 return dict(n=n,incumbent_correct=sum(x[metric] for x in a),candidate_correct=sum(x[metric] for x in b),incumbent_accuracy=sum(x[metric] for x in a)/n,candidate_accuracy=sum(x[metric] for x in b)/n,gain_pp=100*(sum(x[metric] for x in b)-sum(x[metric] for x in a))/n,both_correct=table[True,True],incumbent_only=loss,candidate_only=gain,both_wrong=table[False,False],mcnemar_exact_two_sided_p=p)

def compare(cases,a,b):
 result={k:paired(a,b,k) for k in ['joint',*FIELDS,'schema']}
 targets={c['id'] for c in cases if 'target_UNKNOWN_or_aggregation' in c['families']};result['targeted']=paired([x for x in a if x['id'] in targets],[x for x in b if x['id'] in targets])
 distribution={k:dict(Counter(x['prediction'][k] if x['prediction'] else 'INVALID' for x in b)) for k in FIELDS};result['candidate_distribution']=distribution
 result['noncollapsed']=all(distribution[k].get(v,0)/len(b)>=.05 for k in FIELDS for v in VALUES)
 return result

def regress(cases,a,b):
 result={}
 for family,metric in REGRESSION_METRIC.items():
  ids={c['id'] for c in cases if family in c['families']};assert ids
  result[family]=dict(metric=metric,**paired([x for x in a if x['id'] in ids],[x for x in b if x['id'] in ids],metric))
 return result

def cycle1_gate(comp,reg,training,leakage):
 checks=dict(joint_gain_at_least_8pp=comp['joint']['gain_pp']>=8,paired_p_less_than_001=comp['joint']['mcnemar_exact_two_sided_p']<.01,targeted_gain_at_least_10pp=comp['targeted']['gain_pp']>=10,schema_at_least_99percent=comp['schema']['candidate_accuracy']>=.99,no_major_regression=all(x['gain_pp']>=-3 for x in reg.values()),noncollapsed=comp['noncollapsed'],adapter_changed=training['adapter_changed'],base_unchanged=training['base_unchanged'],leakage=leakage['status']=='PASS')
 return dict(checks=checks,classification='ERROR_DRIVEN_PARAMETER_LEARNING_SUPPORTED' if all(checks.values()) else 'ERROR_DRIVEN_PARAMETER_LEARNING_NOT_ESTABLISHED',cycle2_authorized=all(checks.values()))

def cycle2_gate(comp,retention,regressions,training,leakage):
 checks=dict(joint_gain_at_least_4pp=comp['joint']['gain_pp']>=4,paired_p_less_than_005=comp['joint']['mcnemar_exact_two_sided_p']<.05,t1_retention_loss_at_most_2pp=retention['joint']['gain_pp']>=-2,no_major_regression=all(x['gain_pp']>=-3 for reg in regressions.values() for x in reg.values()),schema_at_least_99percent=comp['schema']['candidate_accuracy']>=.99 and retention['schema']['candidate_accuracy']>=.99 and all(reg['schema']['candidate_accuracy']>=.99 for reg in regressions.values()),adapter_changed=training['adapter_changed'],base_unchanged=training['base_unchanged'],leakage=leakage['status']=='PASS')
 return dict(checks=checks,classification='TWO_CYCLE_ERROR_DRIVEN_LEARNING_SUPPORTED' if all(checks.values()) else 'SECOND_LEARNING_CYCLE_NOT_ESTABLISHED')

def audit_datasets(folder,training=None):
 datasets={n:rows(folder/(n+'.jsonl')) for n in ['H1','V1','T1','R1','H2','V2','T2','R2','N1','N2']};legacy=legacy_signatures();sigs={n:{c['semantic_signature'] for c in cs} for n,cs in datasets.items()};overlaps={}
 for n,cs in datasets.items():
  for c in cs:independently_audit(c)
  assert not sigs[n]&legacy
  if not n.startswith('N'):assert len(sigs[n])==len(cs)
 for test in ['T1','T2']:
  for other in datasets:
   if test==other:continue
   overlaps[test+'/'+other]=len(sigs[test]&sigs[other]);assert not overlaps[test+'/'+other]
 lookup={c['id']:c for cs in datasets.values() for c in cs}
 if training:
  for e in training:
   c=lookup[e['case_id']];assert e['target']==canonical(c['gold']);assert c['semantic_signature'] not in sigs['T1']|sigs['T2']
 # Stronger equivalence removes irrelevant package consistency as well.
 def trial_only(c):
  s=c['state'];return canonical([s['current_trial'],sorted(s['non_current_trials'],key=canonical)])
 strict={n:{trial_only(c) for c in cs} for n,cs in datasets.items()}
 strict_overlaps={t+'/'+n:len(strict[t]&strict[n]) for t in ['T1','T2'] for n in datasets if n!=t}
 assert not any(strict_overlaps.values())
 # Abstract operation families necessarily recur; report rather than claim novelty of the Boolean rules.
 def abstract(cs):return {(status(c['state']['current_trial']),tuple(sorted({status(t) for t in c['state']['non_current_trials']}))) for c in cs}
 abstract_overlap={t+'/'+h:len(abstract(datasets[t])&abstract(datasets[h])) for t in ['T1','T2'] for h in ['H1','H2']}
 return dict(status='PASS',normalized_sealed_overlaps=overlaps,package_ignored_sealed_overlaps=strict_overlaps,legacy_states_excluded=len(legacy),abstract_truth_pattern_overlap_counts=abstract_overlap,normalization='Removes IDs, wording, scope decoration and semantically irrelevant prior ordering; retains every resolved primitive and prior multiplicity.',structural_holdout='T1 has 8–9 prior trials; T2 has 13–15; neither count range occurs in either harvest/validation/regression/neighbor pool. Tests use uncertainty at boundaries and reversed determinate order.',limitation='The same truth labels, primitive types and existential operation recur. Repeating a compliant prior is logically redundant, so this tests length/composition generalization within a synthetic task, not novel logic or real-task competence.',training_exposures_audited=len(training or []))
