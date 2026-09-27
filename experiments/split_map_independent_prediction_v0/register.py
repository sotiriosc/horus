"""Freeze exact contexts, prompts, requests, schedule, and inherited tree."""
import hashlib
import json
import subprocess

from experiments.model_proposal_role_composition_v2_replacement_r1.durable import atomic_write, file_digest
from .protocol import (ROOT, PACKAGE, PARENT, CALL_LIMIT, CONTEXT_LIMIT,
    contexts, request_hash, matched)
from .fixture import Context


NEW_FILES = (
    "experiments/split_map_independent_prediction_v0/README.md",
    "experiments/split_map_independent_prediction_v0/__init__.py",
    "experiments/split_map_independent_prediction_v0/finalize.py",
    "experiments/split_map_independent_prediction_v0/fixture.py",
    "experiments/split_map_independent_prediction_v0/preflight.py",
    "experiments/split_map_independent_prediction_v0/protocol.py",
    "experiments/split_map_independent_prediction_v0/register.py",
    "experiments/split_map_independent_prediction_v0/run.py",
    "experiments/split_map_independent_prediction_v0/schedule.json",
    "research/split-map-independent-prediction-v0-preregistration.md",
)


def git(*args):
    return subprocess.check_output(("git", *args), cwd=ROOT, text=True).strip()


def run():
    assert git("rev-parse", "HEAD") == PARENT
    assert subprocess.run(("git", "diff", "--quiet", PARENT, "--"), cwd=ROOT).returncode == 0
    registered = []
    historical_hashes = []
    for descriptor in contexts():
        context = Context(descriptor)
        checks = matched(context.requests, descriptor)
        assert checks["passed"]
        for role in descriptor["call_order"]:
            digest = request_hash(context.requests[role])
            if role == "J":
                assert digest == descriptor["historical_request_sha256"]
                historical_hashes.append(digest)
            registered.append(dict(call_index=len(registered),
                context_index=descriptor["index"],
                historical_context_number=descriptor["historical_context_number"],
                role=role, seed=descriptor["seed"], request_sha256=digest,
                descriptor_sha256=hashlib.sha256(json.dumps(descriptor, sort_keys=True).encode()).hexdigest()))
    assert len(registered) == CALL_LIMIT and len(historical_hashes) == CONTEXT_LIMIT
    atomic_write(PACKAGE / "schedule.json", registered)

    parent_files = git("ls-tree", "-r", "--name-only", PARENT).splitlines()
    for name in NEW_FILES:
        assert (ROOT / name).is_file(), name
    names = parent_files + list(NEW_FILES)
    assert len(names) == len(set(names))
    hashes = {name: file_digest(ROOT / name) for name in names}
    registration = dict(
        frozen_before_inference=True, parent=PARENT,
        parent_tree=git("rev-parse", f"{PARENT}^{{tree}}"), parent_files=len(parent_files),
        registered_contexts=CONTEXT_LIMIT, registered_calls=CALL_LIMIT,
        historical_context_numbers=[row["historical_context_number"] for row in contexts()],
        historical_joint_request_hashes_reproduced=historical_hashes,
        schedule_sha256=file_digest(PACKAGE / "schedule.json"), sha256=hashes)
    atomic_write(PACKAGE / "frozen-inputs.json", registration)
    print(json.dumps({key: registration[key] for key in (
        "parent", "parent_tree", "parent_files", "registered_contexts",
        "registered_calls", "historical_context_numbers", "schedule_sha256")}, sort_keys=True))


if __name__ == "__main__":
    run()
