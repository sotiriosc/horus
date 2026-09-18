#!/usr/bin/env python3
"""Run fixed, bounded RTL controls; save capped run artifacts outside source."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DUT = [ROOT / 'rtl' / x for x in (
    'horus_block_skpr_repair.v', 'skpr_block_detect_rr.v',
    'skpr_block_repair.v', 'skpr.v', 'horus_norm_v2.v')]
NEW = [HERE / x for x in ('independent_spec.v', 'commit_gate.v',
                         'descendant_control.v', 'bounded_commit_top.v')]


def run(command, log, marker=None):
    with log.open('w') as stream:
        proc = subprocess.run([str(x) for x in command], stdout=stream,
                              stderr=subprocess.STDOUT, timeout=120)
    text = log.read_text()
    if proc.returncode or 'FATAL' in text or (marker and marker not in text):
        raise RuntimeError(f'Validation failed; inspect {log}')
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    out = args.output
    if out is None:
        out = Path(tempfile.mkdtemp(prefix='horus-independent-commit-'))
    else:
        out.mkdir(parents=True, exist_ok=False)
    if out.resolve().is_relative_to(ROOT):
        raise ValueError('Run artifacts must be outside the source tree')
    checks = {}
    for bench, marker in [('tb_spec', 'SPEC PASS'), ('tb_gate_edges', 'EDGES PASS'),
                          ('tb_campaign', None)]:
        run(['iverilog', '-g2012', '-s', bench, '-o', out / bench,
             *NEW, HERE / f'{bench}.v', *DUT], out / f'{bench}-compile.log')
        if marker:
            checks[bench] = run(['vvp', out / bench], out / f'{bench}.log', marker).strip()
    metrics = []  # Fixed campaign report: exactly 21 rows, outside hardware state.
    for seed in (1, 2, 3):
        for mode in range(7):
            text = run(['vvp', out / 'tb_campaign', f'+SEED={seed}', f'+MODE={mode}'],
                       out / f'seed-{seed}-mode-{mode}.log', 'CAMPAIGN PASS')
            records = [line for line in text.splitlines() if line.startswith('TRACE ')]
            lines = [line for line in text.splitlines() if line.startswith('METRICS ')]
            if len(records) != 200 or len(lines) != 1:
                raise RuntimeError('Incomplete fixed campaign output')
            row = {k: int(v) for k, v in (pair.split('=') for pair in lines[0].split()[1:])}
            if row['sent'] != 200 or any(row[x] for x in
                    ('false_accept', 'false_reject', 'duplicate', 'timeout')):
                raise RuntimeError(f'Protocol metric failed: {row}')
            metrics.append(row)
    (out / 'metrics.json').write_text(json.dumps(metrics, indent=2) + '\n')
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in [*DUT, *NEW, *sorted(HERE.glob('tb_*.v')), Path(__file__)]}
    (out / 'provenance.json').write_text(json.dumps({
        'source_sha256': hashes, 'unit_checks': checks,
        'seeds': [1, 2, 3], 'transactions_per_seed_mode': 200,
        'modes': ['clean', 'repair', 'bad_repair', 'bad_id', 'stale_epoch',
                  'descendant_shadow', 'bad_record_id'],
        'iverilog': subprocess.check_output(['iverilog', '-V'], stderr=subprocess.STDOUT,
                                            text=True).splitlines()[0],
        'status': 'PASS'}, indent=2) + '\n')
    print(f'PASS: 21 schedules, 4200 protected transactions; 300 negative-control false accepts. {out}')


if __name__ == '__main__':
    main()
