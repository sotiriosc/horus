"""Deterministic, bounded interpretation of frozen results; no inference."""
from common import *
def render(r,handoff,replay,preservation):
 arms=['P','A','T'];g=r['gates'];supported=lambda name:g[name]['supported'];lines=[]
 def add(s=''):lines.append(s)
 def table(headers,rows):
  add('| '+' | '.join(headers)+' |');add('| '+' | '.join(['---']*len(headers))+' |')
  for row in rows:add('| '+' | '.join(map(str,row))+' |')
  add()
 add('# Horus Triangulation Learning v0');add()
 add('Classification: **'+r['classification']+'**. All 120 prediction worlds and 40 control worlds were completed with P/A/T, twelve discovery probes per arm, and 9,600 complete model responses. Results are bounded to the frozen family, model, prompts and budgets.');add()
 add('For control, the same frozen target was available before discovery to all arms. Passive remained independent of it. Observations alone changed the exact evaluator hypothesis set; model hypotheses never became authenticated truth.');add()
 add('## Provenance');add()
 table(['Artifact','Identity'],[(k,'`'+str(v)+'`') for k,v in handoff.items() if k not in ['seeds','populations','model_base_files_sha256']])
 add('Seeds: `'+canon(handoff['seeds'])+'`. Populations: `'+canon(handoff['populations'])+'`. All base shard/configuration hashes are in identity-preflight.json and post-run-identity.json.');add()
 add('## Predictions and control');add()
 table(['Arm','Short exact /600','Long exact /360','Control success /40','Model calls','Inference seconds'],[(a,r['prediction']['short'][a]['exact'],r['prediction']['long'][a]['exact'],r['control'][a]['successes'],r['costs'][a]['model_calls'],round(r['costs'][a]['inference_seconds'],2)) for a in arms])
 add('Full bit/step accuracy, confusion counts, error categories, baseline matches and model token costs are in results.json. Invalid traces receive zero credit; no prediction is repaired.');add()
 table(['Comparison','Short gain pp','Short paired p','Long gain pp','Long paired p','Median paired bits','Uncertainty area ratio','Control success gain','Control paired p'],[(name,round(c['short']['accuracy_gain']*100,3),c['short'].get('holm_p',c['short']['world_paired_signflip']['p']),round(c['long']['accuracy_gain']*100,3),c['long'].get('holm_p',c['long']['world_paired_signflip']['p']),round(c['information']['median_paired_bits'],4),c['information']['uncertainty_area_ratio'],c['control']['success_gain'],c['control'].get('holm_p',c['control']['paired_mcnemar']['p'])) for name,c in r['comparisons'].items()])
 add('Prediction inference uses exact whole-world paired sign flips. T-P/T-A p-values are Holm adjusted within each named prediction gate. Control uses two-sided exact paired McNemar and Holm for T comparisons. A-P values are unadjusted. Endpoint McNemar is descriptive only. Information uses a separate exact paired sign test.');add()
 add('## Learning and contribution');add()
 table(['Arm','Median final H','Mean bits/probe','Mean useful contrasts/world','Time contrasts','Relation contrasts','Zero-information probes','Exact repeats'],[(a,r['information']['primary'][a]['median_final_H'],round(r['information']['primary'][a]['mean_information_per_experiment'],4),r['information']['primary'][a]['mean_useful_contrasts_per_world'],r['information']['primary'][a]['counts']['time_contrast'],r['information']['primary'][a]['counts']['relation_contrast'],r['information']['primary'][a]['counts']['zero_information'],r['information']['primary'][a]['counts']['repeat']) for a in arms])
 table(['Probe count','P median log2 H','A median log2 H','T median log2 H','P unique fraction','A unique fraction','T unique fraction'],[(t,*[round(r['information']['primary'][a]['curves'][str(t)]['median_log2_H'],4) for a in arms],*[r['information']['primary'][a]['curves'][str(t)]['fraction_unique'] for a in arms]) for t in [0,1,2,3,4,6,8,12]])
 add('The full learning curves, abstract experiment-selection frequencies, legal-action ranks/regret, actuator costs, temporal/relational cards and control contribution metrics are in results.json. Every executed decision and all 79 evaluator probe values are preserved privately and committed by SHA256; they were never model-visible.');add()
 table(['Arm','Target information/probe','Target-zero-information fraction','Target propositions resolved/world','Successful control mean actions','Failed control probes'],[(a,r['control'][a]['mean_target_information_per_probe'],r['control'][a]['target_zero_information_probe_fraction'],r['control'][a]['mean_target_propositions_resolved_per_world'],r['control'][a]['mean_actuator_actions_successful'],r['control'][a]['failed_probes']) for a in arms])
 add('Grounded T alternatives/falsifications: `'+canon(r['grounded_falsification'])+'`. These require opposite observable alternatives viable under pre-experiment H; prose does not establish a true explanation.');add()
 add('## Frozen gates');add()
 table(['Gate','Supported'],[(name,value['supported']) for name,value in g.items()])
 for name,value in g.items():
  def failed(x,prefix=''):
   out=[]
   for k,v in x.items():
    if k=='supported':continue
    if isinstance(v,dict):out+=failed(v,prefix+k+'.')
    elif v is False:out.append(prefix+k)
   return out
  add('- '+name+': '+('all registered conditions passed' if value['supported'] else 'failed conditions: '+', '.join(failed(value)))+'.')
 add();add('The 120/40 populations were retained prospectively. Power planning did not guarantee the conjunction of all demanding gates, especially small or strongly correlated effects. Failed gates mean the corresponding bounded claim was not established.');add()
 add('## Integrity and preservation');add()
 add('Raw evidence was committed before scoring. Zero-inference collector reconstruction checked every prompt, rendered template, generated token path, legal selection, receipt, complete ledger and control execution. Two scoring runs produced byte-identical results, per-world results and per-decision contributions. Replay receipt: `'+canon(replay)+'`.');add()
 add('Persistence references: `'+canon(r['baselines'])+'`. Short common-trace qualification capped accuracy at20%; constant persistence at0%. Long traces exclude all period1–3 repeats and holding the third-step estimate. Registered ceiling is30%.');add()
 add('Audits: `'+canon(r['audits'])+'`. Preservation: `'+canon(preservation)+'`. Publication scans every reachable commit/path and unique blob, unchanged credential rules, actual authority-key representations and private file hashes. Private archives, model/reasoning outputs, raw signed streams, keys, hidden programs and databases are not publication artifacts. Exact pushed-head verification is kept in the private publication receipt.');add()
 add('## Requested interpretation');add()
 answers=[
 ('Does choosing experiments actively beat passive observation?', 'The registered A-P evidence gate '+('passed.' if supported('ACTIVE_EVIDENCE_ACQUISITION_SUPPORTED') else 'did not pass; the full bounded claim is not established.')),
 ('Does Triangulation beat generic active exploration?', 'The registered T-A gate '+('passed.' if supported('TRIANGULATION_OVER_ACTIVE_SUPPORTED') else 'did not pass.')),
 ('Does Time constrain later experimentation?', 'The temporal cards and time-contrast counts measure compatible distinctions acquired. This three-arm design does not isolate the causal effect of the Time instruction; no axis ablation was run.'),
 ('Do Relation contrasts expose conditional interactions?', 'Observed endpoint deltas and additional H-entailed relation cards are measured. They support only the tested contexts and finite family, not a global causal rule.'),
 ('Does Direction reduce irrelevant experimentation?', 'Known-target mutual information and target-zero-information fractions above measure destination relevance. Any arm difference is descriptive for the whole method; the Direction axis was not separately randomized.'),
 ('Does T preferentially choose controlled contrasts?', 'T minus A useful contrasts per primary world = '+str(r['comparisons']['T-A']['information']['useful_contrasts_mean_advantage'])+'. T useful fraction = '+str(r['information']['primary']['T']['useful_contrast_fraction'])+'. These are executed structural comparisons.'),
 ('Does T seek falsification rather than confirmation?', 'The grounded alternative/falsification counts above test observable predictions, not intent. P/A did not emit comparable analysis, so no between-arm claim about falsification intent is justified.'),
 ('Does T reduce uncertainty faster per executed experiment?', 'T/P and T/A normalized area ratios are '+str(r['comparisons']['T-P']['information']['uncertainty_area_ratio'])+' and '+str(r['comparisons']['T-A']['information']['uncertainty_area_ratio'])+'. Values below1 describe faster average reduction; the registered threshold is0.90 together with paired final-information conditions.'),
 ('Can short experiments support unseen longer sequences?', 'The separate short-to-long gate '+('passed.' if supported('SHORT_TO_LONG_CAUSAL_EXTRAPOLATION_SUPPORTED') else 'did not pass.')),
 ('Does better experimentation improve control?', 'The separate matched control-benefit gate '+('passed.' if supported('TRIANGULATION_CONTROL_BENEFIT_SUPPORTED') else 'did not pass.')),
 ('Which capabilities came from the model and deterministic machinery?', 'The model generated hypotheses, selected legal IDs and predicted sensor bits. Deterministic code restricted syntax/action availability, executed machines, authenticated observations, planned from model predictions, and evaluated exact H, contribution and significance. The evaluator never selected A/T discovery experiments.'),
 ('Does this justify a separate experiment-selection learning study?', ('A separately authorized learning study is warranted by the bounded primary gate; no training is authorized or performed here.' if supported('TRIANGULATION_EVIDENCE_ACQUISITION_SUPPORTED') else 'This study does not establish the primary prerequisite for an automatic learning progression. Any future diagnostic or learning study needs its own justification and authorization.')),
 ('What remains before bounded recursive self-improvement?', 'A separately frozen learning intervention, authenticated training evidence, improved selection on genuinely new worlds, efficient repeated improvement, independent replication and preservation of safety/authority boundaries remain untested.')]
 for i,(q,a) in enumerate(answers,1):add(f'{i}. **{q}** {a}');add()
 add('T received an additional analysis call per discovery step. Results compare complete method bundles and do not isolate framing from extra reasoning compute. No weights were updated. No RSI, consciousness, general causal intelligence or universal truth-discovery claim follows. No merge, promotion or subsequent study. STOP.')
 return '\n'.join(lines)+'\n'
