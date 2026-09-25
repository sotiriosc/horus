"""Meaningful boundary checks with deterministic value-only sources."""
import json,unittest
from dataclasses import replace,FrozenInstanceError
from unittest.mock import patch
from .interface import *
from .campaign import fixture,SyntheticMap,SyntheticExplorer,mappings,guarded
from experiments.cross_episode_stale_memory_feasibility_v0.campaign import execute,snap
class Tests(unittest.TestCase):
 def setup_case(self,stage=2):
  m=mappings()[0];c,a,e=fixture(999,m,True,stage);o=ForecastCoordinator(AuthenticatedReader(c,a,e),m['mapping'],'test');return c,a,e,o,o.begin()
 def test_finite_wrong_forecast_is_not_a_fact(self):
  c,a,e,o,s=self.setup_case();before=snap(c);m=SyntheticMap(o.mapping);x=SyntheticExplorer()
  guarded(lambda:s.collect(m));p,_=guarded(lambda:s.choose(x));self.assertEqual(p.underlying_action,'HOLD');self.assertEqual(snap(c),before)
  self.assertEqual(p.selected_forecast.prediction.consequence,1);self.assertEqual(c._active.world.target_consequence,-1)
  with self.assertRaises(FrozenInstanceError):p.selected_forecast.prediction.consequence=0
  self.assertNotIn('verified_outcomes',x.calls[0]['prompt']);self.assertNotIn('RAW',x.calls[0]['prompt'])
 def test_every_action_independent_and_order_bound(self):
  c,a,e,o,s=self.setup_case();ms=SyntheticMap(o.mapping,True);s.collect(ms)
  self.assertEqual([r['underlying_action'] for r in ms.calls],list(ACTIONS))
  inputs=[json.loads(r['prompt']) for r in ms.calls];self.assertEqual([p['target_action'] for p in inputs],['K1','K2','K3'])
  self.assertEqual([[r['consequence'] for r in p['VERIFIED_CHRONOLOGICAL_HISTORY']] for p in inputs],[[-1],[1,-1,-1],[0,0]])
  self.assertEqual(len({f.proposal_id for f in s._forecasts}),3)
 def test_raw_rejection_no_explorer_or_retry(self):
  c,a,e,o,s=self.setup_case();m=SyntheticMap(o.mapping,invalid_action='HOLD',raw='{"next_state":1,"consequence":1} RAW_CANARY');x=SyntheticExplorer()
  with self.assertRaisesRegex(ProposalFailure,'INVALID_MAP'):s.collect(m)
  with self.assertRaises(ProposalFailure):s.choose(x)
  with self.assertRaises(ProposalFailure):s.collect(m)
  self.assertEqual(len(m.calls),2);self.assertEqual(len(x.calls),0)
 def test_payload_detached_and_copy_cannot_be_rebound(self):
  c,a,e,o,s=self.setup_case();view=s.collect(SyntheticMap(o.mapping));view['actions'][0]['map_prediction']['consequence']=777
  self.assertNotEqual(s.view()['actions'][0]['map_prediction']['consequence'],777)
  s._forecasts[0]=replace(s._forecasts[0])
  with self.assertRaisesRegex(ProposalFailure,'FORECAST_IDENTITY'):s.choose(SyntheticExplorer())
 def test_realized_event_during_source_invalidates_request(self):
  c,a,e,o,s=self.setup_case(stage=0);ms=SyntheticMap(o.mapping)
  def interleaved(system,prompt):
   value=ms(system,prompt);execute(c,'HOLD',a,e);return value
  with self.assertRaisesRegex(ProposalFailure,'STALE_CONTEXT'):s.collect(interleaved)
  self.assertEqual(s.map_attempts,1);self.assertEqual(s.explorer_attempts,0)
 def test_decision_reuse_and_source_change_fail_closed(self):
  c,a,e,o,s=self.setup_case();s.collect(SyntheticMap(o.mapping));o.begin()
  with self.assertRaisesRegex(ProposalFailure,'STALE_DECISION'):s.choose(SyntheticExplorer())
  t=o.active;t.owner.reader._source=object()
  with self.assertRaisesRegex(ProposalFailure,'CONTEXT_INVALID'):t.collect(SyntheticMap(o.mapping))
 def test_invalid_and_nonoptimal_explorer_are_not_repaired(self):
  for raw,valid in [('K1',True),('ADVANCE',False),('{"action":"K2"}',False),('K2 because',False)]:
   c,a,e,o,s=self.setup_case();before=snap(c);s.collect(SyntheticMap(o.mapping))
   if valid:self.assertEqual(s.choose(SyntheticExplorer(raw)).underlying_action,'ADVANCE')
   else:
    with self.assertRaisesRegex(ProposalFailure,'INVALID_EXPLORER'):s.choose(SyntheticExplorer(raw))
   self.assertEqual(snap(c),before)
 def test_tie_is_explicit_stop(self):
  c,a,e,o,s=self.setup_case();s.collect(lambda *args:'{"next_state":0,"consequence":0}');x=SyntheticExplorer()
  with self.assertRaisesRegex(ProposalFailure,'TIED_MAXIMUM'):s.choose(x)
  self.assertEqual(len(x.calls),0)
if __name__=='__main__':unittest.main()
