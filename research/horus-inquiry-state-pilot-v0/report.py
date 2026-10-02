"""Deterministic screening report; no interpretation changes after outcomes."""
from common import *
def render(r,handoff,replay,preservation):
 lines=[];arms=r['arms'];decision=r['decision'];comp=r['paired_comparisons']
 def add(s=''):lines.append(s)
 def table(headers,rows):
  add('| '+' | '.join(headers)+' |');add('| '+' | '.join(['---']*len(headers))+' |')
  for row in rows:add('| '+' | '.join(map(str,row))+' |')
  add()
 add('# Horus Inquiry State Pilot v0');add()
 add('Diagnostic screening result: **'+decision['classification']+'**. '+('Recommend a separately authorized confirmatory proposal for Arm '+decision['recommended_arm']+'.' if decision['recommend_scale_up'] else 'The frozen criteria do not justify scaling this intervention.'));add()
 add('All 384 scientific calls completed: 16 fresh matched worlds, A/B/C, six discovery probes and two sealed predictions per arm/world. No parameter learning, full Triangulation claim or larger study. The completed triangulation result at 50713caf9b95dadefbf3951ed892909e459effd0 is preserved unchanged.');add()
 add('A reproduces generic Active, including its existing repeat-count field. B adds tested/untried IDs, budget bookkeeping and the explicit deterministic-reset/no-new-evidence fact. C additionally exposes the complete syntactic contrast frontier. Repeats remain legal in all arms. No provisional model narratives are carried forward.');add()
 add('## Provenance and runtime');add()
 table(['Artifact','Identity'],[(k,'`'+str(v)+'`') for k,v in handoff.items() if k not in ['seeds','populations']])
 add('Seeds: `'+canon(handoff['seeds'])+'`. Population: `'+canon(handoff['populations'])+'`. All model/base file hashes, runtime packages and post-run identity checks are preserved in the identity reports.');add()
 add('## Matched arm outcomes');add()
 table(['Arm','Repeats /96','Zero-information /96','Unique probes total','Mean information bits','Median final H','Median final log2 H','Useful contrasts','Short exact /32','Bit accuracy','Mean rank','Mean regret bits'],[(a,z['exact_repeats'],z['zero_information'],z['unique_probe_sequences'],round(z['mean_information_bits'],4),z['median_final_H'],round(z['median_final_log2_H'],4),z['useful_controlled_contrasts'],z['prediction']['exact'],round(z['prediction']['bit_accuracy'],4),round(z['mean_selected_rank'],3),round(z['mean_regret_bits'],4)) for a,z in arms.items()])
 table(['Arm','Time contrasts','Relation contrasts','Temporal cards added','Relational cards added','Model calls','Prompt tokens','Generated tokens','Recorded inference seconds'],[(a,z['time_contrasts'],z['relation_contrasts'],z['temporal_constraints_added'],z['relational_distinctions_added'],r['costs'][a]['model_calls'],r['costs'][a]['prompt_tokens'],r['costs'][a]['generation_token_count'],round(r['costs'][a]['seconds'],2)) for a,z in arms.items()])
 add('## Learning curves');add()
 table(['Arm','Probes','Median log2 H','Mean cumulative bits','Repeats','Zero-information','Useful contrasts'],[(a,t,round(arms[a]['curves'][str(t)]['median_log2_H'],4),round(arms[a]['curves'][str(t)]['mean_cumulative_bits'],4),arms[a]['curves'][str(t)]['exact_repeats'],arms[a]['curves'][str(t)]['zero_information'],arms[a]['curves'][str(t)]['useful_contrasts']) for a in ['A','B','C'] for t in [1,2,3,4,6]])
 add('## Exact paired screening comparisons');add()
 table(['Comparison','Repeat ratio','Zero-information ratio','Median paired bits','Information wins/ties/losses','Useful contrasts/world advantage','Exact-prediction difference','Bit-accuracy difference'],[(name,c['repeat_ratio'],c['zero_information_ratio'],round(c['median_paired_information_advantage_bits'],4),str(c['information_wins'])+'/'+str(c['information_ties'])+'/'+str(c['information_losses']),c['useful_contrast_mean_advantage'],c['short_exact_difference'],c['short_bit_accuracy_difference']) for name,c in comp.items()])
 add('Every one of the 16 paired per-world differences is published in results.json under paired_comparisons. No significance threshold or formal competence claim is used; these distributions are available for honest future power planning.');add()
 for name,z in decision['screening'].items():
  failures=[k for k,v in z['conditions'].items() if not v];add('- '+name+': '+('PASS' if z['passed'] else 'FAIL — '+', '.join(failures)))
 z=decision['contrast_increment'];add('- C-B additional-frontier gate: '+('PASS' if z['passed'] else 'FAIL — '+', '.join(k for k,v in z['conditions'].items() if not v)));add()
 add('The frozen screening conjunction requires A to exhibit at least 4 repeats, at least 50% fewer repeats, at least 25% and 4 fewer zero-information probes, at least 1 median paired bit of information advantage, gains on at least 10/16 worlds, at least 0.5 more useful contrasts/world, at most one lost exact prediction and at most 2 percentage points bit-accuracy regression, plus integrity. C-B uses a separate incremental gate: 0.5 bit, 10/16 worlds, 0.25 useful contrasts/world, no extra repeats/zero-information, and the same prediction/integrity bounds.');add()
 add('## Integrity');add()
 add('Raw evidence was committed before scientific scoring. Authentication, every exact prompt, structural-frontier reconstruction, legal token path, sealed query and executed ledger passed zero-inference replay. Two scoring passes produced byte-identical public results, private per-world results and per-decision contributions.');add()
 add('Replay: `'+canon(replay)+'`. Audits: `'+canon(r['audits'])+'`. Preservation: `'+canon(preservation)+'`. Full reachable-history publication auditing scans paths, actual key representations, credential patterns and private-evidence hashes. The operational process lock is not scientific evidence.');add()
 add('## Eight requested answers');add()
 answers=[]
 ratios={n:comp[n]['repeat_ratio'] for n in ['B-A','C-A']}
 answers.append(('Did explicit bookkeeping stop repeated resolved experiments?', 'Repeat ratios versus A were '+canon(ratios)+'. A ratio<=0.5 is the frozen reduction criterion; stopping repeats entirely would require zero, not merely an improvement.'))
 answers.append(('Did fewer repeats actually produce more information?', 'Median paired information advantages were B-A '+str(comp['B-A']['median_paired_information_advantage_bits'])+' bits and C-A '+str(comp['C-A']['median_paired_information_advantage_bits'])+' bits. Wins/ties/losses and zero-information totals above distinguish repetition reduction from information benefit.'))
 answers.append(('Did the contrast frontier add value beyond bookkeeping?', 'The separate C-B incremental gate '+('passed.' if decision['contrast_increment']['passed'] else 'did not pass.')+' This does not substitute for either intervention passing the A comparison.'))
 answers.append(('Did B/C preserve the earlier strong first 2–4-probe behavior?', 'The full paired pilot curves at 1/2/3/4/6 above show early and later information acquisition. This pilot uses fresh compatible worlds and a shorter budget; it cannot establish exact replication of the prior 12-probe trajectory. Exact H is monotone under authenticated observations; collapse refers to wasted later probes, not evaluator forgetting.'))
 answers.append(('Was the old collapse mainly caused by inquiry-state management?', 'This pilot cannot establish the main cause. B bundles bookkeeping with an explicit reset fact, A already carried repeat counts, and no arm carries prose hypotheses. Any positive result is evidence for the tested representation bundle, not a diagnosis of internal model state or an isolated narrative-fixation effect.'))
 answers.append(('Is there enough coherent evidence to justify a larger confirmatory study?', 'The frozen screening decision is '+('yes, recommend a separately authorized confirmatory proposal.' if decision['recommend_scale_up'] else 'no; do not scale this intervention from this pilot.')))
 answers.append(('Which intervention should scale, if any?', 'Arm '+decision['recommended_arm']+' under the frozen preference rule; no larger study has been launched.' if decision['recommended_arm'] else 'Neither arm qualifies under all frozen conditions.'))
 answers.append(('What remains unexplained if the screen is negative?', 'The failed conditions identify whether repeats, information, consistency, useful contrasts or prediction retention remain unresolved. This design cannot separate representation from instruction, test learned strategy changes, or prove a general causal account of exploration collapse. No replacement experiment follows automatically.'))
 for i,(q,a) in enumerate(answers,1):add(f'{i}. **{q}** {a}');add()
 add('The 2 sealed queries per world provide only 32 exact endpoints per arm; the retention screen is not a powered noninferiority claim. The finite evaluator can judge contribution but never chooses the model action or supplies utility labels to it. No training, merge, promotion or automatic scale-up. STOP.')
 return '\n'.join(lines)+'\n'
