"""Deterministic synthetic sources only. Sockets forbidden throughout the campaign."""
import json
from dataclasses import asdict,replace
from pathlib import Path
from unittest.mock import patch
from experiments.cross_episode_stale_memory_explorer_revision_v1.contexts import Context as HistoricalContext,schedule as historical_schedule
from experiments.cross_episode_initialization_boundary_v1.boundary import EpisodeController,EpisodePlan
from experiments.cross_episode_stale_memory_feasibility_v0.campaign import execute,snap,boundary_observer
from experiments.base_framework_v1.hidden_oracle import TrueWorldOracle
from experiments.model_proposal_role_composition_v2.protocol import schedule as mappings
from experiments.realized_event_grounding_v0.framework import evidence as receipt_package
from experiments.realized_event_grounding_v0.receipt import RealizedEventReceipt
from experiments.base_framework_v0.framework import MemoryRecord
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import file_digest
from .interface import AuthenticatedReader,ForecastCoordinator,ProposalFailure,CurrentActionForecast,ExplorerProposal,ACTIONS,serialize
ROOT=Path(__file__).resolve().parents[2];PACKAGE=Path(__file__).parent;PARENT='6448aaca17bdc748f468a93e72a355bdb5331450'
READY='A — MAP-GUIDED EXPLORER INTERFACE READY';BOUNDARY='B — ROLE / AUTHORITY BOUNDARY FAILURE';MISSING='C — NOT ESTABLISHED'
INVARIANTS=('forecast_distinct_from_Memory','no_raw_cross_role_text','finite_action_identity','all_legal_actions_required','invalid_missing_fail_closed','no_automatic_retry','freshness_bound','Explorer_has_no_authority','wrong_Map_admitted','no_hidden_truth_repair','UNKNOWN_unchanged','Memory_unchanged','Measure_post_execution','Recovery_post_execution','receipt_authority_unchanged','historical_APIs_results_unchanged','exact_replay','historical_regressions')

def frozen():
 r=json.loads((PACKAGE/'frozen-inputs.json').read_text())
 for n,h in r['sha256'].items():assert file_digest(ROOT/n)==h,n
 return r

class SyntheticMap:
 def __init__(self,mapping,changed=False,invalid_action=None,raw=None):self.mapping=mapping;self.changed=changed;self.invalid_action=invalid_action;self.raw=raw;self.calls=[]
 def __call__(self,system,prompt):
  p=json.loads(prompt);a=self.mapping[p['target_action']]
  result=self.raw if a==self.invalid_action else serialize(dict(next_state=dict(ADVANCE=2,HOLD=1,RETREAT=0)[a],consequence=dict(ADVANCE=-1,HOLD=-1 if self.changed else 1,RETREAT=0)[a]))
  self.calls.append(dict(system=system,prompt=prompt,raw=result,underlying_action=a));return result
class SyntheticExplorer:
 def __init__(self,raw=None):self.raw=raw;self.calls=[]
 def __call__(self,system,prompt):
  p=json.loads(prompt);assert set(p)=={'state','actions'} and len(p['actions'])==3
  assert all(set(row)=={'action','map_prediction'} and set(row['map_prediction'])=={'next_state','consequence'} for row in p['actions'])
  result=self.raw if self.raw is not None else max(p['actions'],key=lambda x:x['map_prediction']['consequence'])['action']
  self.calls.append(dict(system=system,prompt=prompt,raw=result));return result

def fixture(index,m,changed=False,stage=2):
 d=dict(index=2000+index,schedule=0,family=m['family'],family_index=int(m['family'][1])-1,mapping_index=m['mapping_index'],mapping=m['mapping'],seed=0,arm='CHANGED' if changed else 'CONTROL',stage=('P0','P1','P2')[stage],stage_index=stage,role='NONE')
 h=HistoricalContext(d);return h.c,h.authentic,h.executions

def guarded(call):
 with boundary_observer() as effects,patch.object(TrueWorldOracle,'execute',side_effect=AssertionError('NO HIDDEN WORLD QUERY')):
  value=call()
 assert all(v==0 for v in effects.values()),effects
 return value,dict(effects)

def expect_failure(call,codes):
 try:call()
 except ProposalFailure as e:
  assert str(e) in codes,(str(e),codes);return str(e)
 raise AssertionError('proposal boundary accepted forbidden operation')

def run():
 frozen();details=[];idx=0
 with patch('socket.socket',side_effect=AssertionError('ZERO MODEL CALLS')) as network:
  for m in mappings():
   for kind in ('CONTROL','CHANGED','WRONG_MAP','INVALID_MAP','EMPTY_HISTORY'):
    idx+=1;changed=kind in ('CHANGED','WRONG_MAP')
    if kind=='EMPTY_HISTORY':c=EpisodeController(f'EMPTY_{idx}');auth={};actual={}
    else:c,auth,actual=fixture(idx,m,changed)
    before=snap(c);owner=ForecastCoordinator(AuthenticatedReader(c,auth,actual),m['mapping'],f'case{idx}');s=owner.begin()
    ms=SyntheticMap(m['mapping'],kind=='CHANGED',invalid_action='HOLD' if kind=='INVALID_MAP' else None,raw='{"next_state":true,"consequence":1}')
    es=SyntheticExplorer()
    def pipeline():
     if kind=='INVALID_MAP':return expect_failure(lambda:s.collect(ms),{'INVALID_MAP'})
     view=s.collect(ms);assert [r['action'] for r in view['actions']]==list(m['mapping'])
     assert [x['underlying_action'] for x in ms.calls]==list(ACTIONS)
     view['actions'][0]['map_prediction']['consequence']=777
     assert all(row['map_prediction']['consequence'] in (-1,0,1) for row in s.view()['actions'])
     p=s.choose(es);assert s.validate(p)
     assert p.underlying_action==('RETREAT' if kind=='CHANGED' else 'HOLD')
     assert type(p) is ExplorerProposal and type(p.selected_forecast) is CurrentActionForecast
     assert not isinstance(p,(MemoryRecord,RealizedEventReceipt)) and not isinstance(p.selected_forecast,(MemoryRecord,RealizedEventReceipt))
     try:receipt_package(p)
     except (AttributeError,TypeError):pass
     else:raise AssertionError('proposal accepted as receipt')
     if kind=='EMPTY_HISTORY':assert all(json.loads(x['prompt'])['VERIFIED_CHRONOLOGICAL_HISTORY']==[] for x in ms.calls)
     return p.underlying_action
    value,effects=guarded(pipeline);assert snap(c)==before
    assert len(es.calls)==(0 if kind=='INVALID_MAP' else 1) and len(ms.calls)==(2 if kind=='INVALID_MAP' else 3)
    if kind=='WRONG_MAP':assert c._active.world.target_consequence==-1 and value=='HOLD'
    details.append(dict(case=kind,family=m['family'],mapping_index=m['mapping_index'],value=value,passed=True,protected_unchanged=True,before=before,after=snap(c),effects=effects,session=s.evidence(),Map_source=ms.calls,Explorer_source=es.calls))
  m=mappings()[0]
  # Invalids at every collection position, bounded errors and zero Explorer calls.
  invalids=[('malformed','{'),('parser_rejection','{"next_state":1,"consequence":1,"extra":"RAW_CANARY"}'),('missing',None)]
  for action in ACTIONS:
   for name,raw in invalids:
    idx+=1;c,auth,actual=fixture(idx,m);before=snap(c);s=ForecastCoordinator(AuthenticatedReader(c,auth,actual),m['mapping'],f'case{idx}').begin();ms=SyntheticMap(m['mapping'],invalid_action=action,raw=raw);es=SyntheticExplorer()
    def bad():
     code=expect_failure(lambda:s.collect(ms),{'INVALID_MAP'})
     expect_failure(lambda:s.choose(es),{'EXPLORER_UNAVAILABLE'});expect_failure(lambda:s.collect(ms),{'COLLECTION_ALREADY_ATTEMPTED'});return code
    code,effects=guarded(bad);assert snap(c)==before and not es.calls and len(ms.calls)==ACTIONS.index(action)+1
    details.append(dict(case='INVALID_'+name,action=action,passed=True,protected_unchanged=True,effects=effects,session=s.evidence(),source_calls=len(ms.calls),Explorer_calls=0,initial_failure=code))
  # Explicit tie, missing collected forecast, detached copy, alias swap, bad Explorer.
  for kind in ('TIE','MISSING_COLLECTED','FORGED_COPY','ALIAS_SWAP','INVALID_EXPLORER','VALID_WRONG_EXPLORER','REPEATED_CHOICE','SOURCE_FAILURE'):
   idx+=1;c,auth,actual=fixture(idx,m);before=snap(c);s=ForecastCoordinator(AuthenticatedReader(c,auth,actual),m['mapping'],f'case{idx}').begin();ms=SyntheticMap(m['mapping']);es=SyntheticExplorer('K1 extra RAW_CANARY' if kind=='INVALID_EXPLORER' else 'K1' if kind=='VALID_WRONG_EXPLORER' else None)
   def faults():
    if kind=='SOURCE_FAILURE':
     def throwing(*args):raise RuntimeError('RAW_ERROR_CANARY')
     expect_failure(lambda:s.collect(throwing),{'MAP_SOURCE_FAILURE'});return
    if kind=='TIE':
     s.collect(lambda *args:'{"next_state":1,"consequence":1}');expect_failure(lambda:s.choose(es),{'TIED_MAXIMUM'});return
    s.collect(ms)
    if kind=='MISSING_COLLECTED':s._forecasts.pop();expect_failure(lambda:s.choose(es),{'MISSING_FORECAST'})
    elif kind in ('FORGED_COPY','ALIAS_SWAP'):
     s._forecasts[0]=replace(s._forecasts[0],action_alias='K2') if kind=='ALIAS_SWAP' else replace(s._forecasts[0]);expect_failure(lambda:s.choose(es),{'FORECAST_IDENTITY'})
    elif kind=='INVALID_EXPLORER':expect_failure(lambda:s.choose(es),{'INVALID_EXPLORER'})
    else:
     p=s.choose(es)
     if kind=='VALID_WRONG_EXPLORER':assert p.underlying_action=='ADVANCE'
     else:expect_failure(lambda:s.choose(es),{'EXPLORER_UNAVAILABLE'})
   _,effects=guarded(faults);assert snap(c)==before and s.explorer_attempts<=1 and s.map_attempts<=3
   details.append(dict(case=kind,passed=True,protected_unchanged=True,effects=effects,session=s.evidence(),Explorer_source=es.calls))
  # Freshness: same-state new Memory, changed state, epoch, decision, cross-decision cache.
  for kind in ('MEMORY_EVENT','STATE_EVENT','EPOCH','NEW_DECISION','OLD_FORECAST_IN_NEW_DECISION'):
   idx+=1
   if kind=='EPOCH':
    c=EpisodeController(f'EPOCH_{idx}',EpisodePlan(initial_state=1));auth={};actual={};execute(c,'HOLD',auth,actual)
   else:c,auth,actual=fixture(idx,m,stage=0)
   reader=AuthenticatedReader(c,auth,actual);owner=ForecastCoordinator(reader,m['mapping'],f'case{idx}');s=owner.begin();ms=SyntheticMap(m['mapping']);es=SyntheticExplorer()
   guarded(lambda:s.collect(ms));pre_change=snap(c)
   if kind=='MEMORY_EVENT':execute(c,'HOLD',auth,actual)
   elif kind=='STATE_EVENT':execute(c,'RETREAT',auth,actual)
   elif kind=='EPOCH':c.start_episode(1002,1)
   else:
    newer=owner.begin()
    if kind=='OLD_FORECAST_IN_NEW_DECISION':
     guarded(lambda:newer.collect(SyntheticMap(m['mapping'])));newer._forecasts[0]=s._forecasts[0];s=newer
   after_change=snap(c)
   code,effects=guarded(lambda:expect_failure(lambda:s.choose(es),{'STALE_CONTEXT','STALE_DECISION','FORECAST_IDENTITY'}))
   assert snap(c)==after_change and not es.calls
   if kind in ('MEMORY_EVENT','STATE_EVENT'):
    fresh=owner.begin();guarded(lambda:fresh.collect(SyntheticMap(m['mapping'])));assert fresh.decision_id!=s.decision_id and fresh.map_attempts==3
   details.append(dict(case=kind,passed=True,proposal_stage_unchanged=True,before_change=pre_change,after_change=after_change,effects=effects,code=code,session=s.evidence(),Explorer_calls=0))
  assert network.call_count==0
 invariants={k:True for k in INVARIANTS};invariants['exact_replay']=invariants['historical_regressions']=None
 result=dict(study='map-guided-explorer-interface-v0',parent=PARENT,classification=MISSING,eligible_classification=READY,status='AWAITING_REPLAY_AND_PRESERVATION',actual_model_calls=0,network_attempts=0,
  invariant_results=invariants,synthetic_cases=len(details),case_counts={k:sum(d['case']==k for d in details) for k in sorted({d['case'] for d in details})},all_cases_passed=all(d['passed'] for d in details),
  registered_mappings=12,collection_order=list(ACTIONS),render_order='frozen opaque mapping key order',tie_rule='STOP before Explorer on tied predicted maximum',
  future_call_limit=dict(Map=3,Explorer=1,retries=0),primary_executed_proposals=0,forecast_type='CurrentActionForecast',claim_scope='Finite read-only input binding, not model behavior.')
 return result,dict(cases=details)
