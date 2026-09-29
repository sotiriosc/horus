"""Read-only active-state mapping into the byte-frozen empirical E rule."""
from pathlib import Path
from hashlib import sha256

from horus.live import SessionStore
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory, canonical
from experiments.empirical_evidence_acquisition_proposal_v0 import candidate

FROZEN_E_SHA256 = 'fcef478a02beb69a1d29988c5ce12929ad2ba077591131e0dcd114e7ccab99b4'


class IntegrationInvariantError(RuntimeError):
    """Abort selection without a model request or a world action."""


def authenticated_projection(store, memory):
    """Use SessionStore's existing authentication/replay, then reconcile Memory.

    Active events are admitted originals only. An out-of-band rejection journal
    has no active chronology contract, so reject it instead of dropping its tail
    or synthesizing a second event authority.
    """
    if not isinstance(store, SessionStore) or not isinstance(memory, ModernMemory):
        raise IntegrationInvariantError('E requires the active authenticated stores')
    if store._read_checkpoint() != store.checkpoint:
        raise IntegrationInvariantError('checkpoint changed before E projection')
    for name in store.STREAMS:
        if store._read_stream(name) != store.records[name]:
            raise IntegrationInvariantError('authenticated stream differs from live state')
    store._validate_checkpoint_heads()
    records = store.imported_history()
    memory.reconcile(store)
    for envelope in store.records['training']:
        record = envelope['record']
        if (envelope['kind'] == 'REGISTERED_REJECTED_ATTEMPT' or
                ('authorization_status' in record and record['authorization_status'] != 'AUTHORIZED')):
            raise IntegrationInvariantError('non-authorized journal has no active event chronology')
    result = []
    for envelope, event in zip(store.records['events'], records):
        receipt = event['receipt']
        result.append(dict(event_stream_sequence=envelope['sequence'],
            authorization_status=event['authorization_status'],
            event_identity=canonical(event['receipt_identity']),
            receipt_identity=event['receipt_identity'],
            receipt_sha256=event['receipt_provenance_sha256'],
            state=receipt['pre_state'], action=receipt['action'],
            next_state=receipt['next_state'], consequence=receipt['realized_consequence']))
    if result and result[-1]['next_state'] != store.checkpoint['current_state']:
        raise IntegrationInvariantError('current state disagrees with authenticated receipt tail')
    return result


def recommendation(context, history):
    """No relation typing, evidence repair, model, world or Memory access."""
    if sha256(Path(candidate.__file__).read_bytes()).hexdigest() != FROZEN_E_SHA256:
        raise IntegrationInvariantError('frozen E source digest mismatch')
    try:
        return candidate.evaluate(context['state'], context['candidate_set'],
                                  context['assessments'], history)
    except (ValueError, KeyError, TypeError) as exc:
        raise IntegrationInvariantError('invalid E projection: ' + str(exc)) from exc
