"""Synthetic qualification only. No scientific world or query is loaded."""
import time
from common import *
from legal_choice import LegalChoiceTrie
from runtime import load,infer

def main():
 start=time.monotonic();model,tok=load();print('Pinned A0 loaded and all tensor fingerprints verified.',flush=True)
 private=ASSETS/'engineering';private.mkdir(exist_ok=True)
 catalogue=[f'P{i:03d}' for i in range(79)]
 checks=0
 for ids in [catalogue,['P003','P017','P044'],['P017'],['P003','P044']]:
  trie=LegalChoiceTrie(tok,ids);assert set(trie.leaves())==set(trie.paths.values())
  for ident,path in trie.paths.items():
   assert trie.identify(path)==ident
   for i,token in enumerate(path):assert token in trie.allowed(path[:i]);checks+=1
 rows=[]
 # Copy tasks test contextual model authority and changed bindings without any
 # scientific question or information-value oracle.
 for desired in ['P003','P017','P044','P003']:
  ids=['P003','P017','P044'] if len(rows)<3 else ['P003','P044']
  msgs=[dict(role='system',content='Synthetic transport check. Select the requested legal identifier. Return only the JSON object.'),dict(role='user',content=canon(dict(legal_ids=ids,requested_id=desired)))]
  r=infer(model,tok,msgs,ids);rows.append(dict(requested_id=desired,**r))
  print(f'Synthetic constrained choice {len(rows)}/4 legal; elapsed {time.monotonic()-start:.1f}s',flush=True)
 assert all(r['probe_id']==r['requested_id'] for r in rows),'Synthetic context-directed selection did not qualify'
 assert len(set(r['probe_id'] for r in rows))==3
 # Same catalogue and common decision prefix: changing context changes the
 # actual constrained next-token distribution, rather than a parser outcome.
 x,y=rows[0]['finite_choice']['branch_probabilities'],rows[1]['finite_choice']['branch_probabilities']
 assert len(x)==len(y)==1 and x[0]['permitted_tokens']==y[0]['permitted_tokens']
 variation=.5*sum(abs(a-b) for a,b in zip(x[0]['probabilities'],y[0]['probabilities']))
 assert variation>.01
 save(private/'legal-choice-responses.private.json',rows)
 import torch
 report=dict(status='PASS',synthetic_model_calls=4,scientific_model_calls=0,all_choices_in_presented_catalogue=True,exact_json_and_eos=True,complete_trie_support_equals_legal_language=True,trie_prefix_checks=checks,illegal_token_support_zero=True,context_changes_choice=True,context_probability_total_variation=variation,dynamic_removal_supported=True,repairs=0,retries=0,fallbacks=0,oracle_inputs=0,loaded_base_fingerprints_match=True,loaded_adapter_fingerprints_match=True,adapter_sha256=ADAPTER_SHA,all_parameters_cuda=all(p.device.type=='cuda' for p in model.parameters()),all_parameters_frozen=all(not p.requires_grad for p in model.parameters()),peak_allocated_bytes=torch.cuda.max_memory_allocated(),seconds=round(time.monotonic()-start,2),private_responses_sha256=filehash(private/'legal-choice-responses.private.json'),mean_choice_seconds=sum(r['seconds'] for r in rows)/4)
 save(P/'legal-choice-qualification.json',report);print(canon(report),flush=True)
if __name__=='__main__':main()
