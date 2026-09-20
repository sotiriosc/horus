"""Driver fixture through existing grounded execution and Map adapter paths."""
from copy import deepcopy
from dataclasses import asdict
from unittest.mock import patch
from experiments.cross_episode_initialization_boundary_v1.boundary import EpisodeController,EpisodePlan
from experiments.cross_episode_stale_memory_feasibility_v0.campaign import execute,audit,snap,plain
from experiments.cross_episode_initialization_boundary_v1.campaign import boundary_observer
from experiments.map_guided_explorer_interface_v0.interface import AuthenticatedReader
from experiments.model_map_proposal_v0.adapter import MapProposalAdapter
from experiments.realized_event_grounding_v0.framework import evidence
from .protocol import CAMPAIGN,body

GUARD='experiments.base_framework_v1.hidden_oracle.TrueWorldOracle.execute'


class ConditionController(EpisodeController):
    """Trusted external fixture: alter only state-1 HOLD next_state in M."""
    def __init__(self,source_identity,condition):
        assert condition in ('S','M');self.condition=condition
        super().__init__(source_identity,EpisodePlan(initial_state=1))
    def _make_world(self,initial_state):
        world=super()._make_world(initial_state)
        if self.condition=='M':
            values=list(world.fixture.oracle._NEXT);values[4]=2
            world.fixture.oracle._NEXT=tuple(values)
        return world


class Context:
    def __init__(self,d):
        self.d=d;self.c=ConditionController(f'{CAMPAIGN}:c{d["index"]:02d}',d['condition'])
        self.authentic={};self.executions={};self.initial=snap(self.c)
        assert self.initial['world_state']==1 and self.initial['epoch']==1001 and not self.initial['protected']['memory']
        self.setup=[execute(self.c,a,self.authentic,self.executions) for a in d['setup_actions']]
        self.reader=AuthenticatedReader(self.c,self.authentic,self.executions)
        self.capture=self.reader.capture(d['mapping']);self.payload=self.capture['map_inputs']['HOLD'];self.request=body(d,self.payload)
        self.before=snap(self.c);self.audit_before()

    def audit_before(self):
        c=self.c;d=self.d;s=snap(c)
        assert s==self.before and s['world_state']==s['protected']['map']['state']==1 and s['epoch']==1001
        assert s['world_executions']==s['source_event_count']==len(s['protected']['memory'])==d['setup_count']
        assert s['next_transaction_id']==d['setup_count']+1 and s['root_receipt'] is None and s['pending'] is None
        assert self.reader.capture(d['mapping'])==self.capture
        history=self.payload['VERIFIED_CHRONOLOGICAL_HISTORY']
        assert len(history)==1 and [(r['epoch'],r['transaction_id']) for r in history]==[(1001,1)]
        assert history[0]['next_state']==(1 if d['condition']=='S' else 2) and history[0]['consequence']==1
        if d['condition']=='M':
            nav=s['protected']['memory'][1]
            assert (nav['pre_state'],nav['action'],nav['next_state'])==(2,'RETREAT',1)
            assert all(r['transaction_id']!=nav['transaction_id'] for r in history)
        assert len({id(x) for x in self.authentic.values()})==len(self.authentic)==d['setup_count']
        assert len({x.identity() for x in self.authentic.values()})==d['setup_count']
        return audit(c,self.authentic,self.executions)

    def record(self):
        return plain(dict(descriptor=self.d,initial=self.initial,setup=self.setup,before=self.before,capture=self.capture,request=self.request,provenance=self.audit_before()))

    def finish(self,call,journal=None):
        self.audit_before();parsed=call['parsed'];c=self.c
        def log(status,value):
            if journal is not None:journal.append(status,plain(value),call['call_id'])
        if parsed is None:
            log('INVALID_PROPOSAL_NOT_EXECUTED',dict(context_index=self.d['index'],protected_unchanged=True))
            return dict(descriptor=self.d,valid=False,parsed=None,score=dict(next_state=False,consequence=False,exact=False),
                authentic_post_prediction_score=False,reason='INVALID_MAP_NO_REPAIR_NO_EXECUTION',before=self.before,after=snap(c))
        invocations=[]
        def recorded_source(prompt,seed):
            assert prompt==self.request['prompt'] and seed==self.d['seed'];invocations.append(1);assert len(invocations)==1
            return call['response']['raw_output']
        core=c._active.framework.inner
        core.map=MapProposalAdapter(core.map,recorded_source,self.request['prompt'],self.d['seed'])
        with patch(GUARD,side_effect=AssertionError('future world must not execute before latch')):
            pending=c.begin_step('HOLD')
        assert len(invocations)==1 and hasattr(pending,'prediction')
        prediction=asdict(pending.prediction);latched=snap(c)
        assert prediction==latched['prediction_at_begin']
        assert (prediction['next_state'],prediction['consequence'])==(parsed['next_state'],parsed['consequence'])
        assert latched['world_executions']==self.d['setup_count'] and latched['root_receipt'] is None
        assert latched['protected']==self.before['protected']
        log('PREDICTION_LATCHED',dict(prediction=prediction,world_executions=latched['world_executions'],root_receipt=None,snapshot=latched))
        log('EXECUTION_INTENT_RECORDED',dict(epoch=pending.epoch,transaction_id=pending.transaction_id,action=pending.action))
        receipt=c.execute_pending();original=asdict(receipt);actual=asdict(c._active.world.last_actual)
        assert c._source.reader().current() is receipt and receipt.identity() not in self.authentic
        assert receipt.transaction_id==self.d['setup_count']+1 and receipt.event_id==self.d['setup_count']+1
        assert receipt.binding()[:6]==tuple(actual[k] for k in ('epoch','transaction_id','pre_state','action','next_state','consequence'))
        self.authentic[receipt.identity()]=receipt;self.executions[receipt.identity()]=actual
        log('AUTHENTIC_EXECUTION_RECEIPT',dict(actual=actual,receipt=original,original_receipt_object=True))
        with boundary_observer() as effects:result=c.submit_package(evidence(receipt))
        assert result.committed and result.continued
        assert effects['measure']>0 and effects['package_admission']==1
        f=c._active.framework;assert f.packages[-1].receipt is receipt
        assert asdict(receipt)==original and snap(c)['prediction_at_begin']==prediction
        score=dict(next_state=parsed['next_state']==receipt.next_state,consequence=parsed['consequence']==receipt.realized_consequence)
        score['exact']=all(score.values());assert f.inner.memory.records[-1].measurement_matches==score['exact']
        proof=audit(c,self.authentic,self.executions)
        assert snap(c)['protected']['memory'][:-1]==self.before['protected']['memory']
        log('MEASURE_AUTHORIZATION_PUBLICATION',dict(authorization=asdict(result),effects=effects,measurement_matches=score['exact'],provenance=proof))
        c.release(receipt);after=snap(c)
        assert after['world_executions']==after['source_event_count']==self.d['setup_count']+1 and after['root_receipt'] is None
        return plain(dict(descriptor=self.d,valid=True,parsed=parsed,score=score,prediction=prediction,latch=latched,
            actual=actual,receipt=original,authorization=asdict(result),effects=effects,provenance=proof,
            authentic_post_prediction_score=True,prediction_unchanged=True,historical_Memory_unchanged=True,
            before=self.before,after=after))
