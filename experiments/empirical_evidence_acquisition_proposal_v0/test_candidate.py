"""Synthetic, zero-inference and zero-world checks for the inactive E proposal."""
import json
import unittest

from .candidate import ACTIONS, SOURCE, TRIGGER_REASON, WINDOW, evaluate


def event(index, consequence, state=1, action='HOLD', next_state=None, status='AUTHORIZED'):
    return dict(event_stream_sequence=index, authorization_status=status,
                event_identity=f'fixture-event-{index}', receipt_identity=[f'fixture-{index}'],
                receipt_sha256=f'{index:064x}', state=state, action=action,
                next_state=state if next_state is None else next_state,
                consequence=consequence)


def context(values, state=1, kind=None):
    history = [event(i, c, state) for i, c in enumerate(values, 1)]
    kind = kind or ('EMPIRICALLY_STABLE' if len(set(values)) == 1 else 'VARIABLE_RELATION')
    selected = dict(relation=f'{state}:HOLD', relation_type='EMPIRICAL', kind=kind,
                    observation_count=len(values), possible_change=None,
                    recent_window=[dict(next_state=state, consequence=c) for c in values[-WINDOW:]])
    assessments = {
        'ADVANCE': dict(relation=f'{state}:ADVANCE', relation_type='DETERMINISTIC',
                        kind='UNSEEN', observation_count=0, established_value=None),
        'HOLD': selected,
        'RETREAT': dict(relation=f'{state}:RETREAT', relation_type='DETERMINISTIC',
                        kind='UNSEEN', observation_count=0, established_value=None),
    }
    return history, assessments


class CandidateTests(unittest.TestCase):
    def check(self, values, expected, **changes):
        history, assessments = context(values)
        for action, update in changes.get('assessments', {}).items():
            assessments[action].update(update)
        result = evaluate(1, changes.get('actions', ACTIONS), assessments, history)
        self.assertEqual(result['eligible'], expected)
        self.assertEqual(result['target_action'], 'ADVANCE' if expected else None)
        return result

    def test_positive_empirical_relation_does_not_trigger(self):
        self.check([1, 1, 1, 1], False)

    def test_recent_negative_cumulative_positive_does_not_trigger(self):
        result = self.check([1] * 8 + [-1] * 4, False)
        self.assertEqual((result['recent_sum'], result['cumulative_sum']), (-4, 4))

    def test_cumulative_nonpositive_recent_positive_does_not_trigger(self):
        result = self.check([-1] * 4 + [1] * 4, False)
        self.assertEqual((result['recent_sum'], result['cumulative_sum']), (4, 0))

    def test_both_nonpositive_triggers_canonical_first_unseen(self):
        result = self.check([-1, -1, 0, 0], True, actions=['RETREAT', 'HOLD', 'ADVANCE'])
        self.assertEqual(result['suffix_count'], 4)
        self.assertEqual(result['unseen_candidates'], ['ADVANCE', 'RETREAT'])
        self.assertEqual(result['source'], SOURCE)
        self.assertEqual(result['reason'], TRIGGER_REASON)

    def test_less_than_four_cannot_trigger(self):
        self.check([-1, -1, 0], False)

    def test_no_unseen_alternative_does_not_trigger(self):
        known = dict(kind='ESTABLISHED', observation_count=1,
                     established_value=dict(consequence=0, next_state=1))
        self.check([-1] * 4, False, assessments={'ADVANCE': known, 'RETREAT': known})

    def test_unresolved_only_does_not_trigger(self):
        unresolved = dict(kind='UNRESOLVED_CHANGE', observation_count=2)
        self.check([-1] * 4, False,
                   assessments={'ADVANCE': unresolved, 'RETREAT': unresolved})

    def test_possible_regime_change_does_not_trigger(self):
        self.check([-1] * 4, False, assessments={'HOLD': dict(
            kind='POSSIBLE_REGIME_CHANGE', possible_change=dict(challenger='1:-1'))})

    def test_established_positive_ceiling_does_not_trigger(self):
        self.check([-1] * 4, False, assessments={'ADVANCE': dict(
            kind='ESTABLISHED', observation_count=1,
            established_value=dict(consequence=1, next_state=2))})

    def test_state_change_breaks_suffix(self):
        history, _ = context([-1] * 4)
        history[-1]['next_state'] = 2
        _, assessments = context([], state=2)
        self.assertFalse(evaluate(2, ACTIONS, assessments, history)['eligible'])

    def test_action_change_breaks_suffix(self):
        history, assessments = context([-1] * 4)
        history.append(event(5, -1, action='RETREAT'))
        self.assertFalse(evaluate(1, ACTIONS, assessments, history)['eligible'])

    def test_non_authorized_event_breaks_suffix(self):
        history, assessments = context([-1] * 4)
        history.append(event(5, -1, status='REJECTED'))
        self.assertFalse(evaluate(1, ACTIONS, assessments, history)['eligible'])

    def test_one_acquisition_breaks_suffix_even_if_negative(self):
        history, assessments = context([-1] * 4)
        first = evaluate(1, ACTIONS, assessments, history)
        self.assertTrue(first['eligible'])
        history.append(event(5, -1, action=first['target_action']))
        assessments['ADVANCE'].update(kind='ESTABLISHED', observation_count=1,
                                      established_value=dict(consequence=-1, next_state=1))
        second = evaluate(1, ACTIONS, assessments, history)
        self.assertFalse(second['eligible'])
        self.assertEqual(second['suffix_count'], 1)

    def test_restart_reconstructs_same_result_without_mutable_counter(self):
        history, assessments = context([-1, -1, 0, 0])
        before = evaluate(1, ACTIONS, assessments, history)
        after = evaluate(1, ACTIONS, json.loads(json.dumps(assessments)),
                         json.loads(json.dumps(history)))
        self.assertEqual(before, after)

    def test_incomplete_or_inconsistent_projection_fails_closed(self):
        history, assessments = context([-1] * 4)
        with self.assertRaises(ValueError):
            evaluate(1, ACTIONS, assessments, history[1:])
        assessments['HOLD']['recent_window'][0]['consequence'] = 1
        with self.assertRaises(ValueError):
            evaluate(1, ACTIONS, assessments, history)


if __name__ == '__main__':
    unittest.main()
