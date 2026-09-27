import tempfile,unittest,json
from pathlib import Path
from horus.live import SessionStore
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory
from experiments.grounded_uncertainty_state_v0.worker import new_controller
from experiments.grounded_uncertainty_state_v0.harness import prepare_mechanical,publish
from . import (AuthenticatedMemory,RelationKey,RelationType,derive_relation_state,
    assess_relation,DeterministicDecisionSemantics,deterministic_action_labels,DerivedRelationState)
from . import deterministic,empirical


def rows(values):
    return [dict(realized_next_state=1,realized_consequence=v,
        authorization_status='AUTHORIZED',event_identity=f'event-{i}',
        receipt_provenance_sha256=f'hash-{i}',event_stream_sequence=i+1)
        for i,v in enumerate(values)]

class FrozenFoldTests(unittest.TestCase):
    def test_unseen_and_explicit_type(self):
        self.assertEqual(deterministic.fold([])['kind'],'UNSEEN')
        self.assertEqual(empirical.fold([])['kind'],'UNSEEN')
        with self.assertRaises(ValueError):derive_relation_state(AuthenticatedMemory(None,None),RelationKey(1,'HOLD'),None)
        with self.assertRaises(ValueError):RelationKey(1,'')

    def test_first_contradiction_confirmation_rejection_and_old_receipts(self):
        first=deterministic.fold(rows([1]))
        self.assertEqual(first['kind'],'ESTABLISHED')
        second=deterministic.fold(rows([1,-1]))
        self.assertEqual(second['kind'],'UNRESOLVED_CHANGE')
        self.assertEqual(second['candidate_count'],1)
        self.assertEqual(deterministic.fold(rows([1,-1,-1]))['established_value']['consequence'],-1)
        rejected=deterministic.fold(rows([1,-1,1]))
        self.assertEqual(rejected['kind'],'ESTABLISHED')
        self.assertEqual(len(rejected['receipt_provenance']),3)

    def test_empirical_variation_shift_and_restoration(self):
        from experiments.grounded_stochastic_relation_v0.protocol import BASE
        self.assertEqual(empirical.fold(rows([1]*7+[-1]+[1]*6))['kind'],'VARIABLE_RELATION')
        values=BASE+[-1]*5+[0,-1,-1]+[1]*5
        self.assertEqual(empirical.fold(rows(values[:12]))['kind'],'POSSIBLE_REGIME_CHANGE')
        self.assertEqual(empirical.fold(rows(values[:13]))['segment_start'],8)
        self.assertEqual(empirical.fold(rows(values[:20]))['kind'],'POSSIBLE_REGIME_CHANGE')
        self.assertEqual(empirical.fold(rows(values[:21]))['segment_start'],16)
        self.assertEqual(len(empirical.fold(rows(values))['receipt_provenance']),len(values))

    def test_unresolved_status_and_model_does_not_override(self):
        key=RelationKey(1,'HOLD')
        for kind,relation_type,evidence in (
            ('UNRESOLVED_CHANGE',RelationType.DETERMINISTIC,deterministic.fold(rows([1,-1]))),
            ('POSSIBLE_REGIME_CHANGE',RelationType.EMPIRICAL,empirical.fold(rows([1]*8+[-1]*4)))):
            state=DerivedRelationState(key,relation_type,kind,json.dumps(evidence),())
            assessment=assess_relation(key,state,{'consequence':999})
            self.assertEqual(assessment.status,'UNRESOLVED')
            self.assertIsNone(assessment.model_generalization)
            self.assertFalse(assessment.model_has_authority)
        with self.assertRaises(ValueError):assess_relation(RelationKey(2,'HOLD'),state)

    def test_deterministic_decision_scope(self):
        key=RelationKey(1,'HOLD');evidence=deterministic.fold(rows([0]))
        state=DerivedRelationState(key,RelationType.DETERMINISTIC,evidence['kind'],json.dumps(evidence),())
        self.assertEqual(deterministic_action_labels(state,DeterministicDecisionSemantics(0,1)),
                         dict(action_justified=True,optimality_established=False))
        unresolved=deterministic.fold(rows([0,-1]))
        state=DerivedRelationState(key,RelationType.DETERMINISTIC,unresolved['kind'],json.dumps(unresolved),())
        self.assertEqual(deterministic_action_labels(state,DeterministicDecisionSemantics(0,1)),
                         dict(action_justified=False,optimality_established=False))

    def test_unauthorized_folds_reject(self):
        bad=rows([1]);bad[0]['authorization_status']='REJECTED'
        for fold in (deterministic.fold,empirical.fold):
            with self.assertRaises(RuntimeError):fold(bad)

class DurableCoreTests(unittest.TestCase):
    def test_protected_receipt_restart_model_isolation_and_failed_admission(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with SessionStore(root/'session',False) as store,ModernMemory(root/'memory.sqlite3',True) as memory:
                ctx=dict(arm='U',store=store,memory=memory)
                controller=new_controller(store,'A')
                batch=prepare_mechanical(ctx,controller,'U','HOLD')
                spec=dict(action='HOLD',event=1,schedule='CORE_TEST',observation_id='CORE_TEST:1',
                          phase='stationary',isolated_noise=False)
                publish(ctx,controller,batch,spec)
                adapter=AuthenticatedMemory(store,memory)
                key=RelationKey(1,'HOLD')
                state=derive_relation_state(adapter,key,RelationType.DETERMINISTIC)
                self.assertEqual(state.kind,'ESTABLISHED')
                self.assertEqual(len(state.provenance),1)
                self.assertEqual(assess_relation(key,state,{'consequence':999}).status,'GROUNDED')
                self.assertIsNone(assess_relation(key,state,{'consequence':999}).model_generalization)
                state.evidence['kind']='TAMPERED'
                state.provenance[0].value['consequence']=999
                self.assertEqual(state.kind,'ESTABLISHED')
                self.assertEqual(state.evidence['kind'],'ESTABLISHED')
                self.assertEqual(state.provenance[0].value['consequence'],1)
                self.assertEqual(derive_relation_state(adapter,key,RelationType.DETERMINISTIC),state)
                with self.assertRaises(RuntimeError):adapter.append(dict(record=dict(authorization_status='AUTHORIZED')),'forged')
                self.assertEqual(derive_relation_state(adapter,key,RelationType.DETERMINISTIC),state)
                self.assertEqual(derive_relation_state(adapter,RelationKey(1,'RETREAT'),RelationType.DETERMINISTIC).kind,'UNSEEN')
                unseen=derive_relation_state(adapter,RelationKey(1,'RETREAT'),RelationType.DETERMINISTIC)
                offer=assess_relation(unseen.relation,unseen,{'consequence':0})
                self.assertEqual(offer.status,'UNSEEN')
                self.assertEqual(offer.model_generalization,{'consequence':0})
                self.assertFalse(offer.model_has_authority)
                labels=deterministic_action_labels(state,DeterministicDecisionSemantics(0,1))
                self.assertEqual(labels,dict(action_justified=True,optimality_established=True))
                empirical_state=derive_relation_state(adapter,key,RelationType.EMPIRICAL)
                self.assertEqual(empirical_state.kind,'EMPIRICALLY_STABLE')
                with self.assertRaises(TypeError):deterministic_action_labels(empirical_state,DeterministicDecisionSemantics(0,1))
            with SessionStore(root/'session',True) as store,ModernMemory(root/'memory.sqlite3',False) as memory:
                restored=derive_relation_state(AuthenticatedMemory(store,memory),key,RelationType.DETERMINISTIC)
                self.assertEqual(restored,state)

if __name__=='__main__':unittest.main()
