"""Test fixtures and mechanical presentation without generating model evidence."""

from pathlib import Path
import json
import unittest
from unittest.mock import patch

from experiments.model_explorer_integration_v0 import campaign as previous
from experiments.model_explorer_integration_v0.adapter import ForcedOutput
from experiments.model_explorer_memory_study_v1.adapter import MemoryStudyAdapter, presentation
from experiments.model_explorer_memory_study_v1.campaign import fixture, plan, verify_projection, execute, summarize


class StudyTests(unittest.TestCase):
    def test_authorized_fixtures_match_registered_examples(self):
        for study,n,expected in (("A",5,[("ADVANCE",-1)]),("B",6,[("ADVANCE",-1),("HOLD",1)])):
            e=fixture(study,lambda r:None)
            self.assertEqual((e.system.map.current.state,e.system.map.current.version,e.system.next_transaction_id),(1,n,n+1))
            self.assertEqual([(r.action,r.consequence) for r in e.system.memory.records if r.pre_state==1],expected)

    def test_untried_is_not_zero(self):
        canonical=dict(memory=[dict(action="ADVANCE",consequence=-1)])
        semantic=presentation(canonical,"semantic")["memory"]
        self.assertEqual(semantic['UNTRIED'],['HOLD','RETREAT'])
        self.assertEqual(semantic['VERIFIED_PRIOR_OUTCOMES'],[dict(action='ADVANCE',observed_consequences=[-1])])

    def test_order_and_counts_frozen(self):
        schedule=plan()
        self.assertEqual(len(schedule),224)
        self.assertTrue(all(not d['history'] and d['phase']=='bias' for d in schedule[:32]))
        for study,form in [('A','raw'),('A','semantic'),('B','raw'),('B','semantic')]:
            cell=[d for d in schedule[32:] if (d['study'],d['form'])==(study,form)]
            self.assertEqual(len(cell),48)
            self.assertEqual(sum(d['history'] and d['arm_position']==0 for d in cell),12)

    def test_all_registered_prompts_and_integrity_with_forced_output(self):
        # Entire schedule is a harness test, labeled synthetic by the transport.
        setup=[]; rows=[]
        execute(ForcedOutput('HOLD'),rows.append,lambda r:setup.append(r) if r['role']=='setup' else None)
        result=summarize(rows,[])
        self.assertEqual(result['calls'],224)
        self.assertEqual(result['projection_checks'],224)
        self.assertEqual(result['matched_state_checks'],96)
        self.assertEqual(result['violations'],{})
        self.assertEqual(len(setup),1232)
        self.assertTrue(all(not c['supported'] for c in result['cells']))

    def test_unauthorized_or_modified_display_is_detected(self):
        rows=[];e=fixture('B',lambda r:None)
        def factory(*args,**kwargs):return MemoryStudyAdapter(*args,**kwargs,form='semantic')
        with patch.object(previous,'ModelExplorerAdapter',factory):
            row=e.step('model',ForcedOutput('HOLD'),1001)
        registered=json.loads((Path(__file__).parent/'fixtures-and-prompts.json').read_text())
        descriptor=dict(study='B',form='semantic',history=True)
        self.assertTrue(verify_projection(row,descriptor,registered))
        row['model_call']['model_visible_input']['memory']['VERIFIED_PRIOR_OUTCOMES'][0]['observed_consequences']=[1]
        with self.assertRaises(AssertionError):verify_projection(row,descriptor,registered)

    def test_corrupted_memory_is_repaired_before_presentation(self):
        e=fixture('B',lambda r:None)
        def factory(*args,**kwargs):return MemoryStudyAdapter(*args,**kwargs,form='semantic')
        with patch.object(previous,'ModelExplorerAdapter',factory):
            row=e.step('model',ForcedOutput('HOLD'),1001,fault='corrupt_memory')
        self.assertEqual(row['violations'],[])
        shown=row['model_call']['model_visible_input']['memory']['VERIFIED_PRIOR_OUTCOMES']
        self.assertEqual(shown,[dict(action='ADVANCE',observed_consequences=[-1]),dict(action='HOLD',observed_consequences=[1])])


if __name__=='__main__':unittest.main()
