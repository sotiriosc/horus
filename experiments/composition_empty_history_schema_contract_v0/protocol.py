"""Frozen contexts, strict descriptive counts and prospectively fixed decision."""
from collections import Counter
import hashlib
import json
from pathlib import Path
from experiments.model_map_proposal_v0.adapter import MODEL, OPTIONS, SYSTEM, parse
from experiments.composition_initial_map_schema_diagnosis_v0.diagnose import reconstruct_live, shape

ROOT = Path(__file__).resolve().parents[2]
PARSER_PATH = 'experiments/model_map_proposal_v0/adapter.py'
PARSER_SHA = '0195cc2b5fdb657dcb53f6991ed5494f6ffeb2f279cdb4ae0d4f6b9589dc0494'
SYSTEMS = dict(A=SYSTEM, B='Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly two fields: next_state must be an integer in {0,1,2,3}, and consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.')
EPISODES = [0,2,4,5,7,8,9,10,11]
MANIFEST = '4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a'
WEIGHTS = 'bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3'


def encoded(v): return json.dumps(v, sort_keys=True, indent=2)+'\n'
def line(v): return json.dumps(v, sort_keys=True, separators=(',',':'))+'\n'
def sha(b): return hashlib.sha256(b).hexdigest()
def read(p): return json.loads(p.read_text())
def lines(p): return [json.loads(s) for s in p.read_text().splitlines()]


def register(composition):
    contexts, _, unknown = reconstruct_live(composition)
    assert [c['episode'] for c in contexts] == EPISODES
    assert sha((ROOT/PARSER_PATH).read_bytes()) == PARSER_SHA
    assert Counter(c['family'] for c in contexts) == dict(O1=4,O2=5)
    plan=[]
    for i,c in enumerate(contexts):
        assert c['history_depth']==0 and c['payload']['VERIFIED_CHRONOLOGICAL_HISTORY']==[]
        for condition in ('AB' if i%2==0 else 'BA'):
            body={**c['request_body'],'system':SYSTEMS[condition]}
            assert body['options']=={**OPTIONS,'seed':c['seed']} and body['model']==MODEL
            plan.append(dict(index=len(plan),context=i,condition=condition,
                **{k:c[k] for k in ('episode','family','mapping_index','mapping','action','target','state','seed')},
                historical_raw=c['classification']['raw_response'],request=body,request_json=json.dumps(body),
                user_payload_sha256=sha(body['prompt'].encode())))
    sources=[*ROOT.glob('experiments/**/*.py'),ROOT/'research/composition-empty-history-schema-contract-v0-preregistration.md']
    return dict(parent='28b87365e1f768ef7bf176997126fbffe250e059',
        preserved_composition='C — NOT ESTABLISHED',systems=SYSTEMS,plan=plan,
        parser_sha256=PARSER_SHA,source_sha256={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted(sources)},
        input_sha256={p.name:sha(p.read_bytes()) for p in sorted(composition.iterdir()) if p.is_file()},
        unknown_storage_audit=unknown,model_manifest=MANIFEST,model_weights=WEIGHTS)


def validate_registration(reg):
    assert reg['systems']==SYSTEMS and reg['parser_sha256']==PARSER_SHA
    for path,digest in reg['source_sha256'].items(): assert sha((ROOT/path).read_bytes())==digest,path
    assert len(reg['plan'])==18
    for i in range(9):
        pair=reg['plan'][2*i:2*i+2]
        assert [r['condition'] for r in pair]==list('AB' if i%2==0 else 'BA')
        a,b=sorted(pair,key=lambda r:r['condition'])
        assert a['context']==b['context']==i and a['episode']==b['episode']==EPISODES[i]
        assert {k:v for k,v in a.items() if k not in ('index','condition','request','request_json')}=={k:v for k,v in b.items() if k not in ('index','condition','request','request_json')}
        assert {k:v for k,v in a['request'].items() if k!='system'}=={k:v for k,v in b['request'].items() if k!='system'}
        for r in pair:
            body=r['request'];assert set(body)=={'model','system','prompt','stream','options'}
            assert body['system']==SYSTEMS[r['condition']] and body['model']==MODEL and body['stream'] is False
            assert body['options']=={**OPTIONS,'seed':r['seed']}
            assert json.loads(r['request_json'])==body
            payload=json.loads(body['prompt']);assert set(payload)=={'state','target_action','VERIFIED_CHRONOLOGICAL_HISTORY'}
            assert payload['VERIFIED_CHRONOLOGICAL_HISTORY']==[] and payload['state']==r['state'] and payload['target_action']==r['target']
            assert sha(body['prompt'].encode())==r['user_payload_sha256']


def classify(entry,response):
    raw=response['response'];s=shape(raw,entry['mapping'],entry['target'])
    try: parsed=parse(raw);error=None
    except ValueError as exc: parsed=None;error=str(exc)
    assert parsed==s['strict_parsed_prediction'] and error==s['strict_parser_error']
    return dict(index=entry['index'],context=entry['context'],condition=entry['condition'],
        episode=entry['episode'],family=entry['family'],request=entry['request'],request_json=entry['request_json'],
        response=response,parsed=parsed,parse_error=error,shape=s,
        historical_raw_identical=raw==entry['historical_raw'])


def metrics(rows):
    shapes=[r['shape'] for r in rows]
    out=dict(completed=len(rows),valid=sum(s['strict_valid'] for s in shapes),
        JSON_decodable=sum(s['json_parses'] for s in shapes),
        exact_keys=sum(s['json_parses'] and set(s['ordered_keys'])=={'next_state','consequence'} and not s['duplicate_keys'] for s in shapes),
        opaque_token_consequence=sum(bool(s['bare_consequence_token']) for s in shapes),
        prose_string_consequence=sum('consequence' in s['prose_inside_fields'] for s in shapes),
        embedded_token_consequence=sum(bool(s['opaque_tokens_by_field'].get('consequence')) and not s['bare_consequence_token'] for s in shapes))
    for field,domain in [('next_state',range(4)),('consequence',(-1,0,1))]:
        out['integer_'+field]=sum(s['fields'][field]['type']=='int' for s in shapes)
        out['in_domain_'+field]=sum(s['fields'][field]['type']=='int' and s['fields'][field]['value'] in domain for s in shapes)
    out['other_categories']={k:sum(bool(s[k]) for s in shapes) for k in ('numeric_string_fields','bool_fields','float_fields','null_fields','extra_fields','missing_fields','duplicate_keys','multiple_objects','prose_outside_json')}
    out['other_categories']['out_of_domain_integer']=sum(any(s['fields'][k]['type']=='int' and s['fields'][k]['value'] not in domain for k,domain in [('next_state',range(4)),('consequence',(-1,0,1))]) for s in shapes)
    out['malformed_reasons']=dict(Counter(s['strict_parser_error'] for s in shapes if not s['strict_valid']))
    out['consequence_types']=dict(Counter(s['fields']['consequence']['type'] or 'missing' for s in shapes))
    return out


def summarize(reg,rows,meta):
    validate_registration(reg)
    for i,r in enumerate(rows):
        assert r['index']==i and r==classify(reg['plan'][i],r['response'])
    cond={c:metrics([r for r in rows if r['condition']==c]) for c in 'AB'}
    families={f:{c:metrics([r for r in rows if r['condition']==c and r['family']==f]) for c in 'AB'} for f in ('O1','O2')}
    pairs=[]
    for i in range(9):
        d=reg['plan'][2*i];out={k:d[k] for k in ('context','episode','family','mapping_index','mapping','seed','state','target','action','user_payload_sha256')}
        found={r['condition']:r for r in rows if r['context']==i}
        out.update({c+'_valid':found[c]['shape']['strict_valid'] if c in found else None for c in 'AB'})
        out['A_raw_identical_to_history']=found.get('A',{}).get('historical_raw_identical')
        pairs.append(out)
    improved=sum(p['A_valid'] is False and p['B_valid'] is True for p in pairs)
    reverse=sum(p['A_valid'] is True and p['B_valid'] is False for p in pairs)
    matching=(meta['server']['version']=='0.1.16' and meta['installed_model']['digest']==MANIFEST and meta['verified_model_bytes']['weights_sha256']==WEIGHTS and meta['systems']==SYSTEMS and meta['options']==OPTIONS and all(r['response'].get('model')==MODEL for r in rows))
    gates=dict(B_at_least_8=cond['B']['valid']>=8,at_least_7_improved_pairs=improved>=7,
        at_most_1_reverse_pair=reverse<=1,both_families_nonworse=all(families[f]['B']['valid']>=families[f]['A']['valid'] for f in families),
        all_18_complete=len(rows)==18 and all(r['response'].get('done') is True for r in rows),
        parser_unchanged=sha((ROOT/PARSER_PATH).read_bytes())==PARSER_SHA,
        paired_payloads_identical=all(reg['plan'][2*i]['request']['prompt'].encode()==reg['plan'][2*i+1]['request']['prompt'].encode() for i in range(9)),model_config_seed_matching=matching)
    return dict(study='composition-empty-history-schema-contract-v0',parent=reg['parent'],
        original_contract_replication='OBSERVED' if cond['A']['completed']==9 and cond['A']['valid']==0 else 'NOT OBSERVED',
        replication_definition='all nine original-contract schema failures; partial counts retained',
        explicit_contract_compliance=dict(valid=cond['B']['valid'],registered=9),
        primary_decision='SCHEMA-CONTRACT EFFECT SUPPORTED' if all(gates.values()) else 'SCHEMA-CONTRACT EFFECT NOT ESTABLISHED',
        gates=gates,registered_real_calls=18,completed_real_calls=len(rows),conditions=cond,families=families,pairs=pairs,
        pair_counts=dict(A_invalid_B_valid=improved,A_valid_B_invalid=reverse,
            both_valid=sum(p['A_valid'] is True and p['B_valid'] is True for p in pairs),
            both_invalid=sum(p['A_valid'] is False and p['B_valid'] is False for p in pairs)),
        historical_A_raw_identical=sum(p['A_raw_identical_to_history'] is True for p in pairs),
        preserved_composition=reg['preserved_composition'],parser_sha256=PARSER_SHA,
        registration_sha256=sha(encoded(reg).encode()),metadata_sha256=sha(encoded(meta).encode()),
        model=dict(name=MODEL,server='0.1.16',format='GGUF',parameters='47B',quantization='Q4_0',manifest=MANIFEST,weights=WEIGHTS,options=OPTIONS),
        unknown_is_not_memory=dict(history_projection=[],memory_records_created=0,packages_created=0,receipts_created=0,placeholder_events=0,world_executions=0),
        prediction_accuracy_evaluated=False,composition_tested=False)
