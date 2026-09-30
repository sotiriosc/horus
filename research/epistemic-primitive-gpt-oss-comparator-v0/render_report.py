"""Three-model descriptive report from already-frozen scores; no inference."""
import json
from pathlib import Path
P=Path(__file__).resolve().parent;NAMES=['qwen','ministral','gpt_oss']
def render(s):
 m=s['matched_comparison'];out=['# Frozen Epistemic Primitive gpt-oss Comparator v0','',s['registered_interpretation']['pattern'],'','This is the final planned comparator. No further comparator, benchmark, model promotion or Horus intervention is authorized by this result. See completion.json for the freeze chain, model-runtime.json for exact identity/configuration, and method.md for the prospective rules.','',f"112 scheduled; {s['attempted']} attempted; {s['completed']} completed. gpt-oss schema-valid: primitives {sum(x['schema_valid'] for x in s['primitives'].values())}/56; reduction {s['reduction']['schema_valid']}/56.",'','Q = published Qwen3-14B; M = published Ministral-3-14B-Reasoning; G = newly measured gpt-oss-20b. Prior scores are reused without inference or rescoring. These are descriptive comparisons of correlated states/pairs, not an overall model ranking.']
 def table(headers,rows):
  out.extend(['','| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |'])
  out.extend('| '+' | '.join(str(x).replace('|','\\|').replace('\n',' ') for x in row)+' |' for row in rows)
 def sel(x):return 'INVALID' if x is None else '`'+json.dumps(x,sort_keys=True,separators=(',',':'))+'`'
 def ids(xs):return ', '.join(xs) if xs else 'none'
 def primitive(x):return f"{x['correct']}/8; {x['pair_passes']}/4; {'PASS' if x['gate'] else 'FAIL'}"
 out.extend(['','## Seven primitive capabilities','', 'Each cell: endpoints; matched pairs; competence gate. Thresholds >=7/8 AND >=3/4.'])
 table(['Primitive','Qwen','Ministral','gpt-oss'],[[f]+[primitive(models[name]) for name in NAMES] for f,models in m['primitives'].items()])
 for f,models in m['primitives'].items():
  out.extend(['',f'## {f}'])
  table(['Model','Correct /8','Pairs /4','Schema /8','Gate'],[[name,x['correct'],x['pair_passes'],x['schema_valid'],x['gate']] for name,x in models.items()])
  if 'fields' in models['gpt_oss']:table(['Model','same_referent /8','equal_value /8','joint /8'],[[name,x['fields']['same_referent'],x['fields']['equal_value'],x['correct']] for name,x in models.items()])
  table(['State','Gold','Q selected','M selected','G selected','Q correct','M correct','G correct'],[[r['world_id'],sel(r['gold'])]+[sel(r['models'][name]['selected']) for name in NAMES]+[r['models'][name]['correct'] for name in NAMES] for r in m['tasks'] if r['family']==f and r['arm']=='P'])
  table(['Pair','Gold A → B','Q A → B','M A → B','G A → B','Q pass','M pass','G pass'],[[r['pair_id'],' → '.join(sel(x) for x in r['models']['gpt_oss']['P_gold_transition'])]+[' → '.join(sel(x) for x in r['models'][name]['P_selected_transition']) for name in NAMES]+[r['models'][name]['P_pair_pass'] for name in NAMES] for r in m['pairs'] if r['family']==f])
  out.extend(['','Confusion counts (rows gold, columns selected):','```json',json.dumps({name:{k:v for k,v in x.items() if 'confusion' in k} for name,x in models.items()},indent=2),'```'])
 out.extend(['','## Five-class reduction'])
 table(['Measure','Qwen','Ministral','gpt-oss'],[[label]+[m['reduction'][name][key] for name in NAMES] for key,label in [('correct','Endpoints /56'),('schema_valid','Schema /56'),('gate','Competence gate'),('exact_pair_passes','Exact pairs /28'),('flip_pair_passes','Diagnostic flips /19'),('stable_pair_passes','Stable retention /9')]])
 classes=list(s['reduction']['per_class']);table(['Class','Qwen','Ministral','gpt-oss','Required floor'],[[cl]+[f"{m['reduction'][name]['per_class'][cl]['correct']}/{m['reduction'][name]['per_class'][cl]['denominator']}" for name in NAMES]+[s['reduction']['per_class'][cl]['minimum']] for cl in classes])
 out.extend(['','Confusion rows are gold, columns selected. D=current defect; N=no supported diagnosis; U=insufficient; H=historical; X=invalid/contradictory; I=invalid output.'])
 for name in NAMES:
  out.extend(['',name]);table(['Gold','D','N','U','H','X','I'],[[cl]+[m['reduction'][name]['confusion'][cl][col] for col in classes+['INVALID_OUTPUT']] for cl in classes])
 out.extend(['','## Family-aligned reduction subsets'])
 for f,models in m['families'].items():
  out.extend(['',f]);table(['Model','Endpoints /8','Exact pairs /4','Diagnostic flips','Stable retention'],[[name,x['R_correct'],x['R_exact_pair_passes'],f"{x['R_flip_pair_passes']}/{x['R_flip_pairs']}" if x['R_flip_pairs'] else 'N/A',f"{x['R_stable_pair_passes']}/{x['R_stable_pairs']}" if x['R_stable_pairs'] else 'N/A'] for name,x in models.items()])
 out.extend(['','## Every aligned state and reduction selection'])
 table(['State','Family','Gold R','Q P/R correct','M P/R correct','G P/R correct','Q R selected','M R selected','G R selected'],[[r['world_id'],r['family'],sel(r['models']['gpt_oss']['R_gold'])]+[f"{r['models'][name]['P_correct']}/{r['models'][name]['R_correct']}" for name in NAMES]+[sel(r['models'][name]['R_selected']) for name in NAMES] for r in m['states']])
 out.extend(['','## Every reduction matched pair','', 'Flip/stable classification is fixed by gold; exact pass requires both endpoints correct with the expected transition.'])
 table(['Pair','Family','Gold changes','Gold A → B','Q A → B','M A → B','G A → B','Q pass','M pass','G pass'],[[r['pair_id'],r['family'],r['models']['gpt_oss']['diagnostic_gold_changes'],' → '.join(sel(v) for v in r['models']['gpt_oss']['R_gold_transition'])]+[' → '.join(sel(v) for v in r['models'][name]['R_selected_transition']) for name in NAMES]+[r['models'][name]['R_exact_pair_pass'] for name in NAMES] for r in m['pairs']])
 out.extend(['','## Exact matched memberships','', 'P is the isolated primitive corresponding to the state’s family. Sets can overlap.'])
 table(['Category','Count','States'],[[key,v['count'],ids(v['members'])] for key,v in m['state_categories'].items()])
 for key,v in m['pairwise_disagreements'].items():
  out.extend(['',key]);table(['Disagreement','Exact members'],[[k,ids(xs)] for k,xs in v.items()])
 table(['Within-model joint outcome','Qwen','Ministral','gpt-oss'],[[key]+[m['within_model_joint'][name][key]['count'] for name in NAMES] for key in m['within_model_joint']['qwen']])
 out.extend(['','## Evidence sufficiency'])
 es=m['evidence_sufficiency'];table(['Measure','Qwen','Ministral','gpt-oss'],[[key]+[es['summary'][name][key] for name in NAMES] for key in ('P_correct','P_pair_passes','R_correct','R_exact_pair_passes')])
 table(['State','Gold P','Gold R','Q P','M P','G P','Q R','M R','G R'],[[r['world_id'],sel(r['models']['gpt_oss']['P_gold']),sel(r['models']['gpt_oss']['R_gold'])]+[sel(r['models'][name]['P_selected']) for name in NAMES]+[sel(r['models'][name]['R_selected']) for name in NAMES] for r in es['states']])
 table(['Pair','Q P/R pass','M P/R pass','G P/R pass'],[[r['pair_id']]+[f"{r['models'][name]['P_pair_pass']}/{r['models'][name]['R_exact_pair_pass']}" for name in NAMES] for r in es['pairs']])
 out.extend(['','## Registered interpretation','', '```json',json.dumps(s['registered_interpretation'],indent=2),'```','','## Capability and real-system boundary','','Qwen and Ministral capability are immutable published references. gpt-oss capability is measured only under this frozen configuration. Deterministic software verifies, transports, hashes and scores; it does not solve model tasks or pass primitive outputs into reduction. Combined-system capability and interventions are NOT TESTED. Separate primitive calls do not establish internal primitive computation during reduction. Native templates, quantization, reasoning and decoding differ across models; this is not an equal-compute or causal isolation study.','','No Horus, Memory, policy, threshold, architecture or weight change occurs. No training, compiler-assisted diagnosis, model promotion or self-improvement is demonstrated. A benchmark score alone, added deterministic answer rules, prompt tuning or unmeasured model replacement is not durable useful capability. Real progress requires useful behavior surviving prospective testing, an honestly identified cause, and persistence in later operation. Separately authorized engineering may pursue that; this study does not design or build it. Comparator work stops after this publication.'])
 return '\n'.join(out)+'\n'
if __name__=='__main__':
 s=json.loads((P/'scores.json').read_bytes());assert s['status']=='GPT_OSS_EPISTEMIC_COMPARATOR_COMPLETE_V0'
 with (P/'report.md').open('x') as f:f.write(render(s))
