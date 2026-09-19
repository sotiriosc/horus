"""Reconstruct archived contracts and classify text without changing admission."""
import argparse
from collections import Counter
import difflib
import hashlib
import inspect
import json
from pathlib import Path
import re
from types import SimpleNamespace

from experiments.model_map_proposal_v0.adapter import parse, render, serialize, SYSTEM, MODEL, OPTIONS
from experiments.composition_input_bindings_v1.adapters import map_payload
from experiments.model_proposal_role_composition_v1.protocol import schedule, seed
from experiments.model_explorer_semantic_prior_study_v0.adapter import parse_surface

TOKENS=('K1','K2','K3','Q7','M4','Z2')
ACTIONS=('ADVANCE','HOLD','RETREAT')
TEMPLATE='<|im_start|>system\n{{ .System }}<|im_end|>\n<|im_start|>user\n{{ .Prompt }}<|im_end|>\n<|im_start|>assistant\n'


def encoded(value):return json.dumps(value,sort_keys=True,indent=2)+'\n'
def sha(data):return hashlib.sha256(data).hexdigest()
def read(path):return json.loads(path.read_text())
def lines(path):return [json.loads(x) for x in path.read_text().splitlines()]
def mentions(text,tokens):return [t for t in tokens if re.search(r'(?<![A-Za-z0-9_])'+re.escape(t)+r'(?![A-Za-z0-9_])',text)]


def shape(raw,mapping,target):
    pairs=[];duplicates=[]
    def object_hook(items):
        out={}
        for key,value in items:
            if key in out:duplicates.append(key)
            out[key]=value
        pairs.append([k for k,v in items]);return out
    try:value=json.loads(raw,object_pairs_hook=object_hook);json_error=None
    except (ValueError,TypeError) as exc:value=None;json_error=str(exc)
    try:parsed=parse(raw);error=None
    except ValueError as exc:parsed=None;error=str(exc)
    keys=list(value) if type(value) is dict else []
    fields={k:dict(present=k in keys,type=type(value[k]).__name__ if k in keys else None,
                  value=value[k] if k in keys else None) for k in ('next_state','consequence')}
    # Detection only, never conversion/admission or response repair.
    numeric_strings=[k for k in keys if isinstance(value[k],str) and re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?',value[k].strip())]
    opaque={k:mentions(v,TOKENS) for k,v in (value.items() if type(value) is dict else []) if isinstance(v,str)}
    opaque={k:v for k,v in opaque.items() if v}
    canonical={k:mentions(v,ACTIONS) for k,v in (value.items() if type(value) is dict else []) if isinstance(v,str)}
    canonical={k:v for k,v in canonical.items() if v}
    consequence=value.get('consequence') if type(value) is dict else None
    bare=consequence in TOKENS if type(consequence) is str else False
    # An otherwise valid object can contain prose inside a field. That is distinct
    # from prose appended outside the JSON object, which JSON decoding rejects.
    field_prose=[k for k in keys if type(value[k]) is str and bool(re.search(r'\s',value[k].strip()))]
    tail='';multiple=False;outside=False
    if type(raw) is str:
        try:
            _,end=json.JSONDecoder().raw_decode(raw.lstrip());tail=raw.lstrip()[end:].strip()
            if tail:
                try:json.JSONDecoder().raw_decode(tail);multiple=True
                except ValueError:outside=True
        except ValueError:outside=bool(raw.strip())
    return dict(raw_response=raw,raw_sha256=sha(raw.encode()),json_parses=json_error is None,
        json_error=json_error,ordered_keys=keys,object_key_lists=pairs,duplicate_keys=duplicates,
        fields=fields,extra_fields=sorted(set(keys)-{'next_state','consequence'}),
        missing_fields=sorted({'next_state','consequence'}-set(keys)),
        prose_outside_json=outside,prose_inside_fields=field_prose,multiple_objects=multiple,
        numeric_string_fields=numeric_strings,bool_fields=[k for k in keys if type(value[k]) is bool],
        float_fields=[k for k in keys if type(value[k]) is float],null_fields=[k for k in keys if value[k] is None],
        opaque_tokens_by_field=opaque,canonical_actions_by_field=canonical,
        bare_consequence_token=consequence if bare else None,
        bare_token_equals_target=bare and consequence==target,
        bare_token_underlying_action=mapping.get(consequence) if bare else None,
        target_mentioned_in_consequence=type(consequence) is str and target in mentions(consequence,TOKENS),
        consequence_shape='bare_opaque_token' if bare else 'prose_with_target_token' if field_prose and target in opaque.get('consequence',[]) else type(consequence).__name__,
        strict_valid=error is None,strict_parser_error=error,strict_parsed_prediction=parsed)


CONTRACT=[
 dict(requirement='single JSON object',visible='explicit',evidence='exactly one JSON object',parser='json.loads plus exact dict type'),
 dict(requirement='next_state and consequence present',visible='explicit',evidence='containing next_state and consequence',parser='exact key-set equality'),
 dict(requirement='no extra keys',visible='not explicitly stated',evidence='containing is not an explicit exclusive key list',parser='exact key-set equality'),
 dict(requirement='next_state exact integer',visible='absent',evidence='neither instruction nor empty payload specifies output type',parser='type(value) is int'),
 dict(requirement='next_state in 0,1,2,3',visible='absent',evidence='current state 0 is not a domain enumeration',parser='next_state in range(4)'),
 dict(requirement='consequence exact integer',visible='absent',evidence='no consequence rows or type declaration in empty payload',parser='type(value) is int'),
 dict(requirement='consequence in -1,0,1',visible='absent',evidence='no output-domain enumeration',parser='consequence in (-1,0,1)'),
 dict(requirement='no bool/float/numeric-string/null fields',visible='absent',evidence='no explicit output type restriction',parser='exact int rejects these JSON values'),
 dict(requirement='no explanation',visible='explicit',evidence='and no explanation',parser='outside prose fails JSON decode; fields must be integers'),
 dict(requirement='no multiple JSON objects',visible='explicit',evidence='exactly one JSON object',parser='json.loads rejects trailing content'),
 dict(requirement='no duplicate keys',visible='not explicitly stated',evidence='no uniqueness clause',parser='object_pairs_hook raises duplicate field'),
]


def runtime(meta):
    assert meta['template']['template']==TEMPLATE
    return dict(model=meta['model'],server=meta['server'],model_digest=meta['installed_model']['digest'],
        details=meta['installed_model']['details'],weights_digest=meta['verified_model_bytes']['weights_sha256'],
        template=meta['template']['template'],stored_default_system=meta['template']['system'],
        stored_parameters=meta['template']['parameters'])


def reconstruct_live(directory):
    calls=lines(directory/'model-calls.jsonl');steps=lines(directory/'steps.jsonl');meta=read(directory/'metadata.json')
    plan=schedule();assert read(directory/'schedule.json')==plan
    assert len(calls)==21 and len(steps)==12
    maps=[];explorers=[];unknown=[]
    for s in steps:
        p=s['probe'];assert p['before']==p['after']
        assert not p['authorization']['executed'] and not p['authorization']['committed']
        assert p['receipt'] is None and p['prediction'] is None
        assert p['before']['memory']==p['before']['packages']==p['before']['pairs']==[]
        assert 'UNTRIED' not in json.dumps(p['before'])
        unknown.append(dict(episode=s['episode'],memory_record_count=0,packages=0,receipt_absent=True,no_placeholder_records=True))
    for call in calls:
        d=plan[call['episode']];mapping=d['mapping']
        assert call['mapping']==mapping and call['options']['seed']==seed(d,call['decision'],call['role'])
        assert call['memory']==[] and not call['transport_error']
        if call['role']=='Map':
            target=call['input']['target_action'];action=mapping[target]
            expected=serialize(map_payload(call['current_state'],action,[],mapping))
            assert expected==call['exact_prompt'] and json.loads(expected)==call['input']
            assert call['system']==SYSTEM==meta['role_systems']['Map']
            assert call['options']=={**OPTIONS,'seed':seed(d,0,'Map')}
            previous=calls[call['index']-1]
            assert previous['role']=='Explorer' and previous['episode']==call['episode']
            assert previous['parsed']['action']==action
            body=dict(model=MODEL,system=SYSTEM,prompt=expected,stream=False,options={**OPTIONS,'seed':call['options']['seed']})
            rendered=TEMPLATE.replace('{{ .System }}',SYSTEM).replace('{{ .Prompt }}',expected)
            assert 'integer' not in (SYSTEM+expected).lower()
            classified=shape(call['raw_output'],mapping,target)
            assert classified['strict_parser_error']==call['parse_error'] and call['parsed'] is None
            maps.append(dict(call_index=call['index'],episode=call['episode'],family=d['family'],mapping_index=d['mapping_index'],
                mapping=mapping,seed=call['options']['seed'],action=action,target=target,state=call['current_state'],
                history_depth=0,classification=classified,request_body=body,request_json=json.dumps(body),
                exact_prompt=expected,rendered_template=rendered,payload=call['input'],runtime=runtime(meta)))
        elif call['role']=='Explorer' and call['parse_error']:
            raw=call['raw_output'];_,_,error=parse_surface(raw,dict(surface_option_order=list(mapping),surface_to_underlying=mapping))
            assert error==call['parse_error']
            try:value=json.loads(raw)
            except ValueError:value=None
            explorers.append(dict(episode=call['episode'],family=d['family'],mapping_index=d['mapping_index'],mapping=mapping,
                seed=call['options']['seed'],raw_response=raw,raw_sha256=sha(raw.encode()),
                form='single_JSON_object' if type(value) is dict else 'other',keys=list(value) if type(value) is dict else [],
                offered_aliases_present=mentions(raw,mapping),canonical_actions=mentions(raw,ACTIONS),
                multiple_aliases=len(mentions(raw,mapping))>1,UNTRIED_present='UNTRIED' in raw,strict_error=error))
    assert len(maps)==9 and len(explorers)==3
    return maps,explorers,unknown


def historical(directory,name):
    archived=lines(directory/'model-calls.jsonl');registered=read(directory/'registered-prompts.json');meta=read(directory/'metadata.json')
    assert registered['system']==SYSTEM and registered['options']==OPTIONS and len(registered['plan'])==144
    allrows=[]
    for row in archived:
        c=row['model_call'];d=row['descriptor'];rs=[SimpleNamespace(**x) for x in d['fixture_memory']]
        assert d==registered['plan'][d['index']]
        prompt=serialize(render(rs,d));assert prompt==c['exact_prompt']==d['exact_prompt']
        assert c['system']==SYSTEM==meta['system'] and c['options']=={**OPTIONS,'seed':d['seed']}
        assert all(x['exact_authentic_object'] and x['full_binding_verified'] for x in d['fixture_provenance'])
        classified=shape(c['raw_output'],d['mapping'],c['payload']['target_action'])
        assert classified['strict_parser_error']==c['parse_error']
        assert classified['strict_parsed_prediction']==c['parsed_prediction']
        history=c['payload']['VERIFIED_CHRONOLOGICAL_HISTORY'];assert history and all(type(x['next_state']) is int and type(x['consequence']) is int for x in history)
        allrows.append(dict(index=d['index'],family=d['family'],mapping_index=d['mapping_index'],mapping=d['mapping'],
            arm=d['arm'],stage=d['stage'],state=1,action='HOLD',target=c['payload']['target_action'],seed=d['seed'],
            history_depth=len(history),payload=c['payload'],exact_prompt=prompt,system=c['system'],options=c['options'],
            classification=classified,runtime=runtime(meta)))
    summary=dict(study=name,calls=len(allrows),valid=sum(r['classification']['strict_valid'] for r in allrows),
        malformed=sum(not r['classification']['strict_valid'] for r in allrows),
        history_depths=dict(Counter(r['history_depth'] for r in allrows)),
        compliance_by_depth={str(n):dict(calls=sum(r['history_depth']==n for r in allrows),
            valid=sum(r['history_depth']==n and r['classification']['strict_valid'] for r in allrows)) for n in sorted({r['history_depth'] for r in allrows})},
        state_action_scope='state 1 / HOLD',numeric_next_state_example_calls=len(allrows),numeric_consequence_example_calls=len(allrows),
        history_next_state_values=sorted({x['next_state'] for r in allrows for x in r['payload']['VERIFIED_CHRONOLOGICAL_HISTORY']}),
        history_consequence_values=sorted({x['consequence'] for r in allrows for x in r['payload']['VERIFIED_CHRONOLOGICAL_HISTORY']}),
        malformed_reasons=dict(Counter(r['classification']['strict_parser_error'] for r in allrows if not r['classification']['strict_valid'])),
        strict_parser='experiments.model_map_proposal_v0.adapter.parse',system_identical=True,history_numeric_examples_are_implicit_not_explicit_contract=True)
    return summary,allrows


def run(composition,map0,map1):
    root=Path(__file__).resolve().parents[2]
    parser_path='experiments/model_map_proposal_v0/adapter.py'
    parser_digest=sha((root/parser_path).read_bytes())
    assert read(composition/'results.json')['source_sha256'][parser_path]==parser_digest
    assert read(map0/'results.json')['source_sha256'][parser_path]==parser_digest
    assert read(root/'experiments/model_map_established_prior_revision_v1/frozen-inputs.json')['additional_source_sha256'][parser_path]==parser_digest
    live,explorers,unknown=reconstruct_live(composition)
    h0,rows0=historical(map0,'Map v0');h1,rows1=historical(map1,'established-prior Map v1')
    a=min((r for r in live if r['action']=='HOLD'),key=lambda r:r['episode'])
    def representative(rows,stage):
        return min((r for r in rows if r['arm']=='CONTROL' and r['stage']==stage and r['family']==a['family'] and r['mapping']==a['mapping'] and r['target']==a['target']),key=lambda r:r['index'])
    b=representative(rows0,'H0');c=representative(rows1,'P0')
    differences={}
    for label,item in [('A_composition',a),('B_Map_v0',b),('C_Map_v1',c)]:
        body=item.get('request_body',{});options=body.get('options',item.get('options'))
        differences[label]=dict(index=item.get('episode',item.get('index')),state=item['state'],action=item['action'],target=item['target'],
            history_length=item['history_depth'],history_rows=item['payload']['VERIFIED_CHRONOLOGICAL_HISTORY'],
            seed=item['seed'],non_seed_options={k:v for k,v in options.items() if k!='seed'},
            exact_system=SYSTEM,serialization='sorted keys, compact separators',runtime=item['runtime'])
    assert b['runtime']['template']==c['runtime']['template']==a['runtime']['template']
    for field in ('model','server','model_digest','details','weights_digest','stored_default_system'):
        assert a['runtime'][field]==b['runtime'][field]==c['runtime'][field]
    assert sorted(a['runtime']['stored_parameters'].splitlines())==sorted(b['runtime']['stored_parameters'].splitlines())==sorted(c['runtime']['stored_parameters'].splitlines())
    assert differences['A_composition']['non_seed_options']==differences['B_Map_v0']['non_seed_options']==differences['C_Map_v1']['non_seed_options']
    prompt_diffs={label:'\n'.join(difflib.unified_diff(a['exact_prompt'].splitlines(),r['exact_prompt'].splitlines(),fromfile='composition',tofile=label,lineterm='')) for label,r in [('Map_v0',b),('Map_v1',c)]}
    compact_rows=[]
    for r in live:
        s=r['classification']
        compact_rows.append({**{k:r[k] for k in ('call_index','episode','family','mapping_index','mapping','seed','action','target')},
            'json_parses':s['json_parses'],'keys':s['ordered_keys'],
            'next_state_type':s['fields']['next_state']['type'],'next_state_value':s['fields']['next_state']['value'],
            'consequence_type':s['fields']['consequence']['type'],'consequence_shape':s['consequence_shape'],
            'opaque_tokens':s['opaque_tokens_by_field'],'bare_token':s['bare_consequence_token'],
            'bare_token_equals_target':s['bare_token_equals_target'],'bare_token_underlying_action':s['bare_token_underlying_action'],
            'target_mentioned_in_consequence':s['target_mentioned_in_consequence'],'strict_error':s['strict_parser_error']})
    result=dict(classification='A — CONCRETE MODEL/PARSER SPECIFICATION GAP IDENTIFIED',
        secondary='EMPTY-HISTORY ASSOCIATION OBSERVED',new_model_calls=0,
        preserved_live_classification='C — NOT ESTABLISHED',live_calls=dict(Explorer=12,Map=9,Recovery=0),
        live_Explorer_valid=9,live_Explorer_malformed=3,live_Map_valid=0,live_Map_malformed=9,executions=0,memory_commits=0,
        map_cases=compact_rows,shape_counts=dict(Counter(r['classification']['consequence_shape'] for r in live)),
        all_nine=dict(single_valid_json=True,exact_keys=True,next_state_integer_1=True,consequence_string=True,
            parser_error='exact integers required',empty_history=True,numeric_consequence_examples_absent=True),
        bare_token_counts=dict(Counter(r['classification']['bare_consequence_token'] for r in live if r['classification']['bare_consequence_token'])),
        token_mentions=dict(Counter(t for r in live for t in r['classification']['opaque_tokens_by_field'].get('consequence',[]))),
        bare_token_equal_target=sum(r['classification']['bare_token_equals_target'] for r in live),
        target_mentioned=sum(r['classification']['target_mentioned_in_consequence'] for r in live),
        next_state_token_leaks=sum(bool(r['classification']['opaque_tokens_by_field'].get('next_state')) for r in live),
        exclusions={field:sum(bool(r['classification'][field]) for r in live) for field in ('extra_fields','missing_fields','duplicate_keys','prose_outside_json','multiple_objects','numeric_string_fields','bool_fields','float_fields','null_fields','canonical_actions_by_field')},
        parser_contract=CONTRACT,explicit_output_integer_types=False,explicit_output_domains=False,
        identical_archived_parser_source_sha256=parser_digest,
        visible_empty_payload_numbers=dict(current_state=[0],output_next_state_examples=[],output_consequence_examples=[],allowed_output_domain=None),
        historical=[h0,h1],representative_comparison=differences,
        malformed_explorer=[{k:v for k,v in r.items() if k not in ('raw_response','raw_sha256')} for r in explorers],
        family_patterns={family:dict(calls=sum(r['family']==family for r in live),shapes=dict(Counter(r['classification']['consequence_shape'] for r in live if r['family']==family))) for family in ('O1','O2')},
        unknown_is_not_memory=True,causal_effect_established=False,
        recommendation=dict(option=2,conceptual_variable='original visible output schema versus explicit output types/domains',
            matched=['state','target action','empty history','mapping','seed','parser','model','sampler'],implemented=False))
    for r in live:
        s=r['classification']
        assert s['json_parses'] and set(s['ordered_keys'])=={'next_state','consequence'}
        assert s['fields']['next_state']==dict(present=True,type='int',value=1)
        assert s['fields']['consequence']['type']=='str' and s['strict_parser_error']=='exact integers required'
    assert all(n==0 for n in result['exclusions'].values())
    evidence=dict(composition_requests=live,malformed_explorer=explorers,unknown_storage_audit=unknown,
        historical_map_v0=rows0,historical_map_v1=rows1,representative_prompt_diffs=prompt_diffs,
        parser_source=inspect.getsource(parse),exact_map_system=SYSTEM)
    return result,evidence


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('composition','map0','map1','output'):parser.add_argument('--'+name,required=True,type=Path)
    parser.add_argument('--replay',type=Path);args=parser.parse_args()
    if args.output.resolve().is_relative_to(Path(__file__).resolve().parents[2]):raise ValueError('private evidence requires external directory')
    result,evidence=run(args.composition,args.map0,args.map1)
    source_hashes={}
    for label,directory,names in [('composition',args.composition,('model-calls.jsonl','steps.jsonl','schedule.json','metadata.json','results.json')),
        ('map0',args.map0,('model-calls.jsonl','registered-prompts.json','metadata.json','results.json')),
        ('map1',args.map1,('model-calls.jsonl','registered-prompts.json','metadata.json','results.json'))]:
        for name in names:source_hashes[label+'/'+name]=sha((directory/name).read_bytes())
    result['input_evidence_sha256']=source_hashes
    args.output.mkdir(parents=True,exist_ok=False)
    for name,value in [('results.json',result),('diagnostic-private.json',evidence)]:
        text=encoded(value)
        if args.replay:assert text==(args.replay/name).read_text(),name
        (args.output/name).write_text(text)
    print(result['classification']);print(result['secondary']);print('ZERO NEW MODEL CALLS')
    if args.replay:print('Both diagnostic files byte-identical')


if __name__=='__main__':main()
