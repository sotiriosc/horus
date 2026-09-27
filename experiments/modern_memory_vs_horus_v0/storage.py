from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import time

from horus.core import MAPPING, digest


SCHEMA_VERSION = 1


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def file_hash(path: Path) -> str:
    h = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass(frozen=True)
class Retrieval:
    relation: str
    candidate_count: int
    selected: tuple[dict, ...]
    selected_identities: tuple[str, ...]
    reasons: tuple[str, ...]
    chronological_positions: tuple[int, ...]
    candidate_consequences: tuple[int, ...]
    selected_consequences: tuple[int, ...]
    contradictions_in_candidates: bool
    contradictions_included: bool
    contradictions_excluded: bool
    retrieval_seconds: float


class ModernMemory:
    """Append-only authenticated evidence with the frozen modern retrieval rule."""
    def __init__(self, path: Path, create: bool):
        self.path = path.resolve()
        if create and self.path.exists():
            raise RuntimeError("durable store already exists")
        if not create and not self.path.is_file():
            raise RuntimeError("durable store missing")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=DELETE")
        self.db.execute("PRAGMA synchronous=FULL")
        if create:
            self.db.executescript("""
            CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE events(
              chronological_order INTEGER PRIMARY KEY,
              event_identity TEXT NOT NULL UNIQUE,
              source_identity TEXT NOT NULL,
              event_id INTEGER NOT NULL,
              epoch INTEGER NOT NULL,
              transaction_id INTEGER NOT NULL,
              pre_state INTEGER NOT NULL,
              relation TEXT NOT NULL,
              action TEXT NOT NULL,
              realized_consequence INTEGER NOT NULL,
              realized_next_state INTEGER NOT NULL,
              receipt_provenance_sha256 TEXT NOT NULL,
              authorization_status TEXT NOT NULL CHECK(authorization_status='AUTHORIZED'),
              authorization_identity TEXT NOT NULL,
              context_identifier TEXT NOT NULL,
              event_stream_sequence INTEGER NOT NULL UNIQUE,
              event_stream_head_sha256 TEXT NOT NULL UNIQUE
            );
            CREATE INDEX events_relation_order ON events(relation, chronological_order);
            """)
            self.db.execute("INSERT INTO metadata VALUES('schema_version', ?)",
                            (str(SCHEMA_VERSION),))
            self.db.commit()
        row = self.db.execute("SELECT value FROM metadata WHERE key='schema_version'").fetchone()
        if row is None or row[0] != str(SCHEMA_VERSION):
            raise RuntimeError("durable memory schema mismatch")

    def close(self): self.db.close()
    def __enter__(self): return self
    def __exit__(self, *_): self.close()

    def rows(self, relation: str | None = None) -> list[dict]:
        if relation is None:
            query, values = "SELECT * FROM events ORDER BY chronological_order", ()
        else:
            query, values = ("SELECT * FROM events WHERE relation=? "
                             "ORDER BY chronological_order"), (relation,)
        return [dict(row) for row in self.db.execute(query, values)]

    def record(self, store, event_envelope: dict, context_identifier: str) -> dict:
        if not store.records["events"] or event_envelope is not store.records["events"][-1]:
            raise RuntimeError("event is not current authenticated publication")
        event, receipt = event_envelope["record"], event_envelope["record"].get("receipt", {})
        if event.get("authorization_status") != "AUTHORIZED":
            raise RuntimeError("unauthorized evidence cannot enter durable memory")
        identity_tuple = (receipt.get("source_identity"), receipt.get("event_id"),
                          receipt.get("epoch"), receipt.get("transaction_id"))
        if tuple(event.get("receipt_identity", ())) != identity_tuple:
            raise RuntimeError("receipt identity mismatch")
        if digest(receipt) != event.get("receipt_provenance_sha256"):
            raise RuntimeError("receipt provenance mismatch")
        memory = event.get("memory_record", {})
        pairs = (("epoch", "epoch"), ("transaction_id", "transaction_id"),
                 ("pre_state", "pre_state"), ("action", "action"),
                 ("next_state", "next_state"), ("consequence", "realized_consequence"))
        if any(memory.get(m) != receipt.get(r) for m, r in pairs):
            raise RuntimeError("authorized Memory/receipt mismatch")
        identity = canonical(event["receipt_identity"])
        order = len(store.records["events"])
        relation = f'{receipt["pre_state"]}:{receipt["action"]}'
        head = sha256(canonical(event_envelope).encode()).hexdigest()
        authorization_identity = canonical([
            event["authorization_status"], memory.get("pair_decision_id"),
            event_envelope["sequence"]])
        with self.db:
            self.db.execute("INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (order, identity, receipt["source_identity"], receipt["event_id"],
                 receipt["epoch"], receipt["transaction_id"], receipt["pre_state"],
                 relation, receipt["action"], receipt["realized_consequence"],
                 receipt["next_state"], event["receipt_provenance_sha256"],
                 event["authorization_status"], authorization_identity,
                 context_identifier, event_envelope["sequence"], head))
        return dict(order=order, event_identity=identity, relation=relation,
                    event_stream_head_sha256=head)

    def retrieve(self, relation: str, limit: int = 6) -> Retrieval:
        started = time.perf_counter()
        rows = self.rows(relation)
        selected, reasons = [], {}
        for row in reversed(rows[-4:]):
            selected.append(row); reasons[row["event_identity"]] = "RECENT_EXACT_RELATION"
        represented = {row["realized_consequence"] for row in selected}
        for value in sorted({row["realized_consequence"] for row in rows} - represented):
            row = next(item for item in reversed(rows)
                       if item["realized_consequence"] == value)
            if row not in selected and len(selected) < limit:
                selected.append(row); reasons[row["event_identity"]] = "CONTRADICTION_ANCHOR"
        for row in reversed(rows):
            if row not in selected and len(selected) < limit:
                selected.append(row); reasons[row["event_identity"]] = "RECENCY_FILL"
        selected.sort(key=lambda row: row["chronological_order"])
        candidates = tuple(row["realized_consequence"] for row in rows)
        chosen = tuple(row["realized_consequence"] for row in selected)
        contradiction = len(set(candidates)) > 1
        return Retrieval(relation, len(rows), tuple(self._public(row) for row in selected),
            tuple(row["event_identity"] for row in selected),
            tuple(reasons[row["event_identity"]] for row in selected),
            tuple(row["chronological_order"] for row in selected), candidates, chosen,
            contradiction, len(set(chosen)) > 1,
            contradiction and len(set(chosen)) <= 1, time.perf_counter() - started)

    @staticmethod
    def _public(row: dict) -> dict:
        alias = next(key for key, action in MAPPING.items() if action == row["action"])
        return dict(epoch=row["epoch"], transaction_id=row["transaction_id"],
            surface_action=alias, next_state=row["realized_next_state"],
            consequence=row["realized_consequence"], memory_identity=row["event_identity"],
            chronological_order=row["chronological_order"])

    def checkpoint(self) -> dict:
        self.db.commit()
        rows = self.rows()
        return dict(database_sha256=file_hash(self.path), event_count=len(rows),
            event_store_sha256=digest(rows), modern_state_sha256=digest(
                {"policy": "exact relation / recent4 / contradiction anchors / fill6"}))

    def reconcile(self, store) -> dict:
        rows = self.rows()
        if len(rows) != len(store.records["events"]):
            raise RuntimeError("durable store/session event count mismatch")
        for row, envelope in zip(rows, store.records["events"]):
            event, receipt = envelope["record"], envelope["record"]["receipt"]
            if row["event_identity"] != canonical(event["receipt_identity"]) or \
                    row["receipt_provenance_sha256"] != event["receipt_provenance_sha256"] or \
                    row["authorization_status"] != "AUTHORIZED" or \
                    row["realized_consequence"] != receipt["realized_consequence"] or \
                    row["event_stream_sequence"] != envelope["sequence"]:
                raise RuntimeError("durable store contains non-authenticated evidence")
        return dict(status="PASS", authenticated_events=len(rows))
