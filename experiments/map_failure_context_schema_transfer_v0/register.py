"""Freeze the exact contexts, requests and inherited tree before inference."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from experiments.model_proposal_role_composition_v2_replacement_r1.durable import atomic_write, file_digest
from .protocol import ROOT, PACKAGE, PARENT, CALL_LIMIT, PAIR_LIMIT, schedule, request_hash
from .fixture import Context


NEW_FILES = (
    "experiments/map_failure_context_schema_transfer_v0/README.md",
    "experiments/map_failure_context_schema_transfer_v0/__init__.py",
    "experiments/map_failure_context_schema_transfer_v0/finalize.py",
    "experiments/map_failure_context_schema_transfer_v0/fixture.py",
    "experiments/map_failure_context_schema_transfer_v0/preflight.py",
    "experiments/map_failure_context_schema_transfer_v0/protocol.py",
    "experiments/map_failure_context_schema_transfer_v0/register.py",
    "experiments/map_failure_context_schema_transfer_v0/run.py",
    "experiments/map_failure_context_schema_transfer_v0/schedule.json",
    "research/map-failure-context-schema-transfer-v0-preregistration.md",
)


def git(*args):
    return subprocess.check_output(("git", *args), cwd=ROOT, text=True).strip()


def run():
    assert git("rev-parse", "HEAD") == PARENT
    assert subprocess.run(("git", "diff", "--quiet", PARENT, "--"), cwd=ROOT).returncode == 0
    registered = []
    joint_hashes = []
    for descriptor in schedule():
        context = Context(descriptor)
        digest = request_hash(context.request)
        if descriptor["condition"] == "J":
            assert digest == descriptor["historical_request_sha256"]
            joint_hashes.append(digest)
        registered.append(dict(descriptor=descriptor, request_sha256=digest))
    assert len(registered) == CALL_LIMIT and len(set(joint_hashes)) == PAIR_LIMIT
    atomic_write(PACKAGE / "schedule.json", registered)

    parent_files = git("ls-tree", "-r", "--name-only", PARENT).splitlines()
    assert len(parent_files) == 754
    for name in NEW_FILES:
        assert (ROOT / name).is_file(), name
    names = parent_files + list(NEW_FILES)
    assert len(names) == len(set(names))
    hashes = {name: file_digest(ROOT / name) for name in names}
    registration = dict(
        frozen_before_inference=True,
        parent=PARENT,
        parent_tree=git("rev-parse", f"{PARENT}^{{tree}}"),
        parent_files=len(parent_files),
        registered_contexts=PAIR_LIMIT,
        registered_calls=CALL_LIMIT,
        historical_context_numbers=[2, 3, 5, 7, 8, 9, 10, 27, 30, 32, 33],
        historical_joint_request_hashes_reproduced=joint_hashes,
        schedule_sha256=hashlib.sha256((PACKAGE / "schedule.json").read_bytes()).hexdigest(),
        sha256=hashes,
    )
    atomic_write(PACKAGE / "frozen-inputs.json", registration)
    print(json.dumps({key: registration[key] for key in (
        "parent", "parent_tree", "parent_files", "registered_contexts",
        "registered_calls", "historical_context_numbers", "schedule_sha256")}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.parse_args()
    run()
