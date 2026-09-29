"""Evidence-only engineering harness; no gold, model finals, classifications or scoring."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from support import P,read,pack,run,normalize,canonical_map,independent_checks
from dependency_audit import audit_source

ROOT=P.parents[1]
CONTRACT_FREEZE='11776ad70b29a82f85c34115c088a494370a0f04'
BASE='5687d82cc3eede8561ef435b980f23d919518c26'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encode(v):return (json.dumps(v,sort_keys=True,indent=2,ensure_ascii=True)+'\n').encode()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--implementation-freeze',required=True);parser.add_argument('--output-dir',type=Path,required=True);args=parser.parse_args()
    target=args.output_dir.resolve();assert not target.exists(),'Refuse overwrite of an engineering execution'
    assert not target.is_relative_to(ROOT/'research')
    for freeze in (CONTRACT_FREEZE,args.implementation_freeze):
        subprocess.run(['git','merge-base','--is-ancestor',freeze,'HEAD'],cwd=ROOT,check=True)
        names=subprocess.check_output(['git','ls-tree','-r','--name-only',freeze,'--',str(P.relative_to(ROOT))],cwd=ROOT).decode().splitlines()
        for name in names:assert (ROOT/name).read_bytes()==subprocess.check_output(['git','show',freeze+':'+name],cwd=ROOT),name
    manifest=read(P/'fixture-manifest.json');contract=read(P/'mechanical-contract.json');tests=read(P/'synthetic-test-results.json')
    assert tests['status']=='PASS' and tests['mutation_tests']==19
    entries=manifest['entries'];assert len(entries)==80 and len({r['semantic_group'] for r in entries})==20
    case_ids={e['semantic_group'] for e in entries}|{e['render_id'] for e in entries}
    audit=audit_source((P/'compiler.py').read_text(),case_ids);assert audit['status']=='PASS',audit
    allowed_inputs={str((ROOT/e['path']).resolve()) for e in entries}|{str((P/'mechanical-contract.json').resolve())}
    reads=set();denied=[]
    def guard(event,values):
        if event=='open' and isinstance(values[0],(str,bytes)):
            path=Path(values[0]).resolve();mode=values[1] or '';flags=values[2] or 0
            writing=any(c in str(mode) for c in 'wax+') or bool(flags & 3)
            if writing:
                okay=path.is_relative_to(target)
            else:okay=str(path) in allowed_inputs
            if not okay:
                denied.append(str(path));raise PermissionError('Harness path outside evidence allowlist')
            if not writing:reads.add(str(path))
        if event.startswith('socket.'):raise PermissionError('No network in feasibility harness')
        if event=='subprocess.Popen':
            command=values[1]
            if command != [sys.executable,'-I','-S',str(P/'worker.py')]:raise PermissionError('Only isolated compiler workers allowed')
    sys.addaudithook(guard)
    target.mkdir(parents=True);(target/'compiled').mkdir()
    rendered=[];normalized={};cases={};gate_failures=[];invalid=None
    try:
        for entry in entries:
            case_path=ROOT/entry['path'];raw=case_path.read_bytes();assert sha(raw)==entry['sha256']
            case=json.loads(raw)
            capture_rules=[r['data']['rule'] for r in case['records'] if r['kind']=='capture_contract']
            assert capture_rules and all(rule==contract['source']['common_format_statement'] for rule in capture_rules)
            before=pack(case);out,body=run(case);assert pack(case)==before
            try:checks=independent_checks(case,out)
            except AssertionError:
                checks={'independent_checks':False};gate_failures.append(dict(gate='independent_inventory_checks',render_id=entry['render_id']))
            try:norm=normalize(out,case,canonical_map(case))
            except ValueError as exc:
                norm='UNRESOLVED:'+entry['render_id'];gate_failures.append(dict(gate='evidence_only_alignment',render_id=entry['render_id'],reason=str(exc)))
            normalized[entry['render_id']]=norm;cases[entry['render_id']]=case
            (target/'compiled'/(entry['render_id']+'.json')).write_bytes(body)
            facts=dict(record_count=len(out['record_index']),component_count=len(out['component_index']),version_count=len(out['version_index']),current_version=out['current_version'],current_records=len(out['current_record_ids']),historical_records=len(out['historical_record_ids']),unversioned_records=len(out['unversioned_record_ids']),unresolved_records=len(out['unresolved_record_ids']),unknown_count=len(out['unknown_locations']),event_links=len(out['event_links']),capture_links=len(out['capture_links']),integrity_consistent=out['integrity_consistent'],integrity_checks=dict(Counter(f['check']+':'+str(f['consistent']) for f in out['integrity_findings'])),field_entries=len(out['field_inventory']),graph_nodes=len(out['evidence_graph']['nodes']),graph_edges=len(out['evidence_graph']['edges']),input_output_candidate_counts=[len(v['candidates']) for v in out['input_output_candidates']],ambiguities=dict(Counter(v['code'] for v in out['ambiguities'])))
            rendered.append(dict(render_id=entry['render_id'],semantic_group=entry['semantic_group'],label_map=entry['label_map'],order=entry['order'],input_sha256=entry['sha256'],output_sha256=sha(body),normalized_sha256=sha(norm.encode()),checks=checks,facts=facts))
    except Exception as exc:
        invalid=dict(type=type(exc).__name__,message=str(exc),completed_renderings=len(rendered))
    groups=[]
    if not invalid:
        for cid in sorted({e['semantic_group'] for e in entries}):
            rows=sorted([r for r in rendered if r['semantic_group']==cid],key=lambda r:(r['label_map'],r['order']))
            assert [(r['label_map'],r['order']) for r in rows]==[('A',1),('A',2),('B',1),('B',2)]
            same=len({r['normalized_sha256'] for r in rows})==1
            if not same:gate_failures.append(dict(gate='full_representation_normalization',semantic_group=cid))
            groups.append(dict(semantic_group=cid,representative=rows[0]['render_id'],all_four_normalized_identical=same,render_ids=[r['render_id'] for r in rows],facts=rows[0]['facts']))
    outcome='INVALID_STUDY' if invalid or denied else 'GROUNDED_DIAGNOSTIC_EVIDENCE_COMPILER_NOT_ESTABLISHED_V0' if gate_failures else 'GROUNDED_DIAGNOSTIC_EVIDENCE_COMPILER_FEASIBLE_V0'
    def sumfacts(key):return sum(g['facts'][key] for g in groups)
    totals=dict(semantic_packages=len(groups),rendered_packages=len(rendered),normalized_worlds=sum(g['all_four_normalized_identical'] for g in groups),records=sumfacts('record_count'),unknown_locations=sumfacts('unknown_count'),event_links=sumfacts('event_links'),capture_links=sumfacts('capture_links'),field_entries=sumfacts('field_entries'),graph_nodes=sumfacts('graph_nodes'),graph_edges=sumfacts('graph_edges'),current_deployment_resolved=sum(g['facts']['current_version'] is not None for g in groups),integrity_states=dict(Counter(str(g['facts']['integrity_consistent']) for g in groups)),integrity_checks=dict(sum((Counter(g['facts']['integrity_checks']) for g in groups),Counter())),ambiguities=dict(sum((Counter(g['facts']['ambiguities']) for g in groups),Counter())))
    report=dict(classification=outcome,interpretation='Engineering fact extraction only; no diagnostic capability, classification, model improvement or architecture utility inference.',contract_freeze=CONTRACT_FREEZE,implementation_freeze=args.implementation_freeze,base=BASE,gate_failures=gate_failures,invalid=invalid,totals=totals,renderings=rendered,semantic_packages=groups,
        dependency_audit=dict(**audit,harness_allowed_reads=len(allowed_inputs),harness_observed_reads=sorted(str(Path(p).relative_to(ROOT)) for p in reads),denied_accesses=denied,runtime='Every worker denies all filesystem opens, non-json imports, network and subprocess activity after compiler/stdlib bootstrap; static source audit and three malicious-module probes passed.',gold_files_read=0,scientific_scorer_imports=0),mutation_tests=19,synthetic_tests=tests['tests'],python=platform.python_version(),zero_inference=dict(qwen_calls=0,other_model_calls=0,model_server_starts=0,horus_world_executions=0,receipts=0,memory_writes=0,training=0,policy_changes=0,architecture_promotion=0,self_improvement_proposals=0))
    (target/'feasibility-results.json').write_bytes(encode(report))
    print(json.dumps(dict(classification=outcome,totals=totals,invalid=invalid)),flush=True)
if __name__=='__main__':main()
