import unittest
from .protocol import select_route,source_for_model_choice,ACTIONS

def a(kind='UNSEEN',value=None,relation_type='DETERMINISTIC'):
    return dict(kind=kind,relation_type=relation_type,
        established_value=None if value is None else dict(consequence=value,next_state=0))

class PolicyTests(unittest.TestCase):
    def test_established_ceiling_overrides_unknown(self):
        x=dict(ADVANCE=a('ESTABLISHED',-1),HOLD=a('ESTABLISHED',1),RETREAT=a())
        y=select_route(x)
        self.assertEqual((y['route'],y['action'],y['candidates']),('MECHANICAL','HOLD',['HOLD']))
    def test_all_established_choose_max(self):
        x=dict(ADVANCE=a('ESTABLISHED',-1),HOLD=a('ESTABLISHED',0),RETREAT=a('ESTABLISHED',0))
        self.assertEqual(select_route(x)['action'],'HOLD')
    def test_mixed_excludes_inferior_known(self):
        x=dict(ADVANCE=a('ESTABLISHED',-1),HOLD=a('ESTABLISHED',0),RETREAT=a())
        y=select_route(x)
        self.assertEqual(y['candidates'],['HOLD','RETREAT'])
        self.assertEqual(source_for_model_choice(y,x,'RETREAT'),'MODEL_FOR_UNSEEN')
        self.assertEqual(source_for_model_choice(y,x,'HOLD'),'SAFE_GROUNDED_FALLBACK')
    def test_empirical_not_point_fact(self):
        x=dict(ADVANCE=a('ESTABLISHED',-1),HOLD=a('EMPIRICALLY_STABLE',relation_type='EMPIRICAL'),RETREAT=a())
        self.assertEqual(select_route(x)['candidates'],list(ACTIONS))
if __name__=='__main__':unittest.main()
