#!/usr/bin/env python3
"""Clone completed v0.8 private state and run one bounded v0.9 campaign."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from horus.capability_gap import (initialize_capability_gap_registry,
                                  run_capability_gap_campaign)
from horus.live import ModelClient, _now
from horus.relation_routing import relation_routed_clients


def append(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("a") as stream:
        stream.write(json.dumps(value,sort_keys=True)+"\n"); stream.flush(); os.fsync(stream.fileno())


def tree_commitment(root: Path) -> str:
    rows=[]
    for path in sorted(p for p in root.rglob("*") if p.is_file() and not p.name.startswith(".lock")):
        rows.append((str(path.relative_to(root)),hashlib.sha256(path.read_bytes()).hexdigest()))
    return hashlib.sha256(json.dumps(rows,separators=(",",":"),sort_keys=True).encode()).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-session",type=Path,required=True)
    parser.add_argument("--source-registry",type=Path,required=True)
    parser.add_argument("--source-report",type=Path,required=True)
    parser.add_argument("--session",type=Path,required=True)
    parser.add_argument("--registry",type=Path,required=True)
    parser.add_argument("--progress",type=Path,required=True)
    parser.add_argument("--artifact",type=Path,required=True)
    args=parser.parse_args()
    for path in (args.session,args.registry,args.progress,args.artifact):
        if path.exists(): raise SystemExit(f"fresh destination required: {path.name}")
    source_before=dict(session=tree_commitment(args.source_session),
                       registry=tree_commitment(args.source_registry))
    shutil.copytree(args.source_session,args.session)
    shutil.copytree(args.source_registry,args.registry)
    append(args.progress,dict(started_at=_now(),identity="HORUS_CAPABILITY_GAP_DETECTION_V0",
        source_before=source_before,source_attempts=54,source_receipts=50,
        maximum_new_decisions=12,maximum_new_model_calls=108))
    initialize_capability_gap_registry(args.registry,args.source_report)
    specialists,_=relation_routed_clients(args.registry,device="cuda")
    artifact=run_capability_gap_campaign(args.session,args.registry,
        joint_client=ModelClient(),specialist_clients=specialists)
    args.artifact.write_text(json.dumps(artifact,indent=2,sort_keys=True)+"\n")
    source_after=dict(session=tree_commitment(args.source_session),
                      registry=tree_commitment(args.source_registry))
    if source_after!=source_before: raise RuntimeError("v0.8 source changed")
    append(args.progress,dict(finished_at=_now(),campaign_complete=True,
        new_decisions=artifact["new_decisions"],new_model_calls=artifact["new_model_calls"],
        terminal_classification=artifact["terminal_classification"],
        source_after=source_after,source_unchanged=True))
    return 0


if __name__=="__main__": raise SystemExit(main())
