import copy,json,unittest
from generate import P,ARMS,CLASSES
from score import grade,strict,summarize,interpretation,normalize_state
from verify import independent_operation,reduction_normal_form
class ScoringChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.gold=json.loads((P/'materialized/gold.json').read_bytes())
 def rows(self,changes=None):
  rows=[];changes=changes or {}
  for g in self.gold:
   for arm in ARMS:
    obj=copy.deepcopy(changes.get((g['index'],arm),g[arm]));r=grade(json.dumps(obj),arm,g[arm]);r.update(world_id=g['world_id'],arm=arm,gold_class=g['class'],family=g['family'],composition=g['composition']);rows.append(r)
  return rows
 def result(self,changes=None):return summarize(self.rows(changes),self.gold)
 def incorrect(self,index,arm,field=None):
  g=self.gold[index];obj=copy.deepcopy(g[arm])
  if arm=='O':obj['results'][0]='deliberately incorrect fixture'
  elif arm=='S':
   field=field or 'target_component_id';obj[field]=['f0000000000000000'] if isinstance(obj[field],list) else 'f0000000000000000'
  else:obj['classification']=next(c for c in CLASSES if c!=g['class'])
  return obj
 def test_strict_json(self):
  for s in ('NaN','Infinity','1e999','{"a":1,"a":2}','{} trailing','```json\n{}\n```'):
   with self.assertRaises(ValueError):strict(s)
 def test_perfect_all_arms(self):
  s=self.result();self.assertTrue(all(s['gates'].values()));self.assertEqual(s['registered_interpretation'],['ALL_ARMS_SUPPORTED_WITHIN_CASES'])
 def test_O_reverse_is_not_correct(self):
  want={'results':['31','43']};r=grade('{"results":["43","31"]}','O',want);self.assertFalse(r['correct']);self.assertEqual(r['error_category'],'REVERSED_RESULT_ORDER')
 def test_O_family_floor_and_total(self):
  for indices,expect in (([0,1,2],True),([0,1,2,3],False),([0,10],False)):
   s=self.result({(i,'O'):self.incorrect(i,'O') for i in indices});self.assertEqual(s['gates']['O'],expect)
 def test_S_order_irrelevant(self):
  g=self.gold[0]['S'];obj=copy.deepcopy(g)
  for k,v in obj.items():
   if isinstance(v,list):v.reverse()
  for row in obj['capture_groups']:row['source_record_ids'].reverse()
  self.assertTrue(grade(json.dumps(obj),'S',g)['correct'])
 def test_S_duplicates_not_repaired(self):
  g=self.gold[0]['S'];obj=copy.deepcopy(g);obj['in_service_receipt_ids']*=2;r=grade(json.dumps(obj),'S',g);self.assertFalse(r['schema_valid']);self.assertFalse(any(r['fields'].values()))
 def test_S_partial_state_no_joint_rescue(self):
  r=grade(json.dumps(self.incorrect(0,'S')),'S',self.gold[0]['S']);self.assertFalse(r['correct']);self.assertEqual(sum(r['fields'].values()),8)
 def test_S_field_gate_independent_of_joint(self):
  diff={(0,'S'):self.incorrect(0,'S','target_component_id'),(1,'S'):self.incorrect(1,'S','in_service_build_id'),(2,'S'):self.incorrect(2,'S','in_service_receipt_ids')};s=self.result(diff);self.assertEqual(s['arms']['S']['correct'],17);self.assertTrue(s['gates']['S'])
  same={(i,'S'):self.incorrect(i,'S') for i in (0,1,2)};s=self.result(same);self.assertEqual(s['arms']['S']['correct'],17);self.assertFalse(s['gates']['S'])
 def test_R_E_total_and_class_floor(self):
  for arm in ('R','E'):
   for indices,expect in (([0,1,2],True),([0,1,2,3],False),([0,5],False)):
    s=self.result({(i,arm):self.incorrect(i,arm) for i in indices});self.assertEqual(s['gates'][arm],expect)
 def test_schema_failure_not_confusion_credit(self):
  obj=copy.deepcopy(self.gold[0]['R']);obj['extra']=True;s=self.result({(0,'R'):obj});self.assertEqual(s['arms']['R']['confusion_matrix'][self.gold[0]['class']]['INVALID_OUTPUT'],1)
 def test_registered_patterns(self):
  cases=[((True,False,True,False),'A_BINDING_PATTERN'),((True,True,False,False),'B_EPISTEMIC_PATTERN'),((True,True,True,False),'C_COMPOSITION_PATTERN'),((False,False,True,True),'D_MULTIPLE_ISOLATED_LIMITATIONS'),((False,True,True,False),'OTHER_MIXED_PATTERN')]
  for bits,label in cases:self.assertEqual(interpretation(dict(zip(ARMS,bits))),[label])
 def test_end_to_end_failure_despite_isolated_success(self):
  s=self.result({(i,'E'):self.incorrect(i,'E') for i in range(4)});self.assertEqual(s['registered_interpretation'],['C_COMPOSITION_PATTERN']);self.assertEqual(s['associations']['all_isolated_correct_E_wrong']['count'],4);self.assertEqual(s['associations']['all_isolated_correct_E_wrong']['denominator'],20)
 def test_end_to_end_correct_despite_isolated_error(self):
  s=self.result({(0,'O'):self.incorrect(0,'O'),(0,'S'):self.incorrect(0,'S')});self.assertEqual(s['associations']['E_correct_despite_isolated_error']['count'],1);self.assertEqual(s['associations']['at_least_two_isolated_errors']['count'],1)
 def test_conditional_denominators(self):
  s=self.result({(0,'O'):self.incorrect(0,'O'),(1,'S'):self.incorrect(1,'S'),(1,'R'):self.incorrect(1,'R')});self.assertEqual(s['associations']['O_correct_S_wrong']['denominator'],19);self.assertEqual(s['associations']['O_correct_S_wrong']['count'],1);self.assertEqual(s['associations']['S_correct_R_wrong']['count'],0)
 def test_R_E_matched_transition(self):
  s=self.result({(0,'E'):self.incorrect(0,'E'),(1,'R'):self.incorrect(1,'R')});self.assertEqual(s['R_E_comparison']['recognized_class_disagreements'],2);self.assertEqual(s['R_E_comparison']['transitions']['correct_to_wrong'],1);self.assertEqual(s['R_E_comparison']['transitions']['wrong_to_correct'],1)
 def test_independent_operation_vectors(self):
  self.assertEqual(independent_operation(1,{'word':'abba'}),'q1');self.assertEqual(independent_operation(2,{'edges':[[0,1],[1,2]],'start':0}),'11100');self.assertEqual(independent_operation(3,{'left':'sail','right':'salt'}),'2');self.assertEqual(independent_operation(4,{'x':143,'y':221}),'13');self.assertEqual(independent_operation(6,{'a':[2,1,3],'b':[1,2]}),'2,5,5,6');self.assertEqual(independent_operation(8,{'n':9,'k':4}),'126')
 def test_reduction_normalization_preserves_operand_order(self):
  state={'trials':[{'in_service':True,'creation_order':2,'source_capture':{'input_declarations':[{'claimed_input':{'a':[2,1,3]}}]},'admissible_completions':[]}]};other=copy.deepcopy(state);other['trials'][0]['source_capture']['input_declarations'][0]['claimed_input']['a']=[1,2,3];self.assertNotEqual(reduction_normal_form(state),reduction_normal_form(other))
if __name__=='__main__':unittest.main(verbosity=2)
