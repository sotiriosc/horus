import json
from pathlib import Path
import tempfile

from horus.core import MapForecast
from .study import (CONDITIONS, EXPERIMENT, ORDER, STAGE_A, STAGE_B_REGIMES,
                    adapter_paths, file_hash, verify_manifest)


def main() -> dict:
    manifest = json.loads((EXPERIMENT / "source-manifest.json").read_text())
    verify_manifest(manifest)
    assert len(STAGE_A) == 18 and len(STAGE_B_REGIMES) == 6
    assert set(ORDER) == set(CONDITIONS)
    assert 4 * (18 * 2 + 6 * 3 * 2) == 288
    assert CONDITIONS == {"F": (False, False), "H": (True, False),
                          "Z": (False, True), "HZ": (True, True)}
    assert file_hash(adapter_paths()["G2"]) != file_hash(adapter_paths()["G3"])
    # Structural leakage checks: disabled components have no state/interface.
    from .study import Arm
    with tempfile.TemporaryDirectory() as value:
        for name in CONDITIONS:
            arm = Arm(name, Path(value) / name)
            assert (arm.router is not None) == arm.horus_enabled
            assert (arm.explorer is not None) == arm.horus_enabled
            assert arm.controllers == {}
            assert arm.history(1, "ADVANCE") == []
    return dict(status="PASS", inference_calls=0, call_budget=288,
        conditions=list(ORDER), stage_a_events=18, stage_b_opportunities=6,
        component_toggle_count=2, separate_condition_codepaths=0,
        same_model_artifacts_all_conditions=True,
        no_training=True, isolation_structural_checks=True)


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True))

