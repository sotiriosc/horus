"""Protected observation boundary and the registered exact-relation predictors."""
from dataclasses import asdict
from hashlib import sha256
import json
import time

from experiments.map_consequence_only_isolation_v0.protocol import parse as parse_consequence
from experiments.model_map_proposal_v0.adapter import MODEL, parse as parse_joint
from experiments.model_proposal_role_composition_v2.protocol import OPTIONS
from experiments.realized_event_grounding_v0.framework import evidence
from experiments.base_framework_v0.framework import Prediction
from horus.core import BoundPredictionMap, MAPPING, digest, unwrap_map
from horus.live import CONSEQUENCE_SYSTEM, JOINT_SYSTEM, ModelClient, LiveController, _plain
from experiments.modern_memory_vs_horus_v0_1.transport import generate, RULE
from .protocol import SEED
from .reducer import predict as reduce_history
from .uncertainty import predict as uncertainty_predict
from experiments.modern_memory_vs_horus_v0.storage import canonical


def _request(system, prompt, model):
    return dict(model=model, system=system, prompt=prompt, stream=False,
                options={**dict(OPTIONS['Map']), 'seed': SEED, 'temperature': 0})


def capture(controller, store, memory, action):
    core=controller._active.framework.inner
    if core.pending is not None or controller._source.reader().current() is not None:
        raise RuntimeError('in-flight receipt during preparation')
    state=core.map.current.state
    retrieval=memory.retrieve(f'{state}:{action}')
    alias=next(k for k,v in MAPPING.items() if v==action)
    history=[{key:row[key] for key in ('epoch','transaction_id','surface_action',
        'next_state','consequence')} for row in retrieval.selected]
    payload=dict(state=state,target_action=alias,VERIFIED_CHRONOLOGICAL_HISTORY=history)
    return dict(state=state,epoch=core.epoch,transaction_id=core.next_transaction_id,
        memory_sha256=memory.checkpoint()['event_store_sha256'],
        authenticated_history_reference=store.checkpoint['streams']['events'],
        map_inputs={action:payload}, retrieval={action:dict(
            candidate_memory_count=retrieval.candidate_count,
            raw_eligible_memories=list(retrieval.selected_identities),
            memories_supplied_to_model=list(retrieval.selected_identities),
            retrieval_reasons=list(retrieval.reasons),
            chronological_positions=list(retrieval.chronological_positions),
            selected_consequences=list(retrieval.selected_consequences),
            contradictions_in_candidates=retrieval.contradictions_in_candidates,
            contradictions_included=retrieval.contradictions_included,
            contradictions_excluded=retrieval.contradictions_excluded)})


def prepare_model(context, controller, opportunity, action, perturb=False):
    started=time.perf_counter();store=context['store'];memory=context['memory']
    cap=capture(controller,store,memory,action)
    prompt=canonical(cap['map_inputs'][action])
    joint=context['joint'];g2=context['g2']
    joint_request=_request(JOINT_SYSTEM,prompt,getattr(joint,'model_id',MODEL))
    g2_request=_request(CONSEQUENCE_SYSTEM,prompt,g2.model_id)
    g2_request['horus_model_identity']=_plain(g2.horus_model_identity)
    # Freeze both complete requests before either transport call.
    base=f'{opportunity}:M:{action}'
    requests=[(joint,joint_request,f'{base}:J','joint-next-state',parse_joint,perturb),
        (g2,g2_request,f'{base}:G2','modern-consequence:G2',
         lambda raw:parse_consequence(raw,'C'),False)]
    intents=[]
    for client,request,call_id,role,parser,injected in requests:
        intents.append(store.append('calls','REQUEST_INTENT',dict(call_id=call_id,
            role=role,request=request,request_sha256=digest(request),
            condition='M',opportunity=opportunity)))
    parts=[]
    for client,request,call_id,role,parser,injected in requests:
        # _model_component accepts the existing frozen intent to avoid a
        # second logical request record; its response and parse are durable.
        result=generate(client,request,store,call_id)
        if injected and result.get('transport_error') is None:
            result={**result,'pre_fault_response_sha256':digest(result),
                'raw_output':'REGISTERED_MALFORMED_RESPONSE',
                'registered_fault':'MALFORMED_JOINT_OUTPUT'}
        response=store.append('calls','RESPONSE',dict(call_id=call_id,response=result,
            response_sha256=digest(result),fault_injected=injected))
        value=None;error=result.get('transport_error')
        if error is None:
            try:value=parser(result['raw_output'])
            except Exception as exc:error=type(exc).__name__
        kind=('VALID' if error is None else 'TRANSPORT_FAILURE'
              if error in RULE['eligible_errors'] else 'MODEL_OUTPUT_INVALID')
        parsed=store.append('calls','PARSED',dict(call_id=call_id,parsed=value,
            parse_error=error,outcome=kind,strict_parser=True))
        parts.append(dict(value=value,error=error,outcome=kind,call_id=call_id,
            request_sequence=intents[len(parts)]['sequence'],
            response_sequence=response['sequence'],parsed_sequence=parsed['sequence'],
            request_sha256=digest(request)))
    tokens=len(g2.tokenizer(prompt,add_special_tokens=False).input_ids)*2
    valid=all(p['value'] is not None for p in parts)
    prediction=(dict(next_state=parts[0]['value']['next_state'],
                     consequence=parts[1]['value']['consequence']) if valid else None)
    return dict(arm='M',capture=cap,prediction=prediction,all_valid=valid,
        parts=parts,rule='FROZEN_JOINT_MAP_AND_G2_EXACT_RELATION',
        used_event_identities=cap['retrieval'][action]['memories_supplied_to_model'],
        model_calls=2,context_tokens=tokens,model_seconds=time.perf_counter()-started,
        perturbation=perturb)


def prepare_mechanical(context,controller,arm,action):
    started=time.perf_counter();cap=capture(controller,context['store'],context['memory'],action)
    outcome=(uncertainty_predict(context['memory'],f"{cap['state']}:{action}",cap['state'])
        if arm=='U' else reduce_history(context['memory'],cap['state'],arm,action))
    return dict(arm=arm,capture=cap,prediction=dict(
        **(outcome['point'] if arm=='U' else dict(next_state=outcome['next_state'],consequence=outcome['consequence']))),
        all_valid=True,rule=outcome['rule'] if arm=='U' else outcome['reason'],used_event_identities=outcome['used_event_identities'],
        window_consequences=outcome.get('window_consequences'),
        grounded_state=outcome.get('state'),update_seconds=outcome.get('update_seconds',0),
        serialized_state_bytes=outcome.get('serialized_state_bytes',0),
        model_calls=0,context_tokens=0,model_seconds=time.perf_counter()-started,
        perturbation=False)


def publish(context,controller,batch,spec):
    arm=context['arm'];store=context['store'];memory=context['memory']
    if not batch['all_valid'] or batch['prediction'] is None:
        raise RuntimeError('invalid prediction cannot authorize execution')
    cap=batch['capture'];value=batch['prediction'];core=controller._active.framework.inner
    prediction=Prediction(cap['epoch'],cap['transaction_id'],cap['state'],spec['action'],
                          value['next_state'],value['consequence'])
    core.map=BoundPredictionMap(unwrap_map(core.map),prediction)
    pending=controller.begin_step(spec['action'])
    if getattr(pending,'action',None)!=spec['action']:
        raise RuntimeError('protected framework rejected scheduled action')
    if controller._source.reader().current() is not None:
        raise RuntimeError('receipt existed before world execution')
    receipt=controller.execute_pending()
    result=controller.submit_package(evidence(receipt))
    if not result.committed or not result.continued or result.status.value!='AUTHORIZED':
        controller.release(receipt);raise RuntimeError('protected publication rejected')
    core=controller._active.framework.inner
    package,record=controller._active.framework.packages[-1],core.memory.records[-1]
    if package.receipt is not receipt:
        raise RuntimeError('original protected receipt identity lost')
    receipt_value=_plain(asdict(receipt))
    event=dict(session_id=store.checkpoint['session_id'],stage='A',
        study_event=spec['event'],schedule=spec['schedule'],
        scheduled_observation_id=spec['observation_id'],
        phase=spec['phase'],execution_kind='OBSERVATION_CONTROLLED_EXECUTION',
        action_source='OBSERVATION_CONTROLLED',receipt=receipt_value,
        receipt_identity=list(receipt.identity()),
        receipt_provenance_sha256=digest(receipt_value),
        authorization_status=result.status.value,authorization_reason=result.reason,
        memory_record=_plain(asdict(record)),source_scope=dict(
            runtime_index=store.checkpoint['runtime_index'],imported_after_restart=False,
            source_identity=receipt.source_identity),
        external_regime_version=controller._active.world.regime_version,
        regime_model_visible=False)
    envelope=store.append('events','AUTHORIZED_REALIZED_EVENT',event)
    admission=memory.record(store,envelope,
        f'{spec["schedule"]}:{arm}:{spec["event"]}')
    row=dict(arm=arm,schedule=spec['schedule'],event=spec['event'],
        observation_id=spec['observation_id'],phase=spec['phase'],
        isolated_noise=spec['isolated_noise'],state=cap['state'],action=spec['action'],
        prediction=value,realized=dict(next_state=receipt.next_state,
            consequence=receipt.realized_consequence),
        consequence_correct=value['consequence']==receipt.realized_consequence,
        exact_correct=value==dict(next_state=receipt.next_state,
            consequence=receipt.realized_consequence),
        rule=batch['rule'],used_event_identities=batch['used_event_identities'],
        raw_eligible_memories=cap['retrieval'][spec['action']]['raw_eligible_memories'],
        model_supplied_memories=(cap['retrieval'][spec['action']]['memories_supplied_to_model']
                                 if arm=='M' else []),
        selected_consequences=cap['retrieval'][spec['action']]['selected_consequences'],
        window_consequences=batch.get('window_consequences'),
        grounded_state_before=batch.get('grounded_state'),
        mechanical_update_seconds=batch.get('update_seconds',0),
        serialized_state_bytes=batch.get('serialized_state_bytes',0),
        receipt_identity=list(receipt.identity()),
        receipt_provenance_sha256=event['receipt_provenance_sha256'],
        event_stream_sequence=envelope['sequence'],
        event_stream_head_sha256=sha256(canonical(envelope).encode()).hexdigest(),
        durable_admission=admission,model_calls=batch['model_calls'],
        context_tokens=batch['context_tokens'],model_seconds=batch['model_seconds'],
        status='AUTHORIZED')
    if arm=='U':
        memory.reconcile(store)
        row['grounded_state_after']=uncertainty_predict(memory,
            f"{cap['state']}:{spec['action']}",cap['state'])['state']
    store.append('training','GROUNDED_UNCERTAINTY_SCORED_EVENT',row)
    store.save(state=receipt.next_state,next_transaction_id=core.next_transaction_id,
               completed_step=True,attempted_decision=True)
    controller.release(receipt)
    return row
