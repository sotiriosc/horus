"""Read-only reconstruction from complete preserved R1 evidence."""
import json
from pathlib import Path
from types import SimpleNamespace
from experiments.composition_input_bindings_v1.adapters import map_payload, serialize
from experiments.model_proposal_role_composition_v2.protocol import MODEL, SYSTEMS, OPTIONS, schedule, seed
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import file_digest, digest, encoded, inspect

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).parent
PARENT = 'bffc9c5aa2408770038ecaf7fb076757e991cd01'
CAMPAIGN = 'HORUS_COMPOSITION_MAP_MEMORY_ABLATION_V0'


def lines(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def source_hashes(source):
    return {str(p.relative_to(source)): file_digest(p) for p in sorted(source.rglob('*')) if p.is_file()}


def frozen():
    registration = json.loads((PACKAGE/'frozen-inputs.json').read_text())
    for name, sha in registration['source_sha256'].items():
        assert file_digest(ROOT/name) == sha, name
    return registration


def reconstruct(source):
    audit = inspect(source)
    assert audit['journal_valid'] and not audit['ambiguous_calls'] and audit['campaign_state_matches_journal']
    calls = lines(source/'model-calls.jsonl')
    steps = {(s['episode'], s['decision']): s for s in lines(source/'steps.jsonl')}
    journal = lines(source/'journal.jsonl')
    intents = {r['call_id']: r['payload'] for r in journal if r['status']=='REQUEST_INTENT_RECORDED'}
    receipts = {(r['episode'],r['decision']): r['payload']['receipt'] for r in journal if r['status']=='AUTHENTIC_RECEIPT'}
    finalized = {(r['episode'],r['decision']):r['payload']['row'] for r in journal if r['status']=='TRANSACTION_FINALIZED'}
    descriptors = {d['episode']:d for d in schedule()}
    contexts = []
    # Selection uses only role and actual nonempty same-pair input; never prediction correctness.
    for call in calls:
        if call['role'] != 'Map' or not call['input']['VERIFIED_CHRONOLOGICAL_HISTORY']:
            continue
        ep, decision = call['episode'],call['decision']
        descriptor = descriptors[ep]; mapping = descriptor['mapping']
        assert mapping == call['mapping']
        original_id = f'HORUS_COMPOSITION_V2_REPLACEMENT_R1:e{ep:02d}:d{decision:02d}:Map'
        intent = intents[original_id]
        snapshot = source/intent['memory']['snapshot_reference']
        assert file_digest(snapshot)==intent['memory']['sha256']
        memory = json.loads(snapshot.read_text()); step = steps[(ep,decision)]
        assert memory == call['memory'] == step['probe']['before']['memory']
        assert finalized[(ep,decision)] == step
        assert all(r['authorization']=='AUTHORIZED' for r in memory)
        # Every prior observation is linked to an earlier authenticated committed receipt in this episode.
        for record in memory:
            prior = [s for (e,d),s in steps.items() if e==ep and d<decision and s['probe']['authorization']['committed'] and s['probe']['receipt']['transaction_id']==record['transaction_id']]
            assert len(prior)==1
            p=prior[0]['probe']; r=p['receipt']
            assert p['receipt_unchanged'] and any(v['receipt']==r and v['full_binding_verified'] and v['exact_authentic_object'] for v in p['provenance'])
            assert all(record[k]==r[k] for k in ('transaction_id','epoch','pre_state','action','next_state'))
            assert record['consequence']==r['realized_consequence']
            assert record in p['after']['memory']
        action = mapping[call['input']['target_action']]
        assert calls[step['call_indices'][0]]['parsed']['action']==action
        h = map_payload(call['current_state'], action, [SimpleNamespace(**r) for r in memory], mapping)
        assert h==call['input'] and serialize(h)==call['exact_prompt']==intent['exact_user']
        assert call['system']==SYSTEMS['Map']==intent['exact_system']
        options = {**OPTIONS['Map'], 'seed':seed(descriptor,decision,'Map')}
        assert options==call['options']==intent['options']
        body = dict(model=MODEL,system=SYSTEMS['Map'],prompt=serialize(h),stream=False,options=options)
        assert json.dumps(body)==intent['exact_request_json']
        w = {**h, 'VERIFIED_CHRONOLOGICAL_HISTORY':[]}
        assert {k for k in h if h[k]!=w[k]}=={'VERIFIED_CHRONOLOGICAL_HISTORY'}
        receipt = step['probe']['receipt']
        assert receipt==receipts[(ep,decision)] and step['probe']['receipt_unchanged']
        assert receipt['action']==action and receipt['pre_state']==call['current_state']
        assert any(v['receipt']==receipt and v['full_binding_verified'] and v['exact_authentic_object'] for v in step['probe']['provenance'])
        requests = {'H':body, 'W':{**body,'prompt':serialize(w)}}
        index = len(contexts)
        contexts.append(dict(index=index,source_call_index=call['index'],source_call_id=original_id,
            episode=ep,decision=decision,family=call['family'],mapping=mapping,state=call['current_state'],
            action=action,alias=h['target_action'],seed=options['seed'],depth=len(h['VERIFIED_CHRONOLOGICAL_HISTORY']),
            memory_snapshot= intent['memory'],memory=memory,history=h['VERIFIED_CHRONOLOGICAL_HISTORY'],
            receipt=receipt,receipt_sha256=digest(encoded(receipt).encode()),requests=requests,
            exact_requests={k:json.dumps(v) for k,v in requests.items()},
            request_sha256={k:digest(json.dumps(v).encode()) for k,v in requests.items()},
            order=['H','W'] if index%2==0 else ['W','H']))
    assert len(contexts)==42 and len({c['source_call_id'] for c in contexts})==42
    assert [(c['episode'],c['decision']) for c in contexts]==sorted((c['episode'],c['decision']) for c in contexts)
    return contexts


def public_contexts(contexts):
    keys=('index','source_call_index','source_call_id','episode','decision','family','mapping','state','action','alias','seed','depth','memory_snapshot','receipt_sha256','request_sha256','order')
    return [{k:c[k] for k in keys} for c in contexts]
