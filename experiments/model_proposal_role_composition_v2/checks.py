"""Pre-live absence-marker check; bounded capability controls run only post-live."""
import json
from experiments.composition_input_bindings_v1.campaign import setup as fixture_setup, ordinary
from experiments.realized_event_grounding_v0.campaign import published
from experiments.model_map_proposal_v0.adapter import INVALID as MAP_INVALID
from experiments.model_recovery_proposal_v1.adapter import INVALID as RECOVERY_INVALID
from .protocol import schedule
from .runtime import views, Broker, setup, step


def unknown_preflight():
    bundle=fixture_setup(0,'UNKNOWN_PREFLIGHT');snapshots=[]
    for index,action in enumerate((None,'HOLD','ADVANCE','RETREAT','RETREAT','ADVANCE')):
        if action:ordinary(bundle,action)
        snapshot=published(bundle[0]);projections=[]
        for d in schedule():
            for state in range(4):
                projection=views(state,snapshot,d['mapping'])
                if state==0:
                    known={d['mapping'][x['action']] for x in projection['Explorer']['actions'] if x['verified_outcomes']!='UNTRIED'}
                    assert known==set(() if index==0 else ('HOLD',) if index==1 else ('HOLD','ADVANCE') if index<4 else ('HOLD','ADVANCE','RETREAT'))
                projections.append(dict(family=d['family'],mapping_index=d['mapping_index'],state=state,views=projection))
        if snapshots:
            old=snapshots[-1]['snapshot']['memory'];assert snapshot['memory'][:len(old)]==old
        snapshots.append(dict(index=index,snapshot=snapshot,projections=projections))
    return dict(status='PASS',actual_model_calls=0,projection_contexts=288,
                all_seven_unknown_requirements=True,snapshots=snapshots)


class Synthetic:
    def __init__(self,invalid_role=None,invalid=None):self.invalid_role,self.invalid=invalid_role,invalid
    def generate(self,call):
        raw={'Explorer':'K1','Map':'{"next_state":0,"consequence":0}',
             'Recovery':'{"replacement_state":1}'}[call['role']]
        if call['role']==self.invalid_role:raw=self.invalid
        return dict(raw_output=raw,transport_error=None,response_metadata={'synthetic':True})


def controls():
    invalid_e=['{"next_state":1,"consequence":1}','K1 K2','{"action":"K1","authorization":true}','ADVANCE','K1 retry']
    invalid_m=list(MAP_INVALID)+['K1','{"next_state":1,"consequence":1,"action":"HOLD"}',
        '{"next_state":1,"consequence":1,"receipt_id":"fake"}',
        '{"next_state":1,"consequence":1,"epoch":1001}',
        '{"next_state":1,"consequence":1,"next_state":1}']
    invalid_r=list(RECOVERY_INVALID)+['{"replacement_state":1,"retry":true}',
        '{"replacement_state":1,"next_state":1,"consequence":1}']
    rows=[]
    for role,raws in (('Explorer',invalid_e),('Map',invalid_m),('Recovery',invalid_r)):
        for index,raw in enumerate(raws):
            broker=Broker(Synthetic(role,raw));row=step(setup(f'CONTROL_{role}_{index}'),broker,schedule()[0],0)
            assert not row['probe']['authorization']['committed']
            assert row['probe']['authorization']['executed']==(role=='Recovery')
            assert [c['role'] for c in broker.calls]==(['Explorer'] if role=='Explorer' else ['Explorer','Map'] if role=='Map' else ['Explorer','Map','Recovery'])
            rows.append(dict(role=role,index=index,calls=broker.calls,step=row))
    return dict(actual_model_calls=0,status='PASS',counts=dict(Explorer=5,Map=14,Recovery=22),rows=rows)
