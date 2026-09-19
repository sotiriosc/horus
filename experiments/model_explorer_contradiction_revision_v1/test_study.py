"""Bounded deterministic adapter/history/matching tests; never contacts a model."""
import unittest
from copy import deepcopy
from .adapter import parse, render, serialize
from .campaign import schedule, fixture, registration
from .analysis import summarize


class StudyTests(unittest.TestCase):
    def test_schedule_balance(self):
        plan=schedule()
        self.assertEqual(len(plan),144)
        for family in ("O1","O2"):
            for j in range(12):
                group=[d for d in plan if d['family']==family and d['schedule_id']==j]
                self.assertEqual(len(group),6)
                self.assertEqual({d['seed'] for d in group},{40001+j})
                self.assertEqual(len({tuple(d['options']) for d in group}),1)
                self.assertEqual(group[0]['mapping'][group[0]['options'][0]],'HOLD' if j<6 else 'ADVANCE')

    def test_history_projection_preserves_old_and_new(self):
        d=next(d for d in schedule() if d['arm']=='SHIFT' and d['stage']=='H2')
        system,_,_,_=fixture(d);original=deepcopy(system.inner.memory.records)
        shown=render(original,d)
        self.assertEqual([r['transaction_id'] for r in shown['VERIFIED_CHRONOLOGICAL_HISTORY']],[1,2,4,5,7])
        self.assertEqual([r['consequence'] for r in shown['VERIFIED_CHRONOLOGICAL_HISTORY']],[1,-1,-1,1,-1])
        self.assertEqual(original,system.inner.memory.records)
        self.assertEqual(set(shown),{'state','available_actions','VERIFIED_CHRONOLOGICAL_HISTORY'})
        self.assertNotIn('SHIFT',serialize(shown));self.assertNotIn('HOLD',serialize(shown))

    def test_parser_exact_pair_only(self):
        d=schedule()[0]
        self.assertEqual(parse(' \n'+d['options'][0]+'\t',d)[1],'HOLD')
        for raw in ('HOLD','ADVANCE','X9',' '.join(d['options']),d['options'][0]+' because',None):
            self.assertEqual(parse(raw,d),(None,None))
        third=next(s for s in d['mapping'] if s not in d['options'])
        self.assertEqual(parse(third,d),(None,None))

    def test_annex_matched_prompts(self):
        plan,_=registration()
        for j in range(12):
            for family in ('O1','O2'):
                a,b=[d for d in plan if d['schedule_id']==j and d['family']==family and d['stage']=='H0']
                self.assertEqual(a['exact_prompt'],b['exact_prompt'])

    def test_incomplete_behavior_cannot_be_supported(self):
        result=summarize([],[])
        self.assertFalse(result['global_behavioral_gate'])
        self.assertTrue(all(f['revision']=='NOT_ESTABLISHED' for f in result['families'].values()))


if __name__=='__main__':unittest.main()
