"""Deterministic public-data description; never invokes a scorer or inference API."""
import argparse
from collections import Counter
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import subprocess
import sys

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
B = ROOT / 'research/blind-diagnostic-generalization-v0'
R = B / 'replacement-r2'
CODEBOOK_FREEZE = '36a2f7f4b498707cbb71b26e68cc25226918982a'
BASE = 'f4becaf11220f853a87e741fa84009bd0de715b2'
sys.path.insert(0, str(B))
from scorer import strict_json  # Parsing only. No score_rendering/score_benchmark calls.
import jsonschema

D = 'SUPPORTED_CURRENT_DEFECT'
H = 'NO_SUPPORTED_DIAGNOSIS'
U = 'INSUFFICIENT_EVIDENCE'
T = 'HISTORICAL_DEFECT_NOT_CURRENT'
X = 'INVALID_OR_CONTRADICTORY_EVIDENCE'
CLASSES = [D,H,U,T,X]
OPAQUE = re.compile(r'\bz[0-9a-f]{16}\b')
FULL_ID = re.compile(r'z[0-9a-f]{16}')
FIELDS = ['contract_evidence_id','cause_evidence_id','effect_evidence_id','decisive_evidence_id','decisive_field','observed_value','required_value']
MISSING = object()


def read(path):
    return json.loads(path.read_bytes())


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=True) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def same(a, b):
    return type(a) is type(b) and a == b


def pointer_token(value):
    return str(value).replace('~','~0').replace('/','~1')


def strings(value, path=''):
    if isinstance(value, str):
        yield path, 'value', value
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from strings(child, path + '/' + str(i))
    elif isinstance(value, dict):
        for key, child in value.items():
            target = path + '/' + pointer_token(key)
            yield target, 'key', key
            yield from strings(child, target)


def invented_locations(answer, case):
    allowed = {s for _, _, s in strings(case) if FULL_ID.fullmatch(s)}
    locations = []
    for path, kind, text in strings(answer):
        for match in OPAQUE.finditer(text):
            if match.group() not in allowed:
                locations.append(dict(id=match.group(), path=path, kind=kind, start=match.start(), end=match.end()))
    return sorted({v['id'] for v in locations}), locations


def witness_checks(answer, gold):
    witnesses = [gold['mechanism_witness'], *gold.get('mechanism_alternatives', [])]
    mechanism = answer.get('causal_mechanism')
    mechanism = mechanism if isinstance(mechanism, dict) else {}
    exact = {field: any(same(mechanism.get(field, MISSING), w[field]) for w in witnesses) for field in FIELDS}
    indices = [i for i, w in enumerate(witnesses) if all(same(mechanism.get(k, MISSING), v) for k, v in w.items())]
    return exact, bool(indices), indices


def failure_reason(row):
    wrong_class = row['selected_classification'] != row['gold_classification']
    validity = not row['schema_valid'] or not row['ids_valid']
    return ('both' if wrong_class and validity else 'classification_only' if wrong_class else 'schema_or_id_validity_only' if validity else 'none')


def code_counts(rows, codes):
    return {code: dict(renderings=sum(code in r['codes'] for r in rows),
        semantic_cases=len({r['semantic_case_id'] for r in rows if code in r['codes']})) for code in codes}


def selection_counts(rows):
    return {c: dict(renderings=sum(r['selected_classification'] == c for r in rows),
        semantic_cases_with_any=len({r['semantic_case_id'] for r in rows if r['selected_classification'] == c})) for c in [*CLASSES, None]}


def field_counts(rows):
    rows = [r for r in rows if r['gold_classification'] == D]
    names = ['affected_component_exact', *FIELDS, 'all_required_evidence_cited', 'structured_witness_exact']
    def value(r, name):
        return r['witness_field_exact'][name] if name in FIELDS else r[name]
    case_ids = sorted({r['semantic_case_id'] for r in rows})
    return dict(renderings=len(rows), semantic_cases=len(case_ids), exact={name: dict(
        renderings=sum(value(r, name) for r in rows),
        semantic_cases_any=sum(any(value(r, name) for r in rows if r['semantic_case_id'] == c) for c in case_ids),
        semantic_cases_all_four=sum(all(value(r, name) for r in rows if r['semantic_case_id'] == c) for c in case_ids)) for name in names},
        field_mismatch_count_distribution=dict(sorted(Counter(sum(not v for v in r['witness_field_exact'].values()) for r in rows).items())))


def verify_inputs():
    for name in ('codebook.json','input-manifest.json','preservation-baseline.json','README.md'):
        f = P/name
        assert f.read_bytes() == git('show', CODEBOOK_FREEZE + ':' + str(f.relative_to(ROOT))), name
    manifest = read(P/'input-manifest.json')
    for name, want in manifest['files'].items():
        assert sha((ROOT/name).read_bytes()) == want, name
    assert importlib.metadata.version('jsonschema') == '3.2.0'
    assert read(R/'scores.json')['classification'] == 'BLIND_DIAGNOSTIC_CAPABILITY_NOT_ESTABLISHED_V0'
    return manifest


def build():
    manifest = verify_inputs()
    codebook = read(P/'codebook.json')
    codes = codebook['codes']
    grading = read(B/'materialized/grading.json')
    cases = read(B/'materialized/case-manifest.json')['cases']
    family = {c['case_id']: c['family'] for c in cases}
    schedule = read(B/'materialized/render-manifest.json')['schedule']
    scores = read(R/'scores.json')
    prior = read(R/'secondary-analysis.json')
    schema = read(B/'diagnostic-schema.json')
    pairs = read(B/'materialized/matched-pairs.json')
    assert len(schedule) == len(set(schedule)) == 80
    rows = []
    for position, rid in enumerate(schedule, 1):
        g = grading[rid]; gold = g['gold']; credit = scores['renderings'][rid]
        raw = (R/'raw/finals'/(rid+'.txt')).read_bytes()
        try:
            answer = strict_json(raw.decode('utf-8')); parsed = True
        except (ValueError,TypeError):
            answer = None; parsed = False
        valid = False
        if parsed:
            try:
                jsonschema.validate(answer, schema); valid = True
            except jsonschema.ValidationError:
                pass
        assert valid == credit['schema_valid']
        a = answer if isinstance(answer,dict) else {}
        selected = a.get('classification') if a.get('classification') in CLASSES else None
        assert selected == credit['classification']
        cited = a.get('evidence_ids', [])
        cited = {s for s in cited if isinstance(s,str)} if isinstance(cited,list) else set()
        missing = sorted(set(gold['required_evidence']) - cited)
        case = read(B/'materialized/rendered'/(rid+'.json'))
        invented, locations = invented_locations(answer,case)
        local = gold['classification'] == D
        fields, full, matching = witness_checks(a,gold) if local else (None,None,None)
        component = a.get('affected_component_ids',MISSING) == gold['affected_components'] if local else None
        applied = []
        for name, definition in codes.items():
            layer = definition['layer']; pred = definition['predicate']; yes = False
            if layer == 'classification' and gold['classification'] == pred['gold']:
                yes = selected == D if pred['selected']=='== D' else selected != D if pred['selected']=='!= D' else selected not in [gold['classification'], D]
            elif layer == 'localization' and local:
                yes = not component if name=='COMPONENT_MISMATCH' else not full if name=='STRUCTURED_WITNESS_MISMATCH' else not fields[pred['field']]
            elif name=='MISSING_REQUIRED_EVIDENCE': yes = bool(missing)
            elif name=='INVENTED_ID': yes = bool(invented)
            elif name=='EVIDENCE_GROUNDING_PASS': yes = credit['evidence_grounded']
            elif name=='STRICT_JSON_FAILURE': yes = not parsed
            elif name=='SCHEMA_FAILURE': yes = parsed and not credit['schema_valid']
            elif name=='CLASSIFICATION_SCHEMA_PASS': yes = credit['schema_valid'] and selected in CLASSES
            if yes: applied.append(name)
        rows.append(dict(render_id=rid, schedule_position=position, semantic_case_id=g['case_id'],family=family[g['case_id']],
            label_map=g['label_map'], presentation_order=g['order'],gold_classification=gold['classification'],selected_classification=selected,
            strict_json_valid=parsed,schema_valid=credit['schema_valid'],ids_valid=credit['ids_valid'],classification_correct=credit['classification_correct'],
            affected_component_exact=component, structured_witness_exact=full,witness_field_exact=fields,matching_accepted_witness_indices=matching,
            evidence_grounded=credit['evidence_grounded'],all_required_evidence_cited=not missing,missing_required_evidence=missing,
            invented_ids=invented,invented_id_locations=locations,original_bad_or_invented_ids=credit['invented_ids'],
            schema_errors=prior['per_render_diagnostics'][rid]['schema_errors'],codes=applied,original_scorer_credit=credit,raw_final_sha256=sha(raw)))
    lookup={(r['semantic_case_id'],r['label_map'],r['presentation_order']):r for r in rows}
    contrasts=[]
    for c in cases:
        cid=c['case_id']
        for code, cells in [('LABEL_MAP_CLASS_DISAGREEMENT',[(('A',o),('B',o)) for o in (1,2)]),('ORDER_CLASS_DISAGREEMENT',[((l,1),(l,2)) for l in ('A','B')])]:
            for left,right in cells:
                a=lookup[(cid,*left)];b=lookup[(cid,*right)];disagree=a['selected_classification']!=b['selected_classification']
                contrasts.append(dict(code=code,semantic_case_id=cid,gold_classification=c['gold']['classification'],family=c['family'],render_ids=[a['render_id'],b['render_id']],selected_classes=[a['selected_classification'],b['selected_classification']],disagreement=disagree))
                if disagree:
                    a['codes'].append(code);b['codes'].append(code)
        if not scores['semantic_cases'][cid]['consistent']:
            for r in rows:
                if r['semantic_case_id']==cid:r['codes'].append('SEMANTIC_REPRESENTATION_INCONSISTENT')
    for r in rows:
        r['codes']=[code for code in codes if code in r['codes']]
        r['failure_codes']=[code for code in r['codes'] if codes[code]['kind']=='failure']
        r['pass_markers']=[code for code in r['codes'] if codes[code]['kind']=='pass_marker']
    semantics=[]
    for c in cases:
        cid=c['case_id'];rs=[lookup[cid,l,o] for l in ('A','B') for o in (1,2)];credit=scores['semantic_cases'][cid]
        semantics.append(dict(semantic_case_id=cid,family=c['family'],gold_classification=c['gold']['classification'],
            renderings=[dict(render_id=r['render_id'],label_map=r['label_map'],presentation_order=r['presentation_order'],selected_classification=r['selected_classification'],schema_valid=r['schema_valid'],ids_valid=r['ids_valid']) for r in rs],
            code_counts={code:sum(code in r['codes'] for r in rs) for code in codes},
            classification_credit=credit['classification_correct'],localization_credit=credit['localized'] if c['gold']['classification']==D else None,
            evidence_grounding_credit=credit['evidence_grounded'],representation_consistent=credit['consistent'],
            matched_pair_membership=[p['pair_id'] for p in pairs if cid in [p['left'],p['right']]],original_scorer_credit=credit))
    pair_rows=[]
    for pair in pairs:
        cells=[];old=next(p for p in scores['matched_pairs'] if p['pair_id']==pair['pair_id'])
        for l in ('A','B'):
            for o in (1,2):
                endpoints={side:lookup[pair[side],l,o] for side in ('left','right')}
                endpoints={side:dict(render_id=r['render_id'],semantic_case_id=r['semantic_case_id'],gold_classification=r['gold_classification'],selected_classification=r['selected_classification'],schema_valid=r['schema_valid'],ids_valid=r['ids_valid'],classification_correct=r['classification_correct'],failure_reason=failure_reason(r)) for side,r in endpoints.items()}
                failed=[side for side,r in endpoints.items() if not r['classification_correct']]
                wrong=any(r['selected_classification']!=r['gold_classification'] for r in endpoints.values())
                validity=any(not r['schema_valid'] or not r['ids_valid'] for r in endpoints.values())
                reason='both' if wrong and validity else 'classification_only' if wrong else 'schema_or_id_validity_only' if validity else 'none'
                cells.append(dict(label_map=l,presentation_order=o,endpoints=endpoints,failed_endpoints=failed,both_correct=not failed,failure_reason=reason))
        assert sum(c['both_correct'] for c in cells)==old['correct_cells']
        pair_rows.append(dict(pair_id=pair['pair_id'],original_pair=pair,semantic_endpoints={side:dict(semantic_case_id=pair[side],gold_classification=scores['semantic_cases'][pair[side]]['gold_classification'],classification_credit=scores['semantic_cases'][pair[side]]['classification_correct']) for side in ('left','right')},
            semantic_failed_endpoints=[side for side in ('left','right') if not scores['semantic_cases'][pair[side]]['classification_correct']],cells=cells,original_pair_pass=old['correct_direction'],original_scorer_credit=old,
            failed_cell_reasons=dict(Counter(c['failure_reason'] for c in cells if not c['both_correct']))))
    current=[]
    for r in rows:
        if r['gold_classification']==D:
            raw_answer=strict_json((R/'raw/finals'/(r['render_id']+'.txt')).read_bytes().decode('utf-8'));g=grading[r['render_id']]['gold'];m=raw_answer.get('causal_mechanism') or {}
            current.append(dict(render_id=r['render_id'],semantic_case_id=r['semantic_case_id'],family=r['family'],label_map=r['label_map'],presentation_order=r['presentation_order'],
                affected_component_exact=r['affected_component_exact'],returned_components=raw_answer.get('affected_component_ids'),accepted_components=g['affected_components'],
                field_exact=r['witness_field_exact'],returned_witness_fields={k:m.get(k) for k in FIELDS},accepted_witnesses=[g['mechanism_witness'],*g.get('mechanism_alternatives',[])],
                all_required_evidence_cited=r['all_required_evidence_cited'],missing_required_evidence=r['missing_required_evidence'],full_accepted_witness_exact=r['structured_witness_exact'],original_localization_credit=r['original_scorer_credit']['localized']))
    def group_summary(rs):
        cids={r['semantic_case_id'] for r in rs};ss=[s for s in semantics if s['semantic_case_id'] in cids];cc=[c for c in contrasts if c['semantic_case_id'] in cids]
        return dict(renderings=len(rs),semantic_cases=len(ss),code_counts=code_counts(rs,codes),selected_classes=selection_counts(rs),
            original_classification_renderings=sum(r['classification_correct'] for r in rs),original_classification_semantics=sum(s['classification_credit'] for s in ss),
            original_grounded_renderings=sum(r['evidence_grounded'] for r in rs),original_grounded_semantics=sum(s['evidence_grounding_credit'] for s in ss),
            localization=field_counts(rs),representation=dict(label_map_disagreements=sum(c['disagreement'] and c['code']=='LABEL_MAP_CLASS_DISAGREEMENT' for c in cc),order_disagreements=sum(c['disagreement'] and c['code']=='ORDER_CLASS_DISAGREEMENT' for c in cc),contrasts_each_factor=len(ss)*2,inconsistent_semantic_worlds=sum(not s['representation_consistent'] for s in ss)))
    selected=[]
    for rule in codebook['qualitative_selection']:
        key=rule['first_in_frozen_schedule_with']
        candidates=[r for r in rows if (r['gold_classification']==D and r['affected_component_exact'] and not r['structured_witness_exact'])] if rule['example']=='component_without_witness' else [r for r in rows if key in r['codes']]
        first=candidates[0] if candidates else None
        selected.append(dict(rule=rule,render_id=first['render_id'] if first else None,schedule_position=first['schedule_position'] if first else None,final_sha256=first['raw_final_sha256'] if first else None))
    aggregate=dict(status='R2_DETERMINISTIC_POSTMORTEM_COMPLETE',status_meaning='Mechanical descriptive decomposition completed; not a capability classification',
        original_primary_classification=scores['classification'],original_score_sha256=sha((R/'scores.json').read_bytes()),
        total=group_summary(rows),by_gold_class={c:group_summary([r for r in rows if r['gold_classification']==c]) for c in CLASSES},
        by_family={f:group_summary([r for r in rows if r['family']==f]) for f in dict.fromkeys(c['family'] for c in cases)},
        confusion={g:selection_counts([r for r in rows if r['gold_classification']==g]) for g in CLASSES},
        evidence=dict(missing_required_renderings=sum(bool(r['missing_required_evidence']) for r in rows),missing_required_semantic_cases=len({r['semantic_case_id'] for r in rows if r['missing_required_evidence']}),total_missing_required_id_occurrences=sum(len(r['missing_required_evidence']) for r in rows),missing_count_distribution=dict(sorted(Counter(len(r['missing_required_evidence']) for r in rows).items())),
            invented_id_renderings=sum(bool(r['invented_ids']) for r in rows),invented_id_semantic_cases=len({r['semantic_case_id'] for r in rows if r['invented_ids']}),invented_id_rendering_pairs=sum(len(r['invented_ids']) for r in rows),distinct_invented_ids=sorted({i for r in rows for i in r['invented_ids']}),invented_textual_occurrences=sum(len(r['invented_id_locations']) for r in rows),original_bad_or_invented_id_renderings=sum(bool(r['original_bad_or_invented_ids']) for r in rows)),
        original_mandatory_gates=scores['gates'],original_measured=scores['measured'],original_factor_accuracy=scores['factor_accuracy'],
        matched_pairs=dict(passed=sum(p['original_pair_pass'] for p in pair_rows),total=len(pair_rows)),
        no_new_execution=dict(qwen_calls=0,other_model_calls=0,horus_world_executions=0,receipts=0,memory_writes=0,policy_changes=0,training=0,improvement_proposals=0,hidden_semantic_grader_calls=0),
        counting_notes=codebook['conventions'])
    assert len(rows)==80 and len(semantics)==20 and len(current)==24 and len(pair_rows)==6 and len(contrasts)==80
    assert aggregate['total']['original_classification_renderings']==sum(v['classification_correct'] for v in scores['renderings'].values())
    assert aggregate['total']['representation']['label_map_disagreements']==scores['factor_classification_disagreements']['label_map']
    assert aggregate['total']['representation']['order_disagreements']==scores['factor_classification_disagreements']['presentation_order']
    payloads={'rendering-postmortem.jsonl':b''.join((json.dumps(r,ensure_ascii=True,separators=(',',':'))+'\n').encode() for r in rows),
        'semantic-postmortem.json':encode(semantics),'aggregate-postmortem.json':encode(aggregate),'representation-contrasts.json':encode(contrasts),
        'matched-pair-postmortem.json':encode(pair_rows),'current-defect-postmortem.json':encode(current),'qualitative-selection.json':encode(selected)}
    payloads['deterministic-manifest.json']=encode(dict(codebook_freeze=CODEBOOK_FREEZE,base_commit=BASE,input_manifest_sha256=sha((P/'input-manifest.json').read_bytes()),codebook_sha256=sha((P/'codebook.json').read_bytes()),implementation_sha256=sha(Path(__file__).read_bytes()),public_inputs_only=True,new_model_calls=0,files={name:sha(raw) for name,raw in payloads.items()}))
    for name,want in manifest['files'].items():assert sha((ROOT/name).read_bytes())==want
    return payloads


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=Path,required=True);args=parser.parse_args()
    target=args.output_dir.resolve()
    assert target != ROOT and target != B and target != R
    assert not target.exists(), 'Refuse overwrite of an existing deterministic artifact set'
    payloads=build();target.mkdir(parents=True)
    for name,raw in payloads.items():(target/name).write_bytes(raw)
    print(json.dumps(dict(status='R2_DETERMINISTIC_POSTMORTEM_COMPLETE',renderings=80,semantic_cases=20,files=len(payloads),new_model_calls=0)))


if __name__=='__main__':main()
