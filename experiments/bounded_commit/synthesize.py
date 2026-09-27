#!/usr/bin/env python3
"""Bounded optional synthesis. No private files or network dependencies."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
from run import HERE, ROOT, DUT, NEW


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--liberty', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--followup', action='store_true')
    args = parser.parse_args()
    liberty = args.liberty.resolve(strict=True)
    out = args.output or Path(tempfile.mkdtemp(prefix='horus-commit-synthesis-'))
    if args.output:
        out.mkdir(parents=True, exist_ok=False)
    if out.resolve().is_relative_to(ROOT):
        raise ValueError('Keep synthesis artifacts outside source')
    def quoted(path):
        return '"' + str(path).replace('\\', '\\\\').replace('"', '\\"') + '"'
    results = []
    builds = [
            ('checker', 'independent_spec', ''),
            ('gate_without_trace', 'commit_gate', 'chparam -set KEEP_TRACE 0 commit_gate'),
            ('gate_with_trace', 'commit_gate', ''),
            ('integrated', 'bounded_commit_top', ''),
            ('original_wrapper_all_ports', 'horus_block_skpr_repair', '')]
    if args.followup:
        builds = [
            ('protected_record_probe', 'evidence_bank', ''),
            ('quarantine_probe', 'quarantine_bank', ''),
            ('identity_probe', 'identity_comparators', ''),
            ('gate_compact_trace', 'commit_gate', 'chparam -set TRACE_BITS 63 commit_gate'),
            ('followup_integrated', 'bounded_commit_top', '')]
    for label, top, parameters in builds:
        script = '\n'.join([
            'read_verilog ' + ' '.join(quoted(x) for x in [*NEW, *DUT, HERE / 'cost_components.v']),
            parameters, f'synth -top {top} -flatten',
            f'dfflibmap -liberty {quoted(liberty)}',
            f'abc -liberty {quoted(liberty)}', 'clean',
            f'stat -liberty {quoted(liberty)}',
            f'write_json {quoted(out / (label + ".json"))}'])
        (out / f'{label}.ys').write_text(script + '\n')
        with (out / f'{label}.log').open('w') as log:
            proc = subprocess.run(['yosys', '-s', str(out / f'{label}.ys')],
                                  stdout=log, stderr=subprocess.STDOUT, timeout=180)
        if proc.returncode:
            raise RuntimeError(f'Synthesis failed: {label}')
        log = (out / f'{label}.log').read_text()
        areas = re.findall(r'Chip area for (?:top )?module.*?:\s*([0-9.]+)', log)
        if not areas:
            raise RuntimeError('Missing mapped area')
        netlist = json.loads((out / f'{label}.json').read_text())['modules'][top]
        cells = netlist['cells']
        flops = sum('df' in cell['type'].split('__')[-1] for cell in cells.values())
        unmapped = sorted({cell['type'] for cell in cells.values()
                           if not cell['type'].startswith('sky130_fd_sc_hd__')})
        if unmapped:
            raise RuntimeError(f'Unmapped cells: {unmapped}')
        results.append({'label': label, 'area_um2': float(areas[-1]),
                        'mapped_cells': len(cells), 'mapped_flops': flops})
    (out / 'resources.json').write_text(json.dumps({
        'results': results, 'liberty_name': liberty.name,
        'liberty_sha256': hashlib.sha256(liberty.read_bytes()).hexdigest(),
        'yosys': subprocess.check_output(['yosys', '-V'], text=True).strip(),
        'timing': 'Not measured: mapped cell area is not STA or routed timing.',
        'comparison': 'Standalone gate is the added authorization primitive. '
                      'Original wrapper has different observable ports; integrated '
                      'minus original is not a controlled incremental-area estimate.',
    }, indent=2) + '\n')
    print(json.dumps(results, indent=2))
    print(f'Synthesis complete: {out}')


if __name__ == '__main__':
    main()
