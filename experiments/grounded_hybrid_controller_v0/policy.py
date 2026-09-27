"""A finite consequence-only selector. Assessments retain epistemic status."""
from .protocol import ACTION_ORDER,CONSEQUENCE_MAX

def choose(assessments,arm):
    ordered=sorted(assessments,key=lambda a:ACTION_ORDER.index(a['action']))
    if arm=='HYBRID':
        grounded=[a for a in ordered if a['status']=='GROUNDED']
        ceiling=[a for a in grounded if a['value']['consequence']==CONSEQUENCE_MAX]
        if ceiling:
            return dict(action=ceiling[0]['action'],reason=('GROUNDED_AT_REGISTERED_CEILING_WITH_UNRESOLVED_OTHER_ACTION'
                if any(a['status']=='UNRESOLVED' for a in ordered)
                else 'GROUNDED_AT_REGISTERED_CEILING'))
        if any(a['status']=='UNRESOLVED' for a in ordered):
            return dict(action=None,reason='ABSTAIN_UNRESOLVED_COULD_CHANGE_WINNER')
        scored=sorted(ordered,key=lambda a:(-a['value']['consequence'],
            a['status']!='GROUNDED',ACTION_ORDER.index(a['action'])))
        return dict(action=scored[0]['action'],reason=('SELECT_GROUNDED_POINT' if
            scored[0]['status']=='GROUNDED' else 'SELECT_MODEL_GENERALIZATION'))
    scored=sorted(ordered,key=lambda a:(-a['value']['consequence'],ACTION_ORDER.index(a['action'])))
    return dict(action=scored[0]['action'],reason=('MODEL_POINT_MAX' if arm=='MODEL' else 'FORCED_POINT_MAX'))
