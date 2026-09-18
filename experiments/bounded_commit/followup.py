#!/usr/bin/env python3
"""Separately labeled broader-fault and lossless trace-compaction follow-up."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
from run import run, HERE, ROOT, DUT, NEW


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='horus-commit-followup-'))
    if out.resolve().is_relative_to(ROOT):
        raise ValueError('Keep artifacts outside source')
    if args.output:
        out.mkdir(parents=True, exist_ok=False)
    run(['iverilog', '-g2012', '-s', 'tb_broader', '-o', out / 'broader',
         *NEW, HERE / 'tb_broader.v', *DUT], out / 'compile-broader.log')
    rows = []
    for seed in (1, 2, 3):
        for pattern in range(9):
            text = run(['vvp', out / 'broader', f'+SEED={seed}', f'+PATTERN={pattern}'],
                       out / f'broader-{seed}-{pattern}.log', 'BROADER PASS')
            row = next(line for line in text.splitlines() if line.startswith('BROADER seed='))
            rows.append({k: int(v) for k, v in (x.split('=') for x in row.split()[1:])})
    # Bit-for-bit comparison of every decision record and metric, across all
    # original schedules; the same test also reads back the eight stored slots.
    for width in (96, 63):
        run(['iverilog', '-g2012', '-s', 'tb_campaign',
             f'-Ptb_campaign.TRACE_BITS={width}', '-o', out / f'trace-{width}',
             *NEW, HERE / 'tb_campaign.v', *DUT], out / f'compile-trace-{width}.log')
    for seed in (1, 2, 3):
        for mode in range(7):
            outputs = []
            for width in (96, 63):
                outputs.append(run(['vvp', out / f'trace-{width}', f'+SEED={seed}', f'+MODE={mode}'],
                                   out / f'trace-{width}-{seed}-{mode}.log', 'CAMPAIGN PASS'))
            if outputs[0] != outputs[1]:
                raise RuntimeError('Trace compaction changed observable decisions')
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in [*NEW, *DUT, *HERE.glob('tb_*.v'), Path(__file__)]}
    (out / 'followup.json').write_text(json.dumps({
        'broader_faults': rows, 'compact_trace': '21 paired schedules: bit-identical outputs and retained ring',
        'source_sha256': hashes, 'status': 'PASS'}, indent=2) + '\n')
    print(f'FOLLOWUP PASS: 2700 broader-fault transactions; 21 paired trace comparisons. {out}')


if __name__ == '__main__':
    main()
