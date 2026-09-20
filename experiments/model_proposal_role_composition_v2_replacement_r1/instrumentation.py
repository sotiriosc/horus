"""Read-only synchronous journaling around the unchanged v2 role/authority path."""
from contextlib import contextmanager
from dataclasses import asdict
import sys
from experiments.model_proposal_role_composition_v2 import runtime
from experiments.state_recovery_proposal_interface_v1.framework import RecoveryOpportunity
from .durable import DurabilityFailure


class DurableTransport:
    def __init__(self,base,journal):self.base,self.journal=base,journal
    @property
    def requests(self):return self.base.requests
    def generate(self,call):
        cid=self.journal.intent(call)
        result=self.base.generate(call)
        if result.get('transport_error'):
            self.journal.append('TRANSPORT_FAILURE_AMBIGUOUS',result,cid)
            raise DurabilityFailure('transport failure with possible issuance; no retry')
        self.journal.response(cid,result)  # fsynced BEFORE Broker parses raw text
        return result


@contextmanager
def observe_boundaries(journal):
    """Compose the frozen observer; do not modify decisions or original events."""
    old=runtime.observe
    @contextmanager
    def observed():
        with old() as events:
            original=sys.getprofile()
            def callback(frame,event,value):
                original(frame,event,value)
                code=frame.f_code;loc=frame.f_locals;status=None;payload=None
                if event=='return' and code is runtime.RealizedEventFramework.begin_step.__code__:
                    if value is not None and hasattr(value,'prediction'):
                        status='PREDICTION_LATCHED';payload=dict(prediction=asdict(value.prediction),trusted_pending=asdict(value))
                    elif value is not None:status='PREEXECUTION_REJECTION';payload=dict(result=asdict(value))
                elif event=='return' and code is runtime.TestWorld.execute.__code__ and value is not None:
                    status='EXTERNAL_EVENT';payload=dict(actual=asdict(value))
                elif event=='return' and code is runtime.ExternalExecutionBoundary.execute.__code__ and value is not None:
                    status='AUTHENTIC_RECEIPT';payload=dict(receipt=asdict(value))
                elif event=='return' and code is runtime.MeasureAuditor.verify.__code__:
                    status='MEASURE_RESULT';payload=dict(verified=value,measurement=asdict(loc['measurement']))
                elif event=='call' and code is runtime.LiveRecovery.propose.__code__:
                    status='RECOVERY_OPPORTUNITY';payload=dict(context=asdict(loc['context']))
                elif event=='return' and code is RecoveryOpportunity.candidate.__code__ and value is not None:
                    status='RECOVERY_CANDIDATE_ENVELOPE';payload=dict(candidate=asdict(value),decision=asdict(loc['decision']))
                elif code is runtime.StatusBoundAuthorizer.authorize.__code__:
                    if event=='call':status='CANDIDATE_ENVELOPE'
                    elif event=='return':status='AUTHORIZER_DECISION'
                    if status:payload=dict(candidate=asdict(loc['candidate']),decision=asdict(loc['decision']),state_recovery=loc['state_recovery'],accepted=value if event=='return' else None)
                elif event=='return' and code is runtime.RealizedEventFramework.submit_package.__code__ and value is not None:
                    status='COMMIT_OR_REJECTION';payload=dict(result=asdict(value),continuation=value.continued,protected_state=runtime.published(loc['self']))
                if status:journal.append(status,payload)
            sys.setprofile(callback)
            try:yield events
            finally:sys.setprofile(original)
    runtime.observe=observed
    try:yield
    finally:runtime.observe=old
