"""Typed exact-relation state over the existing authenticated durable Memory boundary."""
from dataclasses import dataclass
from enum import Enum
from typing import Any
import json
from . import deterministic, empirical

class RelationType(str,Enum):
    DETERMINISTIC='DETERMINISTIC'
    EMPIRICAL='EMPIRICAL'

@dataclass(frozen=True)
class RelationKey:
    pre_state:int
    action:str
    def __post_init__(self):
        if type(self.pre_state) is not int or not self.action or type(self.action) is not str:
            raise ValueError('exact relation requires integer pre_state and nonempty action')
    @property
    def storage_key(self)->str:return f'{self.pre_state}:{self.action}'

@dataclass(frozen=True)
class ReceiptProvenance:
    identity:str
    receipt_sha256:str
    event_stream_sequence:int
    next_state:int
    consequence:int
    @property
    def value(self)->dict:return dict(next_state=self.next_state,consequence=self.consequence)

@dataclass(frozen=True)
class DerivedRelationState:
    relation:RelationKey
    relation_type:RelationType
    kind:str
    _evidence_json:str
    provenance:tuple[ReceiptProvenance,...]
    @property
    def evidence(self)->dict:return json.loads(self._evidence_json)

@dataclass(frozen=True)
class RelationAssessment:
    relation:RelationKey
    relation_type:RelationType
    status:str
    kind:str
    _evidence_json:str
    provenance:tuple[ReceiptProvenance,...]
    model_generalization:Any=None
    model_has_authority:bool=False
    @property
    def evidence(self)->dict:return json.loads(self._evidence_json)

class AuthenticatedMemory:
    """Adapter to the frozen SessionStore + ModernMemory admission/reconcile path.

    A caller must first append the protected original receipt event to SessionStore.
    `append` then invokes ModernMemory.record, which validates current signed event
    provenance. Derivation always reconciles the durable stores before reading.
    """
    def __init__(self,store,memory):self.store=store;self.memory=memory
    def append(self,event_envelope:dict,context_identifier:str)->dict:
        admission=self.memory.record(self.store,event_envelope,context_identifier)
        self.memory.reconcile(self.store)
        return admission
    def rows(self,relation:RelationKey)->list[dict]:
        if not isinstance(relation,RelationKey):raise TypeError('RelationKey required')
        self.memory.reconcile(self.store)
        return self.memory.rows(relation.storage_key)

def derive_relation_state(memory:AuthenticatedMemory,relation_key:RelationKey,
                          relation_type:RelationType)->DerivedRelationState:
    if not isinstance(memory,AuthenticatedMemory):raise TypeError('AuthenticatedMemory required')
    if not isinstance(relation_key,RelationKey):raise TypeError('RelationKey required')
    if not isinstance(relation_type,RelationType):raise ValueError('explicit RelationType required')
    rows=memory.rows(relation_key)
    state=(deterministic.fold(rows) if relation_type is RelationType.DETERMINISTIC
           else empirical.fold(rows))
    provenance=tuple(ReceiptProvenance(p['identity'],p['receipt_sha256'],
        p['event_stream_sequence'],p['value']['next_state'],p['value']['consequence']) for p in state['receipt_provenance'])
    if len(provenance)!=len(rows):raise RuntimeError('state omitted receipt provenance')
    return DerivedRelationState(relation_key,relation_type,state['kind'],
        json.dumps(state,sort_keys=True,separators=(',',':')),provenance)

def assess_relation(relation_key:RelationKey,state:DerivedRelationState,
                    optional_model_generalization:Any=None)->RelationAssessment:
    if relation_key!=state.relation:raise ValueError('assessment relation mismatch')
    if state.kind=='UNSEEN':status='UNSEEN'
    elif state.kind in ('UNRESOLVED_CHANGE','POSSIBLE_REGIME_CHANGE'):status='UNRESOLVED'
    else:status='GROUNDED'
    return RelationAssessment(relation_key,state.relation_type,status,state.kind,state._evidence_json,
        state.provenance,optional_model_generalization if status=='UNSEEN' else None,False)

@dataclass(frozen=True)
class DeterministicDecisionSemantics:
    acceptable_min:int
    consequence_ceiling:int

def deterministic_action_labels(state:DerivedRelationState,
                                semantics:DeterministicDecisionSemantics)->dict:
    """Application-supplied consequence ordering; never applies to empirical state."""
    if state.relation_type is not RelationType.DETERMINISTIC:
        raise TypeError('safe-fallback labels require explicitly deterministic relation')
    if state.kind!='ESTABLISHED':
        return dict(action_justified=False,optimality_established=False)
    consequence=state.evidence['established_value']['consequence']
    return dict(action_justified=consequence>=semantics.acceptable_min,
                optimality_established=consequence==semantics.consequence_ceiling)
