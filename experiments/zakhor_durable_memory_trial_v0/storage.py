from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import time
from typing import Any

from horus.core import digest


SCHEMA_VERSION = 1
LIMIT = 6
REBIRTH_K = 3


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def file_hash(path: Path) -> str:
    h = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass(frozen=True)
class Retrieval:
    condition: str
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
    zakhor_state: dict | None


class DurableMemory:
    """One SQLite evidence store with two read-only retrieval policies."""
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
        self.db.execute("PRAGMA foreign_keys=ON")
        if create:
            self._create()
        self._verify_schema()

    def close(self) -> None:
        self.db.close()

    def __enter__(self): return self
    def __exit__(self, *_): self.close()

    def _create(self) -> None:
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
        CREATE TABLE zakhor_state(
          relation TEXT PRIMARY KEY,
          active_consequence INTEGER NOT NULL,
          active_regime INTEGER NOT NULL,
          active_since_order INTEGER NOT NULL,
          challenger_consequence INTEGER,
          challenger_count INTEGER NOT NULL,
          updated_order INTEGER NOT NULL,
          state_sha256 TEXT NOT NULL
        );
        CREATE TABLE zakhor_regimes(
          relation TEXT NOT NULL,
          regime INTEGER NOT NULL,
          consequence INTEGER NOT NULL,
          starts_at_order INTEGER NOT NULL,
          confirmed_at_order INTEGER NOT NULL,
          PRIMARY KEY(relation, regime)
        );
        """)
        self.db.execute("INSERT INTO metadata VALUES('schema_version', ?)",
                        (str(SCHEMA_VERSION),))
        self.db.commit()

    def _verify_schema(self) -> None:
        row = self.db.execute("SELECT value FROM metadata WHERE key='schema_version'").fetchone()
        if row is None or row[0] != str(SCHEMA_VERSION):
            raise RuntimeError("durable memory schema mismatch")

    @staticmethod
    def _state_hash(value: dict) -> str:
        return digest({k: value[k] for k in value if k != "state_sha256"})

    def _update_zakhor(self, relation: str, value: int, order: int) -> None:
        row = self.db.execute("SELECT * FROM zakhor_state WHERE relation=?",
                              (relation,)).fetchone()
        if row is None:
            state = dict(relation=relation, active_consequence=value, active_regime=1,
                active_since_order=order, challenger_consequence=None,
                challenger_count=0, updated_order=order)
            state["state_sha256"] = self._state_hash(state)
            self.db.execute("INSERT INTO zakhor_state VALUES(?,?,?,?,?,?,?,?)", tuple(state.values()))
            self.db.execute("INSERT INTO zakhor_regimes VALUES(?,?,?,?,?)",
                            (relation, 1, value, order, order))
            return
        state = dict(row)
        if state["state_sha256"] != self._state_hash(state):
            raise RuntimeError("Zakhor retrieval state authentication failed")
        if value == state["active_consequence"]:
            state["challenger_consequence"] = None
            state["challenger_count"] = 0
        else:
            if value == state["challenger_consequence"]:
                state["challenger_count"] += 1
            else:
                state["challenger_consequence"] = value
                state["challenger_count"] = 1
            if state["challenger_count"] >= REBIRTH_K:
                state["active_regime"] += 1
                state["active_consequence"] = value
                state["active_since_order"] = order - REBIRTH_K + 1
                state["challenger_consequence"] = None
                state["challenger_count"] = 0
                self.db.execute("INSERT INTO zakhor_regimes VALUES(?,?,?,?,?)",
                    (relation, state["active_regime"], value,
                     state["active_since_order"], order))
        state["updated_order"] = order
        state["state_sha256"] = self._state_hash(state)
        self.db.execute("""UPDATE zakhor_state SET active_consequence=?,active_regime=?,
          active_since_order=?,challenger_consequence=?,challenger_count=?,updated_order=?,
          state_sha256=? WHERE relation=?""", (state["active_consequence"],
          state["active_regime"], state["active_since_order"],
          state["challenger_consequence"], state["challenger_count"],
          state["updated_order"], state["state_sha256"], relation))

    def record(self, store, event_envelope: dict, context_identifier: str) -> dict:
        """Admit only the just-published, authenticated SessionStore event."""
        if not store.records["events"] or event_envelope is not store.records["events"][-1]:
            raise RuntimeError("event is not current authenticated publication")
        event = event_envelope["record"]
        receipt = event.get("receipt", {})
        if event.get("authorization_status") != "AUTHORIZED":
            raise RuntimeError("unauthorized evidence cannot enter durable memory")
        if tuple(event.get("receipt_identity", ())) != (
                receipt.get("source_identity"), receipt.get("event_id"),
                receipt.get("epoch"), receipt.get("transaction_id")):
            raise RuntimeError("receipt identity mismatch")
        if digest(receipt) != event.get("receipt_provenance_sha256"):
            raise RuntimeError("receipt provenance mismatch")
        memory = event.get("memory_record", {})
        for memory_key, receipt_key in (("epoch", "epoch"),
                ("transaction_id", "transaction_id"), ("pre_state", "pre_state"),
                ("action", "action"), ("next_state", "next_state"),
                ("consequence", "realized_consequence")):
            if memory.get(memory_key) != receipt.get(receipt_key):
                raise RuntimeError("authorized Memory/receipt mismatch")
        identity = canonical(event["receipt_identity"])
        order = len(store.records["events"])
        relation = f'{receipt["pre_state"]}:{receipt["action"]}'
        head = sha256(canonical(event_envelope).encode()).hexdigest()
        authorization_identity = canonical([
            event["authorization_status"], memory.get("pair_decision_id"),
            event_envelope["sequence"]])
        with self.db:
            self.db.execute("""INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (order, identity, receipt["source_identity"], receipt["event_id"],
                 receipt["epoch"], receipt["transaction_id"], receipt["pre_state"],
                 relation, receipt["action"], receipt["realized_consequence"],
                 receipt["next_state"], event["receipt_provenance_sha256"],
                 event["authorization_status"], authorization_identity,
                 context_identifier, event_envelope["sequence"], head))
            self._update_zakhor(relation, receipt["realized_consequence"], order)
        return dict(order=order, event_identity=identity, relation=relation,
                    event_stream_head_sha256=head)

    def _rows(self, relation: str) -> list[dict]:
        return [dict(row) for row in self.db.execute(
            "SELECT * FROM events WHERE relation=? ORDER BY chronological_order", (relation,))]

    def history(self, relation: str) -> list[dict]:
        return self._rows(relation)

    @staticmethod
    def _public(row: dict) -> dict:
        return dict(epoch=row["epoch"], transaction_id=row["transaction_id"],
            surface_action="K2", next_state=row["realized_next_state"],
            consequence=row["realized_consequence"],
            memory_identity=row["event_identity"],
            chronological_order=row["chronological_order"])

    def retrieve_modern(self, relation: str, limit: int = LIMIT) -> Retrieval:
        started = time.perf_counter()
        rows = self._rows(relation)
        recent = list(reversed(rows[-4:]))
        selected, reasons = [], {}
        for row in recent:
            selected.append(row); reasons[row["event_identity"]] = "RECENT_EXACT_RELATION"
        represented = {row["realized_consequence"] for row in selected}
        for value in sorted({row["realized_consequence"] for row in rows} - represented):
            row = next(item for item in reversed(rows) if item["realized_consequence"] == value)
            if row not in selected and len(selected) < limit:
                selected.append(row); reasons[row["event_identity"]] = "CONTRADICTION_ANCHOR"
        for row in reversed(rows):
            if row not in selected and len(selected) < limit:
                selected.append(row); reasons[row["event_identity"]] = "RECENCY_FILL"
        selected.sort(key=lambda row: row["chronological_order"])
        return self._retrieval("M", relation, rows, selected, reasons, started, None)

    def retrieve_zakhor(self, relation: str, limit: int = LIMIT) -> Retrieval:
        started = time.perf_counter()
        rows = self._rows(relation)
        raw_state = self.db.execute("SELECT * FROM zakhor_state WHERE relation=?",
                                    (relation,)).fetchone()
        state = None if raw_state is None else dict(raw_state)
        if state is not None and state["state_sha256"] != self._state_hash(state):
            raise RuntimeError("Zakhor retrieval state authentication failed")
        selected, reasons = [], {}
        if state is not None:
            # Preserve unassimilated strangers first; K consecutive observations
            # trigger regime rebirth, matching the frozen Zakhor K=3 principle.
            if state["challenger_consequence"] is not None:
                challengers = [row for row in rows
                    if row["chronological_order"] > state["active_since_order"] and
                    row["realized_consequence"] == state["challenger_consequence"]]
                for row in challengers[-REBIRTH_K:]:
                    selected.append(row); reasons[row["event_identity"]] = "STRANGER_CANDIDATE"
            active = [row for row in rows if row["chronological_order"] >=
                      state["active_since_order"] and row["realized_consequence"] ==
                      state["active_consequence"]]
            for row in active[-3:]:
                if row not in selected:
                    selected.append(row); reasons[row["event_identity"]] = "ACTIVE_REGIME_RECENT"
            regimes = [dict(row) for row in self.db.execute(
                "SELECT * FROM zakhor_regimes WHERE relation=? ORDER BY regime DESC",
                (relation,))]
            for regime in regimes[1:]:
                candidates = [row for row in rows if row["chronological_order"] >=
                    regime["starts_at_order"] and row["realized_consequence"] ==
                    regime["consequence"]]
                if candidates and candidates[-1] not in selected and len(selected) < limit:
                    row = candidates[-1]; selected.append(row)
                    reasons[row["event_identity"]] = "PRIOR_REGIME_ANCHOR"
        for row in reversed(rows):
            if row not in selected and len(selected) < limit:
                selected.append(row); reasons[row["event_identity"]] = "RECENCY_FILL"
        selected = selected[:limit]
        selected.sort(key=lambda row: row["chronological_order"])
        return self._retrieval("Z", relation, rows, selected, reasons, started, state)

    def _retrieval(self, condition: str, relation: str, candidates: list[dict],
                   selected: list[dict], reasons: dict, started: float,
                   state: dict | None) -> Retrieval:
        candidate_values = tuple(row["realized_consequence"] for row in candidates)
        selected_values = tuple(row["realized_consequence"] for row in selected)
        contradiction = len(set(candidate_values)) > 1
        included = len(set(selected_values)) > 1
        return Retrieval(condition, relation, len(candidates),
            tuple(self._public(row) for row in selected),
            tuple(row["event_identity"] for row in selected),
            tuple(reasons[row["event_identity"]] for row in selected),
            tuple(row["chronological_order"] for row in selected),
            candidate_values, selected_values, contradiction, included,
            contradiction and not included, time.perf_counter() - started, state)

    def checkpoint(self) -> dict:
        self.db.commit()
        self.db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        self.db.commit()
        event_rows = [dict(row) for row in self.db.execute(
            "SELECT * FROM events ORDER BY chronological_order")]
        z_state = [dict(row) for row in self.db.execute(
            "SELECT * FROM zakhor_state ORDER BY relation")]
        regimes = [dict(row) for row in self.db.execute(
            "SELECT * FROM zakhor_regimes ORDER BY relation,regime")]
        return dict(database_sha256=file_hash(self.path), event_count=len(event_rows),
            event_store_sha256=digest(event_rows), modern_state_sha256=digest(
                {"policy": "exact relation / recent4 / contradiction anchors / fill6"}),
            zakhor_state_sha256=digest(z_state), zakhor_index_sha256=digest(regimes))

    def reconcile(self, store) -> dict:
        events = self._rows("1:HOLD")
        if len(events) != len(store.records["events"]):
            raise RuntimeError("durable store/session event count mismatch")
        for row, envelope in zip(events, store.records["events"]):
            event, receipt = envelope["record"], envelope["record"]["receipt"]
            if row["event_identity"] != canonical(event["receipt_identity"]) or \
                    row["receipt_provenance_sha256"] != event["receipt_provenance_sha256"] or \
                    row["authorization_status"] != "AUTHORIZED" or \
                    row["realized_consequence"] != receipt["realized_consequence"] or \
                    row["event_stream_sequence"] != envelope["sequence"]:
                raise RuntimeError("durable store contains non-authenticated evidence")
        return dict(status="PASS", authenticated_events=len(events))
