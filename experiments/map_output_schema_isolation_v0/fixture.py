"""Authentic histories and ordinary execution; model probes never enter framework."""
from copy import deepcopy
from dataclasses import asdict
from unittest.mock import patch
from experiments.cross_episode_initialization_boundary_v1.boundary import EpisodeController,EpisodePlan
from experiments.cross_episode_stale_memory_feasibility_v0.campaign import execute,audit,snap,plain
from experiments.cross_episode_initialization_boundary_v1.campaign import boundary_observer
from experiments.map_guided_explorer_interface_v0.interface import AuthenticatedReader
from experiments.realized_event_grounding_v0.framework import evidence
from experiments.base_framework_v0.framework import MapModel
from .protocol import CAMPAIGN,CONTROL,body

GUARD='experiments.base_framework_v1.hidden_oracle.TrueWorldOracle.execute'


class Context:
    def __init__(self,d):
        self.d=d;self.c=EpisodeController(f'{CAMPAIGN}:c{d["index"]:02d}',EpisodePlan(initial_state=1))
        self.authentic={};self.executions={};self.initial=snap(self.c)
        assert self.initial['world_state']==1 and self.initial['epoch']==1001 and not self.initial['protected']['memory']
        self.setup=[execute(self.c,'HOLD',self.authentic,self.executions)]
        self.reader=AuthenticatedReader(self.c,self.authentic,self.executions)
        self.capture=self.reader.capture(d['mapping']);self.payload=self.capture['map_inputs']['HOLD'];self.request=body(d,self.payload)
        self.before=snap(self.c);self.audit_before()

    def audit_before(self):
        c=self.c;d=self.d;s=snap(c)
        assert s==self.before and s['world_state']==s['protected']['map']['state']==1 and s['epoch']==1001
        assert s['world_executions']==s['source_event_count']==len(s['protected']['memory'])==1
        assert s['next_transaction_id']==2 and s['root_receipt'] is None and s['pending'] is None
        assert self.reader.capture(d['mapping'])==self.capture and type(c._active.framework.inner.map) is MapModel
        history=self.payload['VERIFIED_CHRONOLOGICAL_HISTORY']
        assert len(history)==1 and [(r['epoch'],r['transaction_id'],r['next_state'],r['consequence']) for r in history]==[(1001,1,1,1)]
        assert len(self.authentic)==1
        return audit(c,self.authentic,self.executions)

    def record(self):
        return plain(dict(descriptor=self.d,initial=self.initial,setup=self.setup,before=self.before,capture=self.capture,request=self.request,provenance=self.audit_before()))

    def grounded_step(self,journal=None,call_id=None):
        """No raw or parsed probe argument; no model adapter, inference or condition branch."""
        self.audit_before();c=self.c
        def log(status,value):
            if journal is not None:journal.append(status,plain(value),call_id)
        with patch(GUARD,side_effect=AssertionError('future event must not execute before control latch')):
            pending=c.begin_step('HOLD')
        prediction=asdict(pending.prediction);latched=snap(c)
        assert prediction==latched['prediction_at_begin']
        assert {k:prediction[k] for k in CONTROL}==CONTROL
        assert latched['world_executions']==1 and latched['root_receipt'] is None and latched['protected']==self.before['protected']
        log('CONTROL_PREDICTION_LATCHED',dict(prediction=prediction,non_model=True,snapshot=latched))
        log('EXECUTION_INTENT_RECORDED',dict(epoch=pending.epoch,transaction_id=pending.transaction_id,action=pending.action))
        receipt=c.execute_pending();original=asdict(receipt);actual=asdict(c._active.world.last_actual)
        assert c._source.reader().current() is receipt and receipt.identity() not in self.authentic
        assert receipt.transaction_id==receipt.event_id==2
        assert receipt.binding()[:6]==tuple(actual[k] for k in ('epoch','transaction_id','pre_state','action','next_state','consequence'))
        self.authentic[receipt.identity()]=receipt;self.executions[receipt.identity()]=actual
        log('AUTHENTIC_EXECUTION_RECEIPT',dict(actual=actual,receipt=original,original_receipt_object=True))
        with boundary_observer() as effects:result=c.submit_package(evidence(receipt))
        assert result.committed and result.continued and effects['measure']==1 and effects['package_admission']==1
        f=c._active.framework;assert f.packages[-1].receipt is receipt and type(f.inner.map) is MapModel
        assert asdict(receipt)==original and snap(c)['prediction_at_begin']==prediction
        control_match=(CONTROL['next_state'],CONTROL['consequence'])==(receipt.next_state,receipt.realized_consequence)
        assert f.inner.memory.records[-1].measurement_matches==control_match
        proof=audit(c,self.authentic,self.executions)
        assert snap(c)['protected']['memory'][:-1]==self.before['protected']['memory']
        log('MEASURE_AUTHORIZATION_PUBLICATION',dict(authorization=asdict(result),effects=effects,control_measurement_matches=control_match,provenance=proof))
        c.release(receipt);after=snap(c)
        assert after['world_executions']==after['source_event_count']==2 and after['root_receipt'] is None
        return plain(dict(control_prediction=prediction,latch=latched,actual=actual,receipt=original,authorization=asdict(result),effects=effects,
            provenance=proof,control_measurement_matches=control_match,before=self.before,after=after))

    def finish(self,call,journal=None):
        # Parse values are retained outside the ordinary execution method and never supplied to it.
        parsed=deepcopy(call['parsed']);grounded=self.grounded_step(journal,call['call_id']);receipt=grounded['receipt']
        valid=parsed is not None
        score=dict(consequence=parsed['consequence']==receipt['realized_consequence'] if valid else None,next_state=None,exact=None)
        if valid and self.d['condition']=='J':
            score['next_state']=parsed['next_state']==receipt['next_state'];score['exact']=score['next_state'] and score['consequence']
        assert parsed==call['parsed']
        return dict(descriptor=self.d,valid=valid,parsed=parsed,score=score,authentic_post_response_score=True,authentic_history=True,
            probe_detached=True,probe_publication=False,**grounded)
