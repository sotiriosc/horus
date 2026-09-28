import json,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from horus.live import SessionStore
from .fixtures import build
from .worker import run,validate_contexts,payload
from .analyze import analyze
from .protocol import ORDERS,PAIRS,SYSTEMS,PRIMARY_CALLS

class GroundedFake:
    def generate(self,request):
        context=json.loads(request['prompt'])
        assessments=context['grounded_assessments']
        best=max((a for a in context['available_actions'] if assessments[a]['kind']=='ESTABLISHED'),
            key=lambda a:assessments[a]['established_value']['consequence'])
        return dict(raw_output=json.dumps({'selected_action':best}),transport_error=None,
            response_metadata=dict(prompt_eval_count=50,eval_count=9))

class Tests(unittest.TestCase):
    def test_protected_fixtures_matched_prompts_and_no_diagnostic_execution(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp);doc=build(root);validate_contexts(doc)
            for pair,(a,b) in PAIRS.items():
                for order in ORDERS:
                    for condition in SYSTEMS:
                        x=payload(doc,pair,order,condition,a)
                        y=payload(doc,pair,order,condition,b)
                        self.assertEqual({k for k in x if x[k]!=y[k]},{'grounded_assessments'})
            result=run(root,doc,GroundedFake())
            self.assertEqual(result['calls'],PRIMARY_CALLS)
            self.assertEqual(result['diagnostic_world_executions'],0)
            with SessionStore(root/'inference/session',True) as store:
                self.assertEqual(len(store.records['events']),0)
            audit=analyze(root,doc)
            self.assertEqual(audit['classification'],'GROUNDING_SENSITIVE_WITHOUT_DIRECTIVE')
            self.assertEqual(audit['valid_action_outputs'],36)

if __name__=='__main__':unittest.main()
