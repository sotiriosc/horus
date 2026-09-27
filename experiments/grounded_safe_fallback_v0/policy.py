"""Only the unresolved-decision branch differs from frozen H_ABSTAIN."""
from experiments.grounded_hybrid_controller_v0.policy import choose as parent_choose
from .protocol import ACTION_ORDER,ACCEPTABLE_MIN,CONSEQUENCE_MAX

def choose(assessments,arm):
    if arm in ('FORCED_GROUNDED','MODEL'):
        old=parent_choose(assessments,arm)
        return dict(**old,action_justified=False,optimality_established=False,
                    unresolved_relations=[])
    old=parent_choose(assessments,'HYBRID')
    unresolved=[a['relation'] for a in assessments if a['status']=='UNRESOLVED']
    if arm=='H_SAFE' and old['reason']=='ABSTAIN_UNRESOLVED_COULD_CHANGE_WINNER':
        acceptable=sorted((a for a in assessments if a['status']=='GROUNDED'
            and a['value']['consequence']>=ACCEPTABLE_MIN),
            key=lambda a:(-a['value']['consequence'],ACTION_ORDER.index(a['action'])))
        if acceptable:
            return dict(action=acceptable[0]['action'],reason='SAFE_GROUNDED_FALLBACK',
                action_justified=True,optimality_established=False,
                unresolved_relations=unresolved)
    selected=next((a for a in assessments if a['action']==old['action']),None)
    return dict(**old,
        action_justified=bool(selected and selected['status']=='GROUNDED' and
            selected['value']['consequence']>=ACCEPTABLE_MIN),
        optimality_established=bool(selected and selected['status']=='GROUNDED' and
            selected['value']['consequence']==CONSEQUENCE_MAX),
        unresolved_relations=unresolved)
