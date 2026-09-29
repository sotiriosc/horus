"""Zero-inference integration regressions; disposable protected unit fixtures only."""
from contextlib import contextmanager
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import json, subprocess, sys, unittest

from horus.live import SessionStore, SessionError
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory
from experiments.grounded_stagnation_escape_evaluation_v0 import worker as base
from experiments.grounded_stagnation_escape_promotion_controlled_v0 import worker as incumbent
from experiments.empirical_evidence_acquisition_proposal_v0 import candidate as E
from experiments.empirical_evidence_acquisition_proposal_v0.test_candidate import context as synthetic
from grounded_agent.policy import promoted_decide
from grounded_agent.empirical_policy import integrated_decide
from grounded_agent.empirical_adapter import authenticated_projection, recommendation, IntegrationInvariantError


class NoModel:
    def generate(self, *args, **kwargs): raise AssertionError('inference forbidden')


@contextmanager
def fixture(values=(-1,0,-1,0), state=1, target_cost=-1, target_state=None):
    with TemporaryDirectory() as tmp:
        root=Path(tmp)
        def outcome(case,s,a,visit,index):
            if a=='HOLD': return s, values[visit-1] if visit<=len(values) else 0
            return (s if target_state is None else target_state),target_cost
        with patch.object(base,'scenario_override',outcome):
            with SessionStore(root/'session',False) as store,ModernMemory(root/'memory.sqlite3',True) as memory:
                store.save(state=state,next_transaction_id=1)
                for _ in values:base.execute(store,memory,'UNIT','E',0,'HOLD','REGISTERED_SETUP',setup=True)
                yield root,store,memory


def execute_choice(s,m,choice,index=1):
    action,source,route,info,aa,suffix=choice
    return base.execute(s,m,'UNIT','E',index,action,source,route,info,aa,counter_before=suffix['count'])


class IntegrationTests(TestCase):
    def test_I1_ordinary_model_request_semantics_unchanged(self):
        for values in ((),(1,0,1,1)):
            with self.subTest(values=values),fixture(values) as (_,s,m):
                info=dict(raw='{"selected_action":"HOLD"}',transport_error=None,call_id='UNIT:FIXED',raw_output_sha256='f'*64,request_sha256='e'*64,context_tokens=0,output_tokens=0,latency_seconds=0)
                with patch.object(incumbent,'call_model',return_value=deepcopy(info)) as mock:
                    old=promoted_decide(s,m,NoModel(),1);old_args=mock.call_args
                with patch.object(incumbent,'call_model',return_value=deepcopy(info)) as mock:
                    new=integrated_decide(s,m,old_args.args[1],1);new_args=mock.call_args
                self.assertEqual(old,new)
                self.assertEqual(old_args,new_args)
                self.assertEqual(new[3]['status'],'VALID')

    def test_I2_S_exact_domain_and_structural_exclusivity(self):
        from grounded_agent.test_promotion import PromotionTests
        from experiments.grounded_stagnation_escape_evaluation_v0 import candidate as S
        with fixture((0,),state=0,target_cost=0) as (_,s,m):
            helper=PromotionTests()
            for i in range(1,4):helper._fallback(s,m,i)
            ctx=incumbent.context(s,m,4)
            self.assertEqual(S.escape_choice(s,m,0,ctx['assessments'])[0],'ADVANCE')
            self.assertFalse(recommendation(ctx,authenticated_projection(s,m))['eligible'])
            with patch.object(incumbent,'canonical_action_decision',side_effect=AssertionError('ordinary route')):
                choice=integrated_decide(s,m,NoModel(),4)
            self.assertEqual((choice[0],choice[1],choice[2]['route']),('ADVANCE','STAGNATION_ESCAPE','ESCAPE'))
            self.assertIsNone(choice[3]['call_id'])

    def test_I3_E_exact_domain_model_free_and_no_mutable_state(self):
        with fixture() as (_,s,m):
            ctx=incumbent.context(s,m,1)
            self.assertIsNone(incumbent.escape_choice(s,m,ctx['state'],ctx['assessments'])[0])
            before=m.checkpoint();checkpoint_keys=set(s.checkpoint);events=deepcopy(s.records['events'])
            choice=integrated_decide(s,m,NoModel(),1)
            self.assertEqual((choice[0],choice[1],choice[2]['reason']),('ADVANCE',E.SOURCE,E.TRIGGER_REASON))
            self.assertEqual(choice[3]['status'],'NOT_CALLED');self.assertIsNone(choice[3]['call_id'])
            self.assertEqual(m.checkpoint(),before);self.assertEqual(events,s.records['events'])
            self.assertEqual(set(s.checkpoint),checkpoint_keys)
            self.assertEqual([x['kind'] for x in s.records['calls']],['ACTION_FROZEN'])
            self.assertEqual(s.records['calls'][-1]['record']['reason'],E.TRIGGER_REASON)
            self.assertTrue(recommendation(incumbent.context(s,m,1),authenticated_projection(s,m))['eligible'])

    def test_I4_grounded_ceiling_has_priority(self):
        with fixture(target_cost=1) as (_,s,m):
            base.execute(s,m,'UNIT','E',0,'ADVANCE','REGISTERED_SETUP',setup=True)
            with patch('grounded_agent.empirical_policy.recommendation',side_effect=AssertionError('E consulted for mechanical route')):
                result=integrated_decide(s,m,NoModel(),1)
            self.assertEqual((result[0],result[1]),('ADVANCE','GROUNDED_MECHANICAL'))
            self.assertIsNone(result[3]['call_id'])

    def test_I5_omitted_projection_aborts_without_fallback(self):
        with fixture() as (_,s,m):
            history=authenticated_projection(s,m)
            with patch('grounded_agent.empirical_policy.authenticated_projection',return_value=history[1:]):
                with self.assertRaisesRegex(IntegrationInvariantError,'invalid E projection'):
                    integrated_decide(s,m,NoModel(),1)
            self.assertEqual(s.records['calls'],[])

    def test_simultaneous_eligibility_is_invariant_error(self):
        with fixture() as (_,s,m):
            ctx=incumbent.context(s,m,1)
            with patch.object(incumbent,'escape_choice',return_value=('ADVANCE',ctx['suffix'])):
                with self.assertRaisesRegex(IntegrationInvariantError,'simultaneously'):
                    integrated_decide(s,m,NoModel(),1)
            self.assertEqual(s.records['calls'],[])

    def test_in_memory_and_disk_tampering_fail_closed(self):
        with fixture() as (root,s,m):
            s.records['events'][-1]['record']['receipt']['realized_consequence']=1
            with self.assertRaisesRegex(IntegrationInvariantError,'stream differs'):
                integrated_decide(s,m,NoModel(),1)
            self.assertEqual(s.records['calls'],[])
        with fixture() as (root,s,m):
            path=root/'session'/'events.jsonl';path.write_text(path.read_text().replace('AUTHORIZED_REALIZED_EVENT','FORGED_EVENT'))
            with self.assertRaises(SessionError):integrated_decide(s,m,NoModel(),1)
            self.assertEqual(s.records['calls'],[])

    def test_non_authorized_journal_never_silently_dropped(self):
        with fixture() as (_,s,m):
            s.append('training','REGISTERED_REJECTED_ATTEMPT',dict(authorization_status='REJECTED'))
            s.save(state=1,next_transaction_id=s.checkpoint['next_transaction_id'])
            with self.assertRaisesRegex(IntegrationInvariantError,'no active event chronology'):
                integrated_decide(s,m,NoModel(),1)
            self.assertEqual(s.records['calls'],[])

    def test_negative_receipt_reset_and_fresh_requalification(self):
        with fixture(target_cost=-1) as (_,s,m):
            choice=integrated_decide(s,m,NoModel(),1);row=execute_choice(s,m,choice)
            self.assertEqual(row['realized']['consequence'],-1)
            self.assertEqual(row['grounded_after']['observation_count'],1)
            self.assertFalse(recommendation(incumbent.context(s,m,2),authenticated_projection(s,m))['eligible'])
            for count in range(1,5):
                base.execute(s,m,'UNIT','E',0,'HOLD','REGISTERED_SETUP',setup=True)
                got=recommendation(incumbent.context(s,m,2),authenticated_projection(s,m))
                self.assertEqual(got['eligible'],count==4)
            self.assertEqual(got['target_action'],'RETREAT')
            self.assertEqual(s.records['events'][4]['record']['receipt']['realized_consequence'],-1)

    def test_state_changing_acquisition_uses_same_protected_worker(self):
        with fixture(target_cost=0,target_state=2) as (_,s,m):
            row=execute_choice(s,m,integrated_decide(s,m,NoModel(),1))
            self.assertEqual((row['realized']['next_state'],s.checkpoint['current_state']),(2,2))
            self.assertEqual(len(s.records['events']),5)
            self.assertFalse(recommendation(incumbent.context(s,m,2),authenticated_projection(s,m))['eligible'])

    def test_I6_fresh_process_reconstructs_eligibility(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            with fixture() as (src,s,m):
                expected=recommendation(incumbent.context(s,m,1),authenticated_projection(s,m))
                # Copy a closed fixture snapshot solely for a unit-test restart, not matched scientific arms.
                m.checkpoint()
                import shutil
                shutil.copytree(src/'session',root/'session')
                shutil.copy2(src/'memory.sqlite3',root/'memory.sqlite3')
            code='''import json,sys
from pathlib import Path
from horus.live import SessionStore
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory
from grounded_agent.empirical_policy import integrated_decide
from grounded_agent.empirical_adapter import authenticated_projection,recommendation
from experiments.grounded_stagnation_escape_promotion_controlled_v0 import worker
p=Path(sys.argv[1])
with SessionStore(p/'session',True) as s,ModernMemory(p/'memory.sqlite3',False) as m:
 x=recommendation(worker.context(s,m,1),authenticated_projection(s,m))
 choice=integrated_decide(s,m,object(),1)
 print(json.dumps(dict(candidate=x,action=choice[0],source=choice[1],call_id=choice[3]['call_id'])))
'''
            actual=json.loads(subprocess.check_output([sys.executable,'-c',code,str(root)],text=True))
            self.assertEqual(actual['candidate'],expected)
            self.assertEqual((actual['action'],actual['source'],actual['call_id']),('ADVANCE',E.SOURCE,None))

    def test_original_policy_file_is_byte_identical_rollback(self):
        p=Path(__file__).with_name('policy.py')
        self.assertEqual(sha256(p.read_bytes()).hexdigest(),'b54caf86137121c1d1b1a914b86ac41e97a940d6d15c15a87aecb44236d9fd02')


class FrozenBoundaryTests(TestCase):
    def test_exact_inclusive_signs_and_stable_variable_scope(self):
        for seq in ([0]*4,[-1]*4,[1,-1,1,-1],[-1,-1,1,1],[1,1,0,0,0,-1],[-1,-1,0,1,0,0]):
            h,a=synthetic(seq);r=E.evaluate(1,E.ACTIONS,a,h)
            self.assertEqual(r['eligible'],sum(seq)<=0 and sum(seq[-4:])<=0)
        self.assertEqual(E.WINDOW,4)

    def test_observed_empirical_alternatives_excluded(self):
        h,a=synthetic([-1]*4)
        for action in ('ADVANCE','RETREAT'):
            a[action].update(relation_type='EMPIRICAL',kind='VARIABLE_RELATION',observation_count=2)
        self.assertFalse(E.evaluate(1,E.ACTIONS,a,h)['eligible'])

    def test_all_replication_case_boundaries_read_only(self):
        # Replay already-published semantic projections, never generate a new campaign.
        root=Path(__file__).resolve().parents[1]/'research/empirical-evidence-acquisition-replication-v0'
        cases=json.loads((root/'case-definitions.json').read_text())['cases']
        results=json.loads((root/'public-results.json').read_text())['cases']
        from grounded_state import empirical,deterministic
        for name,spec in cases.items():
            if spec['fault']:continue  # actual auth faults are tested above and in frozen candidate tests
            rows=[];history=[]
            for i,x in enumerate(spec['setup']+spec['prefix']+spec['interrupt'],1):
                history.append(dict(event_stream_sequence=i,authorization_status='AUTHORIZED',event_identity=str(i),receipt_identity=[str(i)],receipt_sha256=f'{i:064x}',state=x['pre_state'],action=x['action'],next_state=x['next_state'],consequence=x['consequence']))
                rows.append(dict(relation=f"{x['pre_state']}:{x['action']}",realized_next_state=x['next_state'],realized_consequence=x['consequence'],authorization_status='AUTHORIZED',event_identity=str(i),receipt_provenance_sha256=f'{i:064x}',event_stream_sequence=i))
            aa={};state=spec['boundary_state']
            for action in E.ACTIONS:
                key=f'{state}:{action}';emp=key in spec['empirical_relations'];selected=[r for r in rows if r['relation']==key]
                folded=(empirical if emp else deterministic).fold(selected)
                aa[action]=dict(relation=key,relation_type='EMPIRICAL' if emp else 'DETERMINISTIC',**folded)
                aa[action]['observation_count']=len(selected)
            result=E.evaluate(state,spec['candidate_input_order'],aa,history)
            self.assertEqual(result,results[name]['candidate']['output'],name)

if __name__=='__main__':unittest.main()
