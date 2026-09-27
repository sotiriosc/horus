#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""Execute public checks in a fresh work directory; keep measured logs and hashes."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
FAILURE = re.compile(r"(?im)^\s*(?:FAIL(?:ED)?\b(?!\s*:\s*0\b)|FATAL\b|ERROR\b)|\b[1-9]\d*\s+(?:failures|mismatches)\b|\bfails\s*=\s*[1-9]|\bFAIL\s*:\s*[1-9]")


def validate_output(text: str, required: tuple[str, ...], simulation: bool = False) -> None:
    if simulation and FAILURE.search(text):
        raise RuntimeError("simulation reported a failure even if its exit code was zero")
    for pattern in required:
        if not re.search(pattern, text, re.MULTILINE):
            raise RuntimeError(f"execution did not produce required evidence: {pattern}")


class Checks:
    def __init__(self, output: Path):
        self.output = output
        self.work = output / "work"
        self.logs = output / "logs"
        self.logs.mkdir()
        self.work.mkdir()
        # Only source directories are copied. Prior generated outputs never seed a run.
        for folder in ("rtl", "tb", "sim", "tests", "experiments", "research", "docs", "scripts"):
            if (ROOT / folder).exists():
                shutil.copytree(ROOT / folder, self.work / folder,
                                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", *(
                                    ("*.csv", "*.json", "*.hex", "*.dat", "*.npz", "*.png", "*.txt", "*.log", "*.vcd", "run_*", "sim_*")
                                    if folder == "sim" else ())))
        self.env = os.environ.copy()
        self.env.pop("PYTHONOPTIMIZE", None)
        self.env.update(PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="2", MKL_NUM_THREADS="2",
                        MPLCONFIGDIR=str(output / "matplotlib"))
        self.results = []
        self.index = 0
        self.liberty = None

    def command(self, name, args, *, cwd="sim", required=(), simulation=False, timeout=180):
        self.index += 1
        logfile = self.logs / f"{self.index:02d}-{name}.log"
        row = dict(name=name, command=args, cwd=cwd, log=str(logfile.relative_to(self.output)), status="FAIL")
        start = time.monotonic()
        try:
            with logfile.open("w") as stream:
                result = subprocess.run(args, cwd=self.work / cwd, env=self.env,
                                        stdout=stream, stderr=subprocess.STDOUT, timeout=timeout)
            row["returncode"] = result.returncode
            if result.returncode:
                raise RuntimeError(f"command exited {result.returncode}")
            validate_output(logfile.read_text(errors="replace"), tuple(required), simulation)
            row["status"] = "PASS"
        except (OSError, subprocess.TimeoutExpired, RuntimeError) as exc:
            row["error"] = str(exc)
            raise
        finally:
            row["seconds"] = round(time.monotonic() - start, 3)
            self.results.append(row)
            (self.output / "checks.json").write_text(json.dumps(self.results, indent=2) + "\n")
            print(f"{row['status']} {name}", flush=True)

    def py(self, name, script, *args, cwd="sim", required=(), timeout=180):
        self.command(name, [sys.executable, script, *args], cwd=cwd, required=required, timeout=timeout)

    def rtl(self, name, bench, modules, *, defines=(), plus=(), required=(r"\bPASS",)):
        executable = "run_" + name
        args = ["iverilog", "-g2012", "-Wall", *["-D" + d for d in defines], "-o", executable,
                "../tb/" + bench + ".v", *["../rtl/" + m + ".v" for m in modules]]
        self.command(name + "-compile", args)
        self.command(name, ["vvp", executable, *plus], required=required, simulation=True)

    def synthesis(self, script):
        if self.liberty is None:
            result = subprocess.run(["bash", "find_sky130_liberty.sh"], cwd=self.work / "sim",
                                    capture_output=True, text=True, check=True)
            self.liberty = Path(result.stdout.strip())
            if not self.liberty.is_file():
                raise RuntimeError("Set SKY130_HD_LIB to an installed Sky130 HD liberty file")
            (self.output / "synthesis-input.json").write_text(json.dumps({
                "library_name": self.liberty.name,
                "library_sha256": hashlib.sha256(self.liberty.read_bytes()).hexdigest()}, indent=2) + "\n")
        source = self.work / "sim" / script
        generated = self.work / "sim" / ("run_" + script)
        generated.write_text(source.read_text().replace("@LIBERTY@", str(self.liberty)))
        self.command(script.removesuffix(".ys"), ["yosys", "-Q", generated.name], required=(r"Chip area",))

    def keeper(self):
        self.command("keeper-compile", ["iverilog", "-g2012", "-o", "run_keeper-rtl", "../tb/tb_skpr.v", "../rtl/skpr.v"])
        self.py("keeper-cosimulation", "test_scale_keeper.py", "--with-rtl", "--rtl-vvp", "run_keeper-rtl",
                "--outdir", "keeper_results", required=(r"RTL vs golden mismatches:\s*0", r"Determinism.*0 mismatches"))

    def core(self):
        for name, bench, modules in [
            ("nfe", "tb_horus_nfe", ["horus_nfe"]),
            ("pgate", "tb_horus_pgate_ctrl", ["horus_pgate_ctrl"]),
            ("router", "tb_horus_router", ["horus_router"]),
            ("wrapper", "tb_horus_nfe_wrapper", ["horus_nfe_wrapper", "horus_nfe"]),
            ("mesh", "tb_horus_mesh_top", ["horus_nfe", "horus_pgate_ctrl", "horus_system", "horus_router", "horus_mesh_top"]),
        ]:
            required = (r"ALL.*(?:PASSED|PASS)",)
            if name == "nfe":
                required = (r"Test 1.5\*1.5: Result E=33 .*f=\s*8", r"Test Max:.*Result E=33 .*f=62", r"Test UF:.*Result=0\s+underflow=1", r"SUB G-B Cy2: Result=\{S=0 E=30\(stored\) f=8\}")
            self.rtl(name, bench, modules, required=required)
        for name, module in [("format-codecs", "format_zoo"), ("compact-codecs", "compact_nfe")]:
            self.command(name, [sys.executable, "-c", f"import {module}; {module}.run_unit_tests()"], required=(r"PASS",))
        self.py("tile-model", "tile_model.py", required=(r"ALL TESTS PASSED",))
        for fixture in (self.work / "tests/fixtures/tile").glob("*.hex"):
            shutil.copy2(fixture, self.work / "sim" / fixture.name)
        common = ["fp8_e4m3_mul", "horus_e3m6_core"]
        self.rtl("tile", "tb_horus_tile", ["horus_tile", *common, "horus_norm_v2", "skpr_block_detect"], required=(r"2258 tests, 0 failures",))
        self.py("tile-v2-goldens", "tile_v2_golden.py")
        self.rtl("tile-v2", "tb_horus_tile_v2", ["horus_tile_v2", *common], required=(r"2005 tests, 0 failures",))
        self.py("detector-vectors", "skpr_golden.py", "--emit", "skpr_vectors.csv", "--T", "13", "--n_rand", "20000")
        self.rtl("detector", "tb_skpr_block_detect", ["skpr_block_detect"], plus=("+VECTORS=skpr_vectors.txt",), required=(r"DETECT SIDECAR PASS",))
        self.rtl("alignment", "tb_tile_skpr_align", ["horus_tile_skpr", "horus_tile", *common, "horus_norm_v2", "skpr_block_detect", "skpr"])
        self.py("recovery-model", "tile_skpr_recovery_arc.py", "--out", "TILE_SKPR_RECOVERY.csv", "--json", "TILE_SKPR_RECOVERY_SUMMARY.json", "--stim", "tile_skpr_recovery_stim.txt", required=(r"PASS_B_JUSTIFIES_DETECT",))
        self.rtl("recovery", "tb_tile_skpr_recovery", ["horus_block_skpr", "horus_norm_v2", "skpr_block_detect", "skpr"], plus=("+STIM=tile_skpr_recovery_stim.txt",))
        self.rtl("repair", "tb_skpr_block_repair", ["skpr_block_repair"])
        self.rtl("transaction", "tb_horus_tile_skpr_repair", ["horus_block_skpr_repair", "skpr_block_detect_rr", "skpr_block_repair", "horus_norm_v2", "skpr"])
        self.py("jacobi-operands", "jacobi_rtl_golden.py")
        self.py("mac-goldens", "scaling_mac_golden.py")
        for width in (32, 34, 36):
            self.rtl(f"mac-{width}", "tb_scaling_mac", ["horus_e3m6_mac_param", f"horus_e3m6_mac_w{width}"], defines=(f"ACC_W{width}",), required=(rf"PASS  tb_scaling_mac W{width}",))
        self.py("array-goldens", "scaling_array_golden.py")
        for size in (2, 4):
            self.rtl(f"array-{size}", "tb_scaling_array", [f"horus_array_{size}x{size}", "horus_tile_v2", *common], defines=(f"ARRAY_{size}X{size}",), required=(r"PASS  tb_scaling_array",))
        self.command("normalizer-goldens", [sys.executable, "-c", "import expnorm_sweep; expnorm_sweep.gen_golden_csv('EXPNORM_GOLDEN.csv')"])
        self.rtl("normalizer", "tb_horus_norm", ["horus_norm", "horus_nfe"], required=(r"OVERALL: ALL TESTS PASSED",))
        self.keeper()
        self.py("bitexact", "tests/test_horus_bitexact.py", cwd=".", required=(r'"verdict": "PASS"',))
        self.py("bitexact-alias", "tests/test_skpr_rule5_equivalence.py", cwd=".", required=(r'"verdict": "PASS"',))
        self.command("structured-tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_structured_output_controller.py", "-v"], cwd=".", required=(r"Ran 9 tests", r"^OK$"))
        self.py("structured-scenarios", "experiments/structured_output/evaluate_structured_output_controller.py", "--results", "structured-evaluation.json", cwd=".", required=(r"pass_rate=7/7",))
        self.command("runner-tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_public_runner.py", "-v"], cwd=".", required=(r"^OK$",))

    def experiments(self):
        self.py("mlp-train", "mlp_train.py")
        self.command("normalizer-goldens", [sys.executable, "-c", "import expnorm_sweep; expnorm_sweep.gen_golden_csv('EXPNORM_GOLDEN.csv')"])
        self.py("normalizer-v2-goldens", "expnorm_sweep.py", "--v2-golden")
        self.rtl("normalizer-v2", "tb_horus_norm_v2", ["horus_norm_v2"], required=(r"7 PASS, 0 FAIL",))
        self.py("mlp-python", "mlp_infer_nfe.py")
        self.rtl("mlp-rtl", "tb_mlp_inference", ["horus_nfe", "horus_norm_v2"], required=(r"360",))
        self.py("mlp-comparison", "analyze_mlp.py", required=(r"PREDICTIONS EXACT \(360/360\)",))
        self.py("hopfield-python", "hopfield_demo.py")
        self.rtl("hopfield-rtl", "tb_hopfield_recall", ["horus_nfe"], required=(r"Total exact recalls: 120 / 120",))
        self.py("hopfield-comparison", "analyze_hopfield.py", required=(r"Divergent iterations:\s*0",))
        self.rtl("feedback", "tb_second_source_chain", ["horus_nfe"], required=(r"SSC_CHAIN_TRACE.csv",))
        self.py("feedback-analysis", "analyze_second_source_chain.py", required=(r"P1.*NOT CONFIRMED", r"P2.*CONFIRMED", r"P3.*CONFIRMED"))
        self.py("normalization-sweep", "norm_interval_sweep.py", required=(r"largest passing k = 128", r"largest passing k = 8"))
        self.rtl("normalization-rtl", "tb_norm_interval", ["horus_nfe"], required=(r"CONFIRMED.*k=128", r"CONFIRMED.*PI k=8"))
        self.py("jacobi-operands", "jacobi_rtl_golden.py")
        self.py("jacobi-model", "jacobi_mac_model.py", required=(r"converged: 200/200", r"R2 PASS: True"))
        self.rtl("jacobi-rtl", "tb_jacobi_mac", ["horus_e3m6_mac"], required=(r"38408/38408", r"23333/23333"))
        self.py("blockfp", "blockfp_test.py", required=(r"E0M6\+block.*K1 FAIL", r"E0M9\+block.*K1 PASS"))

    def synth(self):
        for script in ("synth_horus_e3m6_mac.ys", "synth_horus_e3m6_acc_baseline.ys", "synth_blockfp_mul7.ys", "synth_blockfp_mul10.ys"):
            self.synthesis(script)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite", choices=("core", "experiments", "synthesis", "keeper", "all"))
    parser.add_argument("--output", type=Path, help="new output directory; defaults to a fresh system temporary directory")
    args = parser.parse_args()
    if args.output:
        output = args.output.resolve()
        # An existing directory is never overwritten or recursively copied into itself.
        output.mkdir(parents=True, exist_ok=False)
    else:
        output = Path(tempfile.mkdtemp(prefix="horus-checks-"))
    if ROOT == output or ROOT in output.parents:
        # Outputs under the repository are supported only outside copied source directories.
        if output.relative_to(ROOT).parts[0] in {"rtl", "tb", "sim", "tests", "experiments", "research", "docs", "scripts"}:
            raise SystemExit("Choose an output directory outside source directories")
    source_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for folder in ("rtl", "tb", "sim", "tests", "experiments", "research", "docs", "scripts")
                     for p in (ROOT / folder).rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    packages = {}
    for package in ("numpy", "scipy", "scikit-learn", "matplotlib"):
        try:
            packages[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            packages[package] = None
    provenance = dict(suite=args.suite, python=sys.version, packages=packages, source_sha256=source_hashes, status="RUNNING")
    (output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(f"Output: {output}", flush=True)
    try:
        checks = Checks(output)
        for suite in (("core", "experiments", "synthesis") if args.suite == "all" else (args.suite,)):
            getattr(checks, "synth" if suite == "synthesis" else suite)()
    except (OSError, subprocess.SubprocessError, RuntimeError) as exc:
        provenance.update(status="FAIL", error=str(exc))
        print(f"FAIL: {exc}; inspect {output}", file=sys.stderr)
        return 1
    else:
        provenance["status"] = "PASS"
        print(f"PASS: {len(checks.results)} executed steps; evidence at {output}")
        return 0
    finally:
        (output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
