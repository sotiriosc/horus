"""Offline rebaseline checks. Never starts or contacts a model server."""
import argparse
from contextlib import ExitStack
from copy import deepcopy
from dataclasses import asdict, replace
import importlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


def run(repository):
    sys.path.insert(0, str(repository))
    from experiments.realized_event_grounding_v0.campaign import TestWorld, published
    from experiments.realized_event_grounding_v0.receipt import ExternalExecutionBoundary
    from experiments.realized_event_grounding_v0.framework import evidence, RealizedEventFramework
    from experiments.state_recovery_authorizer_status_binding_v1.framework import StatusBoundFramework
    from experiments.base_framework_v1.framework import MeasureAuditor
    from experiments.base_framework_v1 import source_a, source_b
    from experiments.base_framework_v2 import witness_c, campaign as old_campaign

    records = []; mutations = []; suites = []
    def setup(name, state=1, epoch=1001, outcome=None, change_after=0):
        class World(TestWorld):
            def execute(self, *args):
                actual = super().execute(*args)
                if outcome is not None and self.oracle.execution_count > change_after:
                    self.last_actual = replace(actual, consequence=outcome)
                return self.last_actual
        world = World(state, False)
        source = ExternalExecutionBoundary(world, 'REBASELINE_' + name)
        return StatusBoundFramework(source.reader(), state, epoch), source, world

    def snapshot(system):
        return dict(protected=published(system), authorized=sorted(system.inner.state_authorizer.authorized),
                    evictions=system.inner.memory.evictions)

    def check(name, operation):
        # Any failure aborts this audit; never tune or repair the architecture.
        detail = operation()
        records.append(dict(name=name, passed=True, detail=detail))

    with ExitStack() as stack:
        socket = stack.enter_context(patch('socket.socket', side_effect=AssertionError('ZERO INFERENCE: socket forbidden')))
        http = stack.enter_context(patch('urllib.request.urlopen', side_effect=AssertionError('ZERO INFERENCE: HTTP forbidden')))
        banned = [stack.enter_context(patch.object(m, n, side_effect=AssertionError('LEGACY LAW AUTHORITY FORBIDDEN')))
                  for m, n in [(source_a, 'observe'), (source_b, 'observe'), (witness_c, 'observe'), (old_campaign, 'make_evidence')]]
        # Same state/action, native prediction/history and source identity; only external consequence differs.
        for consequence in (1, -1):
            system, source, world = setup('MUTATION', outcome=consequence, change_after=3)
            for action in ('HOLD','ADVANCE','RETREAT'):
                p=system.begin_step(forced_action=action)
                r=source.execute(p.epoch,p.transaction_id,p.action)
                assert system.submit_package(evidence(r)).committed
                source.release(r)
            before = snapshot(system)
            pending = system.begin_step(forced_action='HOLD')
            prediction = asdict(pending.prediction)
            assert source.reader().current() is None
            receipt = source.execute(pending.epoch, pending.transaction_id, pending.action)
            result = system.submit_package(evidence(receipt))
            assert result.committed and result.continued
            memory = system.inner.memory.records[-1]
            assert memory.consequence == receipt.realized_consequence == world.last_actual.consequence == consequence
            assert system.packages[-1].receipt is receipt and asdict(system.inner._prediction_at_begin) == prediction
            assert asdict(system.packages[-1].prediction) == prediction
            mutations.append(dict(before=before, prediction=prediction, actual=asdict(world.last_actual),
                                  receipt=asdict(receipt), memory=asdict(memory), result=asdict(result),
                                  original_receipt_object=True, old_memory_unchanged=published(system)['memory'][:-1]==before['protected']['memory'],
                                  retained_HOLD_consequences=[r.consequence for r in system.inner.memory.records if r.pre_state==1 and r.action=='HOLD']))
        assert mutations[0]['before'] == mutations[1]['before']
        assert mutations[0]['prediction'] == mutations[1]['prediction']
        assert {k:v for k,v in mutations[0]['receipt'].items() if k!='realized_consequence'} == {k:v for k,v in mutations[1]['receipt'].items() if k!='realized_consequence'}
        assert mutations[1]['prediction']['consequence'] == 1
        assert mutations[1]['memory']['measurement_matches'] is False
        assert all(m['old_memory_unchanged'] for m in mutations)
        assert mutations[1]['retained_HOLD_consequences']==[1,-1]

        for alias in ((2, -2), (1, True), (1, 1.0)):
            def domain(alias=alias):
                system, source, world = setup('ALIAS', state=0)
                pending = system.begin_step(forced_action='ADVANCE')
                receipt = source.execute(pending.epoch, pending.transaction_id, pending.action)
                package = evidence(receipt); fields = list(receipt.binding()); fields[4:6] = alias
                package = replace(package, a=tuple(fields), b=tuple(fields))
                before = snapshot(system); result = system.submit_package(package)
                assert not result.committed and not result.continued and snapshot(system)==before
                return dict(candidate_next_state=alias[0], candidate_consequence=alias[1], reason=result.reason, publication_unchanged=True)
            check('numeric_domain_alias_' + repr(alias), domain)
        def root_domain():
            system, source, world = setup('INVALID_ROOT_DOMAIN', state=0, outcome=-2)
            pending = system.begin_step(forced_action='ADVANCE');receipt=source.execute(pending.epoch,pending.transaction_id,pending.action)
            before=snapshot(system);result=system.submit_package(evidence(receipt))
            assert result.reason=='receipt_domain' and not result.committed and snapshot(system)==before
            return dict(reason=result.reason,publication_unchanged=True)
        check('genuine_but_out_of_domain_emission',root_domain)
        for inner in (False, True):
            def ingress(inner=inner):
                system, source, world=setup('INGRESS');system.begin_step(forced_action='HOLD');before=snapshot(system)
                endpoint=system.inner if inner else system
                result=endpoint.submit_receipt('A',None)
                assert not result.committed and not result.continued and snapshot(system)==before
                return dict(inner=inner,reason=result.reason,publication_unchanged=True)
            check('delegated_ingress_'+str(inner),ingress)
        for attack in ('equal_copy','wrong_receipt','old_receipt','detached_pair_binding','detached_package_binding'):
            def binding(attack=attack):
                system,source,world=setup('BINDING')
                p=system.begin_step(forced_action='HOLD');old=source.execute(p.epoch,p.transaction_id,p.action)
                assert system.submit_package(evidence(old)).committed;source.release(old)
                p=system.begin_step(forced_action='HOLD');receipt=source.execute(p.epoch,p.transaction_id,p.action);package=evidence(receipt)
                if attack=='equal_copy':package=evidence(replace(receipt))
                elif attack=='wrong_receipt':package=evidence(replace(receipt,realized_consequence=-1))
                elif attack=='old_receipt':package=evidence(old)
                elif attack=='detached_pair_binding':package=replace(package,a=old.binding(),b=old.binding())
                else:package=replace(package,c=old.identity())
                before=snapshot(system);result=system.submit_package(package)
                assert not result.committed and not result.continued and snapshot(system)==before
                return dict(reason=result.reason,publication_unchanged=True)
            check(attack,binding)
        for fault in ('late_failure','pair_identity','package_order'):
            def atomic(fault=fault):
                system,source,world=setup('ATOMIC')
                p=system.begin_step(forced_action='HOLD');r=source.execute(p.epoch,p.transaction_id,p.action)
                assert system.submit_package(evidence(r)).committed;source.release(r)
                p=system.begin_step(forced_action='HOLD');r=source.execute(p.epoch,p.transaction_id,p.action)
                before=snapshot(system);original=system._audit
                def audit(core,packages,memory=True):
                    if len(packages)==2:
                        if fault=='pair_identity':core.pairs.decisions[-1]=replace(core.pairs.decisions[-1],transaction_id=99)
                        elif fault=='package_order':packages.reverse()
                        else:raise ValueError('injected final validation failure')
                    return original(core,packages,memory)
                with patch.object(system,'_audit',audit):result=system.submit_package(evidence(r))
                assert not result.committed and not result.continued and snapshot(system)==before
                return dict(reason=result.reason,publication_unchanged=True,authorization_ledger_unchanged=True)
            check('staged_'+fault,atomic)
        def descending():
            system,source,world=setup('DESCENDING',epoch=101)
            for epoch in (101,1):
                if epoch!=101:system.start_epoch(epoch)
                p=system.begin_step(forced_action='HOLD');r=source.execute(p.epoch,p.transaction_id,p.action)
                assert system.submit_package(evidence(r)).committed;source.release(r)
            original=list(system.inner.memory.records);system.inner.memory.records[0]=replace(original[0],consequence=-1)
            p=system.begin_step(forced_action='HOLD')
            assert system.inner.memory.records==original
            r=source.execute(p.epoch,p.transaction_id,p.action);assert system.submit_package(evidence(r)).committed
            ids=[(x.epoch,x.transaction_id) for x in system.inner.memory.records]
            assert ids==[(101,1),(1,1),(1,2)];system.assert_bounds()
            return dict(insertion_order=ids,identity_aligned_repair=True)
        check('descending_epoch_recovery_order',descending)
        def latch():
            system,source,world=setup('LATCH',outcome=-1)
            p=system.begin_step(forced_action='HOLD');original=asdict(p.prediction)
            system.inner.pending.prediction=replace(p.prediction,consequence=-1)
            r=source.execute(p.epoch,p.transaction_id,p.action);result=system.submit_package(evidence(r))
            assert result.committed and not system.inner.memory.records[-1].measurement_matches
            assert asdict(system.packages[-1].prediction)==original
            return dict(original_prediction=original,late_pending_prediction_ignored=True)
        check('pre_execution_prediction_latch',latch)
        modules=[
            'realized_event_grounding_v0.test_grounding',
            'state_recovery_proposal_interface_v1.test_interface',
            'state_recovery_authorizer_status_binding_v1.test_status',
            'composition_input_bindings_v1.test_bindings',
            'cross_episode_authenticated_memory_boundary_v0.test_boundary',
            'cross_episode_initialization_boundary_v1.test_boundary',
            'map_guided_explorer_interface_v0.test_interface',
            'model_proposal_role_composition_v2.test_study',
        ]
        for name in modules:
            suite=unittest.defaultTestLoader.loadTestsFromName('experiments.'+name);stream=io.StringIO()
            result=unittest.TextTestRunner(stream=stream,verbosity=1).run(suite)
            suites.append(dict(module=name,tests=result.testsRun,passed=result.wasSuccessful(),log=stream.getvalue()))
            assert result.wasSuccessful(),(name,stream.getvalue())
        assert socket.call_count==http.call_count==0
        assert all(m.call_count==0 for m in banned)
    return dict(model_calls=0,network_calls=0,legacy_law_authority_calls=0,mutation=mutations,
                controls=records,existing_suites=suites,tests=sum(x['tests'] for x in suites),
                deterministic_controls=len(records),passed=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    data=run(args.repository.resolve());args.output.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in data.items() if k not in ('mutation','controls','existing_suites')}))

if __name__=='__main__':main()
