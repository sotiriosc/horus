"""Driver-owned initialization for a copy-stageable in-process world.

A single publication reference owns both present world and framework. No model
gets this controller, source, framework or world. Public snapshots are detached
values. Existing admission and receipt authority remain unchanged.
"""
from copy import copy,deepcopy
from dataclasses import dataclass
from threading import RLock
from experiments.base_framework_v0.framework import MapModel
from experiments.realized_event_grounding_v0.campaign import TestWorld,published
from experiments.realized_event_grounding_v0.receipt import ExternalExecutionBoundary
from experiments.state_recovery_authorizer_status_binding_v1.framework import StatusBoundFramework,StatusBoundAuthorizer
from .projection import explorer_payload,map_payload,ACTIONS


@dataclass(frozen=True)
class EpisodePlan:
    initial_state:int=0
    first_epoch:int=1001
    second_epoch:int=1002

    def __post_init__(self):
        if type(self.initial_state) is not int or self.initial_state not in range(4):
            raise ValueError('registered state must be an exact finite int')
        if (type(self.first_epoch) is not int or type(self.second_epoch) is not int or
                (self.first_epoch,self.second_epoch)!=(1001,1002)):
            raise ValueError('registered epoch pair must be 1001,1002')


class EpisodeWorld:
    """Trusted reset primitive for the existing stationary simulation only.

    Copies external simulation state before initialization. No action executes,
    counter increments, last event changes or receipt is minted. This is not a
    physical external-device rollback primitive.
    """
    def __init__(self,initial_state):self.fixture=TestWorld(initial_state,False)
    @property
    def state(self):return self.fixture.oracle.state
    @property
    def execution_count(self):return self.fixture.oracle.execution_count
    @property
    def last_actual(self):return self.fixture.last_actual
    def execute(self,epoch,transaction_id,action):return self.fixture.execute(epoch,transaction_id,action)
    def initialize_staged(self,initial_state):
        # Called only on an unpublished copy owned by the controller.
        self.fixture.oracle._state=initial_state


@dataclass(frozen=True)
class Publication:
    world:EpisodeWorld
    framework:StatusBoundFramework


class _WorldExecutionPort:
    """Stable source-facing execution route; no reset operation."""
    def __init__(self,current):self._current=current
    def execute(self,*args):return self._current().world.execute(*args)


class EpisodeController:
    """Trusted experiment controller. Participants receive projection values only."""
    def __init__(self,source_identity,plan=EpisodePlan()):
        self._lock=RLock();self._plan=plan;self._source_identity=source_identity
        self._source=ExternalExecutionBoundary(_WorldExecutionPort(lambda:self._active),source_identity)
        self._registered_source=self._source
        self._active=Publication(self._make_world(plan.initial_state),
            StatusBoundFramework(self._source.reader(),plan.initial_state,plan.first_epoch))

    def _make_world(self,initial_state):return EpisodeWorld(initial_state)

    def snapshot(self):
        with self._lock:
            p=self._active;c=p.framework.inner
            return deepcopy(dict(world_state=p.world.state,world_executions=p.world.execution_count,
                last_actual=p.world.last_actual,protected=published(p.framework),epoch=c.epoch,
                epochs_started=c.epochs_started,next_transaction_id=c.next_transaction_id,
                episode_steps=c.episode_steps,continuation=c.continuation_authorized,
                pending=c.pending,root_receipt=self._source.reader().current(),
                authorization_keys=sorted(c.state_authorizer.authorized),authorizer_type=type(c.state_authorizer).__name__,
                trace=c.trace,metrics=c.metrics,evictions=c.memory.evictions,
                prediction_at_begin=c._prediction_at_begin,package_grant=c._package_grant))

    def projections(self,mapping):
        with self._lock:
            p=self._active;p.framework.assert_bounds();core=p.framework.inner;state=core.map.current.state
            return dict(Explorer=explorer_payload(state,core.memory.records,mapping),
                Map={a:map_payload(state,a,core.memory.records,mapping) for a in ACTIONS})

    def begin_step(self,action):
        with self._lock:return self._active.framework.begin_step(forced_action=action)
    def execute_pending(self):
        with self._lock:
            p=self._active.framework.inner.pending
            if p is None:raise RuntimeError('no pending transaction')
            return self._source.execute(p.epoch,p.transaction_id,p.action)
    def submit_package(self,package,**faults):
        with self._lock:return self._active.framework.submit_package(package,**faults)
    def release(self,receipt):
        with self._lock:self._source.release(receipt)

    def _prepare_framework(self,active,new_epoch,initial_state):
        # Shallow wrapper copy retains the same read port and historical package
        # objects; deepcopy only the core, exactly as ordinary staged admission.
        staged=copy(active.framework);staged.inner=deepcopy(active.framework.inner)
        staged.packages=list(active.framework.packages)
        staged.inner.start_epoch(new_epoch)
        staged.inner.map=MapModel(initial_state,new_epoch)
        staged.assert_bounds()
        return staged

    def _prepare_world(self,active,initial_state):
        staged=deepcopy(active.world)
        staged.initialize_staged(initial_state)
        return staged

    def start_episode(self,new_epoch,initial_state):
        with self._lock:
            active=self._active;core=active.framework.inner
            if type(initial_state) is not int or initial_state not in range(4):
                raise ValueError('initial_state must be an exact finite int')
            if type(new_epoch) is not int:raise ValueError('epoch must be an exact int')
            if initial_state!=self._plan.initial_state:raise ValueError('state differs from registered plan')
            if self._source is not self._registered_source:raise ValueError('source lifetime changed')
            if self._source.reader().current() is not None:raise RuntimeError('pending external receipt')
            if core.pending is not None:raise RuntimeError('in-flight transaction')
            if (not core.continuation_authorized or not core.map.current.valid or
                    core.map.quarantine or core.memory.quarantine):raise RuntimeError('illegal prior continuation state')
            if active.world.state!=core.map.current.state:raise ValueError('prior world/Map state split')
            active.framework.assert_bounds()
            if any(p.receipt.source_identity!=self._source_identity for p in active.framework.packages):
                raise ValueError('retained source lifetime mismatch')
            # Existing epoch checks run on staged state, not the publication.
            staged_framework=self._prepare_framework(active,new_epoch,initial_state)
            if (core.epoch,new_epoch)!=(self._plan.first_epoch,self._plan.second_epoch):
                raise ValueError('epoch differs from registered plan')
            staged_world=self._prepare_world(active,initial_state)
            if (staged_world.state!=initial_state or staged_world.execution_count!=active.world.execution_count or
                    staged_world.last_actual!=active.world.last_actual):raise ValueError('external reset preparation invalid')
            old=published(active.framework);new=published(staged_framework)
            if any(old[k]!=new[k] for k in ('memory','pairs','packages','memory_quarantine','commits')):
                raise ValueError('history altered during initialization')
            if any(a is not b for a,b in zip(active.framework.packages,staged_framework.packages)):
                raise ValueError('historical package identity changed')
            if (staged_framework.inner.map.current.state!=initial_state or
                    staged_framework.inner.map.current.epoch!=new_epoch or
                    staged_framework.inner.map.current.version!=0 or
                    type(staged_framework.inner.state_authorizer) is not StatusBoundAuthorizer):
                raise ValueError('authorized reset preparation invalid')
            publication=Publication(staged_world,staged_framework)
            result=dict(new_epoch=new_epoch,initial_state=initial_state,map_version=0,
                realized_events=0,receipts=0,memory_observations=0,pairs=0,packages=0)
            # Sole commit point. No world/Map pair of assignments, callback or I/O.
            self._active=publication
            return result
