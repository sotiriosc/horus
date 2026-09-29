"""Post-primary descriptive analysis only; never changes frozen scores or raw finals."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import jsonschema

P = Path(__file__).resolve().parent
B = P.parent
sys.path.insert(0, str(B))
from scorer import strict_json


def read(path):
    return json.loads(path.read_bytes())


def main():
    score_bytes = (P / 'scores.json').read_bytes()
    score = json.loads(score_bytes)
    assert read(P / 'replay.json')['byte_identical']
    assert score['classification'] != 'INVALID_STUDY'
    grading = read(B / 'materialized/grading.json')
    cases = read(B / 'materialized/case-manifest.json')['cases']
    schema = read(B / 'diagnostic-schema.json')
    protocol = read(B / 'protocol.json')
    classes = list(read(B / 'materialized/case-manifest.json')['class_distribution'])
    D, H, U, T, X = classes
    per = score['renderings']
    semantics = score['semantic_cases']
    matrix = {c: {k: 0 for k in [*classes, 'UNPARSEABLE_OR_NO_VALID_CLASS']} for c in classes}
    diagnostics = {}
    errors = Counter()
    for rid, row in grading.items():
        gold = row['gold']
        result = per[rid]
        matrix[gold['classification']][result['classification'] or 'UNPARSEABLE_OR_NO_VALID_CLASS'] += 1
        try:
            answer = strict_json((P / 'raw/finals' / (rid + '.txt')).read_bytes().decode('utf-8'))
            schema_errors = list(jsonschema.Draft7Validator(schema).iter_errors(answer))
            error_rows = [dict(keyword=e.validator, instance_path=list(e.absolute_path), schema_path=list(e.absolute_schema_path)) for e in schema_errors]
            errors.update(e.validator for e in schema_errors)
            parsed = True
        except (ValueError, TypeError):
            answer = None
            error_rows = [dict(keyword='strict_json_parse')]
            errors['strict_json_parse'] += 1
            parsed = False
        assert (parsed and not error_rows) == result['schema_valid']
        a = answer if isinstance(answer, dict) else {}
        cited = a.get('evidence_ids', [])
        cited = set(cited) if isinstance(cited, list) and all(isinstance(v, str) for v in cited) else set()
        d = dict(strict_json_parsed=parsed, schema_errors=error_rows,
                 missing_required_evidence=sorted(set(gold['required_evidence']) - cited),
                 invented_ids=result['invented_ids'])
        if gold['classification'] == D:
            mechanism = a.get('causal_mechanism')
            witnesses = [gold['mechanism_witness'], *gold.get('mechanism_alternatives', [])]
            matches = [w for w in witnesses if isinstance(mechanism, dict) and all(
                k in mechanism and type(mechanism[k]) is type(v) and mechanism[k] == v for k, v in w.items())]
            d.update(components_exact=a.get('affected_component_ids') == gold['affected_components'],
                     structured_witness_exact=bool(matches),
                     exact_witness_fully_cited=any({v for k, v in w.items() if k.endswith('_evidence_id')} <= cited for w in matches))
        diagnostics[rid] = d
    def summarize(ids, case_ids):
        return dict(renderings=len(ids), schema_valid=sum(per[i]['schema_valid'] for i in ids),
                    classification_correct=sum(per[i]['classification_correct'] for i in ids),
                    localized=sum(per[i]['localized'] for i in ids),
                    evidence_grounded=sum(per[i]['evidence_grounded'] for i in ids),
                    semantic_cases=len(case_ids),
                    semantic_classification_correct=sum(semantics[i]['classification_correct'] for i in case_ids),
                    semantic_localized=sum(semantics[i]['localized'] for i in case_ids),
                    semantic_evidence_grounded=sum(semantics[i]['evidence_grounded'] for i in case_ids),
                    semantic_consistent=sum(semantics[i]['consistent'] for i in case_ids))
    per_class = {}
    for c in classes:
        ids = [i for i, row in grading.items() if row['gold']['classification'] == c]
        case_ids = sorted({grading[i]['case_id'] for i in ids})
        per_class[c] = summarize(ids, case_ids)
    per_family = {}
    for family in dict.fromkeys(c['family'] for c in cases):
        case_ids = [c['case_id'] for c in cases if c['family'] == family]
        ids = [i for i, row in grading.items() if row['case_id'] in case_ids]
        defect_cases = [c for c in case_ids if semantics[c]['gold_classification'] == D]
        defect_ids = [i for i in ids if grading[i]['case_id'] in defect_cases]
        per_family[family] = dict(all_variants=summarize(ids, case_ids), current_defect=summarize(defect_ids, defect_cases))
    current = [i for i, row in grading.items() if row['gold']['classification'] == D]
    valid_current = [i for i in current if per[i]['schema_valid']]
    correct_current = [i for i in current if per[i]['classification_correct']]
    localization = dict(total_current_renderings=len(current), schema_valid_current=len(valid_current),
        frozen_classification_correct=len(correct_current),
        exact_components_among_schema_valid=sum(diagnostics[i]['components_exact'] for i in valid_current),
        exact_structured_witness_among_schema_valid=sum(diagnostics[i]['structured_witness_exact'] for i in valid_current),
        exact_witness_fully_cited_among_schema_valid=sum(diagnostics[i]['exact_witness_fully_cited'] for i in valid_current),
        correct_class_wrong_components=sum(not diagnostics[i]['components_exact'] for i in correct_current),
        correct_class_exact_components_wrong_witness=sum(diagnostics[i]['components_exact'] and not diagnostics[i]['structured_witness_exact'] for i in correct_current),
        frozen_localized_renderings=sum(per[i]['localized'] for i in current),
        frozen_localized_semantics=score['measured']['current_defect_localization_min'])
    metadata = [read(f) for f in sorted((P / 'raw/metadata').glob('*.json'))]
    controls = read(P / 'raw/control-metadata.json')
    def bounds(values):
        return dict(min=min(values), max=max(values), total=sum(values))
    runtime = dict(completed_calls=len(metadata),
        finish_reasons=dict(Counter(m['finish_reason'] for m in metadata)),
        native_separated_reasoning=sum(m['reasoning_separated'] for m in metadata),
        completion_http_statuses=dict(Counter(str(m['http_status']) for m in metadata)),
        control_routes=dict(Counter(m['method'] + ' ' + m['path'] for m in controls)),
        control_http_statuses=dict(Counter(str(m['http_status']) for m in controls)),
        cached_tokens=bounds([m['usage']['prompt_tokens_details']['cached_tokens'] for m in metadata]),
        timing_cache_n=bounds([m['timings']['cache_n'] for m in metadata]),
        prompt_tokens=bounds([m['prompt_tokens'] for m in metadata]),
        completion_tokens=bounds([m['completion_tokens'] for m in metadata]),
        slot_n_erased=bounds([m['n_erased'] for m in metadata]),
        zero_erase_count=sum(m['n_erased'] == 0 for m in metadata),
        positive_erase_count=sum(m['n_erased'] > 0 for m in metadata),
        request_wall_seconds=bounds([m['wall_seconds'] for m in metadata]))
    report = dict(replacement_id='R2', analysis_role='Descriptive only; frozen scores are authoritative and unchanged',
        primary_score_sha256=hashlib.sha256(score_bytes).hexdigest(),
        schema_valid=sum(r['schema_valid'] for r in per.values()), total_finals=len(per),
        strict_json_parsed=sum(d['strict_json_parsed'] for d in diagnostics.values()),
        schema_error_keyword_occurrences=dict(errors),
        confusion_matrix=matrix,
        confusion_definition='Gold rows; raw strictly parsed enum columns, including schema-invalid finals. Scientific classification credit additionally requires full schema and valid IDs.',
        per_class=per_class, per_family=per_family, localization=localization,
        evidence=dict(frozen_grounded_renderings=sum(r['evidence_grounded'] for r in per.values()),
            frozen_grounded_semantics=score['measured']['evidence_grounded_semantics_min'],
            schema_valid_outputs_missing_required_evidence=sum(per[i]['schema_valid'] and bool(d['missing_required_evidence']) for i, d in diagnostics.items()),
            correct_class_outputs_missing_required_evidence=sum(per[i]['classification_correct'] and bool(d['missing_required_evidence']) for i, d in diagnostics.items()),
            invented_id_outputs=sum(bool(r['invented_ids']) for r in per.values()),
            invented_id_output_pairs=sum(len(r['invented_ids']) for r in per.values()),
            distinct_bad_ids=sorted({i for r in per.values() for i in r['invented_ids']})),
        abstention_and_false_positives=dict(
            insufficient_selected=sum(matrix[c][U] for c in classes),
            insufficient_correct_raw_class=matrix[U][U],
            insufficient_to_current=matrix[U][D],
            insufficient_to_healthy=matrix[U][H],
            current_to_insufficient=matrix[D][U],
            current_to_healthy=matrix[D][H],
            healthy_to_current=matrix[H][D],
            historical_to_current=matrix[T][D],
            invalid_correct_raw_class=matrix[X][X],
            invalid_to_current=matrix[X][D]),
        factor_accuracy=score['factor_accuracy'],
        factor_classification_disagreements=score['factor_classification_disagreements'],
        factor_disagreement_denominators=dict(label_map=40, presentation_order=40),
        matched_pairs=score['matched_pairs'],
        mandatory_gates={k: dict(measured=score['measured'][k], threshold=v, comparison='<=' if k.endswith('_max') else '>=', passed=score['gates'][k]) for k, v in protocol['mandatory_gates'].items()},
        runtime=runtime, per_render_diagnostics=diagnostics,
        limitations=['20 designed semantic cases, with four correlated renderings each; not 80 independent samples.',
                    'Structured witnesses are scored exactly under frozen rules; prose is unscored and no semantic corrections are made.',
                    'Server grammar does not enforce all frozen JSON Schema constraints; Python validation remains authoritative.',
                    'Secondary breakdowns are descriptive and cannot upgrade the primary result.'])
    assert (P / 'scores.json').read_bytes() == score_bytes
    target = P / 'secondary-analysis.json'
    value = (json.dumps(report, indent=2, ensure_ascii=True) + '\n').encode()
    if target.exists():
        assert target.read_bytes() == value
    else:
        target.write_bytes(value)
    print(json.dumps({k: report[k] for k in ('schema_valid','total_finals','schema_error_keyword_occurrences','confusion_matrix','localization','evidence','abstention_and_false_positives','runtime')}, indent=2))


if __name__ == '__main__':
    main()
