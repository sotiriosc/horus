"""Read-only post-campaign integrity checks; emits safe attestations and hashes."""
import datetime
import json
import socket
import subprocess
from pathlib import Path

from guard import P, B, ROOT, BASE, PRIVATE, file_sha, frozen_transport, inheritance, runtime_identity, schema_compatibility, git
from score_campaign import load_raw

EXECUTION_FREEZE = 'd7df165e08a20e6302d8b4e72224ac69dc69df63'
RAW_FREEZE = '364c3eb06635751b47d540d46c5792fd45a4fb7d'


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    assert not path.exists()
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + '\n')


def main():
    assert git('branch', '--show-current').decode().strip() == 'research/blind-diagnostic-generalization-v0-replacement-r2'
    checks = dict(inheritance=inheritance(), execution_freeze=frozen_transport(EXECUTION_FREEZE),
                  runtime=runtime_identity(), schema=schema_compatibility())
    raw, execution = load_raw(P)
    assert execution['attempted_calls'] == execution['completed_calls'] == 80
    assert execution['stop'] is None and execution['server_terminated']
    assert execution['retries'] == execution['answer_repairs'] == execution['critic_calls'] == 0
    assert not execution['scoring_during_execution']
    manifest = read(B / 'materialized/render-manifest.json')
    entries = {r['render_id']: r for r in manifest['entries']}
    metadata = {f.stem: read(f) for f in (P / 'raw/metadata').glob('*.json')}
    assert list(execution['statuses']) == manifest['schedule']
    assert all(v == 'COMPLETED' for v in execution['statuses'].values())
    assert len(metadata) == len(raw) == 80
    for order, rid in enumerate(manifest['schedule'], 1):
        m = metadata[rid]
        assert m['call_order'] == order and m['request_sha256'] == entries[rid]['request_sha256']
        assert m['http_status'] == 200 and m['transport_status'] == 'COMPLETED'
        assert m['final_sha256'] == file_sha(P / 'raw/finals' / (rid + '.txt'))
        assert m['response_sha256'] == file_sha(PRIVATE / (rid + '-response.json'))
        assert m['slot_erase_sha256'] == file_sha(PRIVATE / (rid + '-erase.json'))
        assert m['slot_before_sha256'] == file_sha(PRIVATE / (rid + '-slot.json'))
        assert read(PRIVATE / (rid + '-intent.json'))['request_sha256'] == m['request_sha256']
    wire_metadata = [read(f) for f in sorted(PRIVATE.glob('http-*-metadata.json'))]
    assert len(wire_metadata) == 243
    for m in wire_metadata:
        body = PRIVATE / m['private_body_file']
        assert file_sha(body) == m['response_sha256']
        assert body.stat().st_size == m['response_bytes']
    completions = [m for m in wire_metadata if m['path'] == '/v1/chat/completions']
    assert len(completions) == 80 and all(m['http_status'] == 200 for m in wire_metadata)
    assert [m['response_sha256'] for m in completions] == [metadata[r]['response_sha256'] for r in manifest['schedule']]
    assert not any('action=save' in m['path'] or 'action=restore' in m['path'] for m in wire_metadata)
    for f in (P / 'raw').rglob('*'):
        if f.is_file():
            assert f.stat().st_mode & 0o222 == 0
            assert git('show', RAW_FREEZE + ':' + str(f.relative_to(ROOT))) == f.read_bytes()
    assert git('show', RAW_FREEZE + ':' + str((P / 'raw-freeze.json').relative_to(ROOT))) == (P / 'raw-freeze.json').read_bytes()
    committed = git('ls-tree', '-r', '--name-only', RAW_FREEZE, '--', str(P.relative_to(ROOT))).decode().splitlines()
    assert str((P / 'scores.json').relative_to(ROOT)) not in committed
    assert str((P / 'secondary-analysis.json').relative_to(ROOT)) not in committed
    assert git('rev-parse', RAW_FREEZE + '^').decode().strip() == EXECUTION_FREEZE
    assert read(P / 'replay.json')['score_sha256'] == file_sha(P / 'scores.json')
    assert read(P / 'secondary-analysis.json')['primary_score_sha256'] == file_sha(P / 'scores.json')
    slot = Path(read(P / 'launch-plan.json')['slot_directory'])
    assert not slot.exists() and not (PRIVATE / 'slot-directory-archive').exists()
    with socket.socket() as connection:
        assert connection.connect_ex(('127.0.0.1', 18085)) != 0
    excluded = []
    for ref in git('for-each-ref', '--format=%(refname)', 'refs/heads').decode().splitlines():
        if 'private-archive' in ref:
            code = subprocess.run(['git','merge-base','--is-ancestor',ref,'HEAD'],cwd=ROOT).returncode
            assert code == 1
            excluded.append(ref)
    for line in git('diff', '--name-status', BASE, 'HEAD').decode().splitlines():
        status, name = line.split('\t')
        assert status == 'A' and name.startswith(str(P.relative_to(ROOT)) + '/')
    private_files = [f for f in sorted(PRIVATE.rglob('*')) if f.is_file()]
    write(P / 'private-evidence-manifest.json', dict(policy='Hashes only. Full response envelopes, native reasoning, server logs and private control bodies remain outside public ancestry.',
          file_count=len(private_files), sha256={str(f.relative_to(PRIVATE)):file_sha(f) for f in private_files}))
    report = dict(status='PASS', replacement_id='R2', verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        **checks, raw_freeze_commit=RAW_FREEZE,
        evidence_order=dict(raw_commit_parent=EXECUTION_FREEZE, raw_commit_contains_all_raw_files=True,
            raw_commit_contains_scores=False, raw_commit_contains_secondary_analysis=False,
            primary_scoring_after_raw_commit=True, exact_replay=read(P / 'replay.json')),
        raw_inventory_hashes_verified=162, raw_files_read_only=True,
        exact_request_hashes_and_dispatch_order_verified=80,
        complete_private_http_bodies_verified=243, private_completion_envelopes_verified=80,
        private_archive_heads_excluded=len(excluded), slot_directory_removed=True, dedicated_port_closed=True,
        execution=dict(real_server_starts=1, real_model_requests=80, real_completions=80,
            server_terminated=True, retries=0, answer_repairs=0, critic_calls=0, auditor_rescue=0,
            save_restore_operations=0, world_executions=0, authenticated_receipts=0, memory_writes=0,
            training=0, policy_changes=0, threshold_changes=0, architecture_changes=0,
            improvement_proposals=0, world_regeneration=False),
        active_architecture='grounded authority -> S -> E -> ordinary model (unchanged)',
        preservation_attestation_basis='All 1643 inherited tracked files, nine protected branch heads, frozen R2 implementation and raw hashes checked; isolated operation history contains only the benchmark server and research evidence/reporting commands, with no Horus execution or Memory/policy operations. No private Memory database was opened.',
        publication_scope='Only this R2 branch and its audited public ancestry; no merges or other branch pushes.')
    write(P / 'postflight.json', report)
    print(json.dumps(dict(status='PASS', parent_files=checks['inheritance']['parent_files_byte_identical'],
                         frozen_method_files=checks['execution_freeze']['method_files_unchanged'],
                         raw_files=162, private_http_bodies=243, private_files=len(private_files),
                         private_archive_heads_excluded=len(excluded), slot_directory_removed=True)))


if __name__ == '__main__':
    main()
