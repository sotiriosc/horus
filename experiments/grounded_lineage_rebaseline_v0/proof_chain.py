"""Independently check one committed R1 event using retained JSON only."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(data): return hashlib.sha256(data).hexdigest()
def lines(path):return [json.loads(x) for x in path.read_text().splitlines()]
def verify(archive):
    journal=lines(archive/'journal.jsonl');previous='0'*64
    for i,row in enumerate(journal):
        value={k:v for k,v in row.items() if k!='record_sha256'}
        assert row['sequence']==i and row['previous_sha256']==previous
        assert sha((json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode())==row['record_sha256']
        previous=row['record_sha256']
    calls=lines(archive/'model-calls.jsonl');steps=lines(archive/'steps.jsonl')
    step=next(x for x in steps if (x['episode'],x['decision'])==(0,0));probe=step['probe']
    events=[r for r in journal if (r['episode'],r['decision'])==(0,0)]
    def event(status):
        chosen=[r for r in events if r['status']==status];assert len(chosen)==1;return chosen[0]
    ec,mc,rc=[calls[i] for i in step['call_indices']]
    assert [c['role'] for c in (ec,mc,rc)]==['Explorer','Map','Recovery']
    # Independent finite parsing, not the experiment's expected-answer helper.
    action=ec['mapping'][ec['raw_output'].strip()]
    prediction=json.loads(mc['raw_output']);replacement=json.loads(rc['raw_output'])
    assert set(prediction)=={'next_state','consequence'} and type(prediction['next_state']) is int and prediction['next_state'] in range(4)
    assert type(prediction['consequence']) is int and prediction['consequence'] in (-1,0,1)
    assert set(replacement)=={'replacement_state'} and type(replacement['replacement_state']) is int and replacement['replacement_state'] in range(4)
    latched=event('PREDICTION_LATCHED')['payload'];pending=latched['trusted_pending'];p=latched['prediction']
    assert pending['prediction']==p==probe['prediction']
    assert action==pending['action']==p['action']
    assert prediction=={k:p[k] for k in ('next_state','consequence')}
    actual=event('EXTERNAL_EVENT')['payload']['actual'];receipt=event('AUTHENTIC_RECEIPT')['payload']['receipt']
    assert actual==probe['actual'] and receipt==probe['receipt']
    identity=('epoch','transaction_id','pre_state','action')
    assert all(p[k]==pending[k if k!='pre_state' else 'proposal_pre_state']==actual[k]==receipt[k] for k in identity)
    assert (actual['next_state'],actual['consequence'])==(receipt['next_state'],receipt['realized_consequence'])
    publication=event('COMMIT_OR_REJECTION')['payload'];protected=publication['protected_state'];assert protected==probe['after']
    record=protected['memory'][-1];pair=protected['pairs'][-1];package=protected['packages'][-1]
    assert package['receipt']==receipt and package['prediction']==p
    assert package['package_id']==[receipt[k] for k in ('source_identity','event_id','epoch','transaction_id')]
    assert pair['pair_decision_id']==package['pair_decision_id']==record['pair_decision_id']
    for k in (*identity,'next_state','consequence'):
        rv=receipt['realized_consequence' if k=='consequence' else k]
        assert record[k]==pair[k]==actual[k]==rv
    for k in ('observation_a_id','observation_b_id'):assert record[k]==pair[k]
    assert record['source_pair']==[pair['source_a'],pair['source_b']]
    assert all(pair[k]=='SHARED_REALIZED_EVENT_ROOT' for k in ('domain_a','domain_b','lineage_a','lineage_b'))
    measure=event('MEASURE_RESULT')['payload'];m=measure['measurement']
    matches=all(p[k]==actual[k] for k in (*identity,'next_state','consequence'))
    assert m['matches']==pair['measurement_matches']==record['measurement_matches']==matches
    assert not matches and measure['verified'] and m['status']=='MEASURED'
    assert (m['epoch'],m['transaction_id'],m['observation_id'])==(record['epoch'],record['transaction_id'],record['pair_decision_id'])
    auth=event('AUTHORIZER_DECISION')['payload'];candidate=auth['candidate']
    assert auth['accepted'] and auth['state_recovery'] and candidate['status']=='RECOVERING'
    assert auth['decision']==pair and candidate['value']==replacement['replacement_state']==receipt['next_state']
    assert all(candidate[k]==record[k] for k in ('epoch','transaction_id','pair_decision_id'))
    assert record['authorization']=='AUTHORIZED' and publication['result']['committed'] and publication['continuation']
    assert probe['provenance'][0]['exact_authentic_object'] and probe['provenance'][0]['full_binding_verified']
    # Actual later Map request, not just an unused after-step projection.
    later=calls[12];assert later['episode']==0 and later['decision']==4 and later['role']=='Map'
    later_record=next(r for r in later['memory'] if (r['epoch'],r['transaction_id'])==(1001,1));assert later_record==record
    entry=next(z for z in later['input']['VERIFIED_CHRONOLOGICAL_HISTORY'] if z['transaction_id']==1)
    assert later['current_state']==record['pre_state'] and later['mapping'][entry['surface_action']]==record['action']
    assert {k:entry[k] for k in ('next_state','consequence','transaction_id')}=={k:record[k] for k in ('next_state','consequence','transaction_id')}
    intent=next(r for r in journal if r['status']=='REQUEST_INTENT_RECORDED' and r['payload'].get('episode')==0 and r['payload'].get('decision')==4 and r['payload'].get('role')=='Map')
    body=intent['payload'];assert json.loads(body['exact_user'])==later['input']==body['structured_projection']
    assert json.loads(body['exact_request_json'])==body['request'] and body['request']['prompt']==later['exact_prompt']
    ref=body['memory'];snapshot=archive/ref['snapshot_reference'];assert sha(snapshot.read_bytes())==ref['sha256']
    assert json.loads(snapshot.read_text())==later['memory']
    ordered=['PREDICTION_LATCHED','EXTERNAL_EVENT','AUTHENTIC_RECEIPT','MEASURE_RESULT','RECOVERY_OPPORTUNITY','RECOVERY_CANDIDATE_ENVELOPE','CANDIDATE_ENVELOPE','AUTHORIZER_DECISION','COMMIT_OR_REJECTION','TRANSACTION_FINALIZED']
    indices=[event(k)['sequence'] for k in ordered];assert indices==sorted(indices) and indices[-1]<intent['sequence']
    return dict(passed=True,model_calls=0,campaign='model_proposal_role_composition_v2_replacement_r1',episode=0,decision=0,
        retained_journal_records_verified=len(journal),journal_head_sha256=previous,
        archive_file_sha256={n:sha((archive/n).read_bytes()) for n in ('journal.jsonl','model-calls.jsonl','steps.jsonl')},
        selected_call_indices=step['call_indices'],parsed_action=action,parsed_map_prediction=prediction,parsed_recovery_value=replacement['replacement_state'],
        execution_call_arguments={k:pending[k] for k in ('epoch','transaction_id','action')},
        execution_call_evidence='Arguments reconstructed from retained trusted pending record and inspected boundary.execute call site; profiler records actual world and boundary returns. No separate historical entry-call argument capture exists.',
        original_prediction=p,actual=actual,receipt=receipt,package=package,pair=pair,measure=measure,authorizer=auth,memory_record=record,
        journal_sequence={k:event(k)['sequence'] for k in ordered},
        later_call=dict(index=12,episode=0,decision=4,role='Map',journal_intent_sequence=intent['sequence'],request_sha256=sha(body['exact_request_json'].encode()),memory_snapshot_sha256=ref['sha256'],visible_history_entry=entry),
        original_object_identity='Retained runtime identity check is true; JSON field/hash verification cannot recreate historical Python identity. Original issuer and recorder remain trusted.',
        original_raw_archives_unchanged=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();result=verify(a.archive);a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print('PASS full retained R1 chain: episode0 decision0 -> actual later Map call12; journal records',result['retained_journal_records_verified'])
if __name__=='__main__':main()
