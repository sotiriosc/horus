"""Synthetic mechanical edge cases only; no scientific aggregation or model calls."""
import ast
import unittest
from pathlib import Path
from analyze import same, strict_json, witness_checks, invented_locations, failure_reason, code_counts, field_counts, FIELDS, D

class MechanicalTests(unittest.TestCase):
    def witness(self, **changes):
        base=dict(contract_evidence_id='z0000000000000001',cause_evidence_id='z0000000000000002',effect_evidence_id='z0000000000000003',decisive_evidence_id='z0000000000000002',decisive_field='/value',observed_value=1,required_value=2)
        base.update(changes);return base
    def test_types_are_not_coerced(self):
        self.assertFalse(same(True,1));self.assertFalse(same(1,1.0));self.assertTrue(same(1,1))
    def test_alternative_marginals_do_not_create_full_witness(self):
        first=self.witness();second=self.witness(decisive_field='/other',observed_value=7)
        mixed=self.witness(decisive_field='/other')
        fields,full,indices=witness_checks({'causal_mechanism':mixed},{'mechanism_witness':first,'mechanism_alternatives':[second]})
        self.assertTrue(all(fields.values()));self.assertFalse(full);self.assertEqual(indices,[])
    def test_full_alternative_and_unscored_description(self):
        first=self.witness();second=self.witness(observed_value=7);returned=dict(second,description='Unscored prose')
        fields,full,indices=witness_checks({'causal_mechanism':returned},{'mechanism_witness':first,'mechanism_alternatives':[second]})
        self.assertTrue(full);self.assertEqual(indices,[1])
    def test_missing_witness_is_all_mismatches(self):
        fields,full,indices=witness_checks({}, {'mechanism_witness':self.witness()})
        self.assertFalse(any(fields.values()));self.assertFalse(full)
    def test_original_strict_parser_rejects_duplicates_and_constants(self):
        for raw in ['{"a":1,"a":2}','{"a":NaN}','```json\n{}\n```']:
            with self.assertRaises(ValueError):strict_json(raw)
    def test_unknown_ids_have_key_and_value_locations_and_spans(self):
        good='z0000000000000001';bad='z0000000000000002'
        ids,locs=invented_locations({'a/b~c':[bad+' '+bad],bad:good},{'id':good})
        self.assertEqual(ids,[bad]);self.assertEqual(len(locs),3)
        self.assertEqual(locs[0]['path'],'/a~1b~0c/0');self.assertEqual(locs[-1]['kind'],'key')
        self.assertEqual(locs[1]['start'],18)
    def test_existing_wrong_category_id_is_not_invented(self):
        good='z0000000000000001';ids,locs=invented_locations({'evidence_ids':[good]},{'components':[{'id':good}]})
        self.assertEqual(ids,[]);self.assertEqual(locs,[])
    def test_failure_reasons_preserve_schema_id_boundary(self):
        row=dict(selected_classification=D,gold_classification=D,schema_valid=True,ids_valid=True)
        self.assertEqual(failure_reason(row),'none')
        self.assertEqual(failure_reason(dict(row,schema_valid=False,ids_valid=False)),'schema_or_id_validity_only')
        self.assertEqual(failure_reason(dict(row,selected_classification=None)),'classification_only')
        self.assertEqual(failure_reason(dict(row,selected_classification=None,ids_valid=False)),'both')
    def test_semantic_any_is_not_a_three_of_four_credit(self):
        rows=[dict(semantic_case_id='a',codes=['X']),dict(semantic_case_id='a',codes=[]),dict(semantic_case_id='b',codes=['X'])]
        self.assertEqual(code_counts(rows,['X','Y']),{'X':{'renderings':2,'semantic_cases':2},'Y':{'renderings':0,'semantic_cases':0}})
    def test_field_any_and_all_four_distinct(self):
        row=dict(gold_classification=D,semantic_case_id='a',affected_component_exact=True,structured_witness_exact=False,all_required_evidence_cited=False,witness_field_exact={k:False for k in FIELDS})
        rows=[dict(row) for _ in range(4)];rows[0]['structured_witness_exact']=True
        counts=field_counts(rows)['exact']['structured_witness_exact']
        self.assertEqual(counts,dict(renderings=1,semantic_cases_any=1,semantic_cases_all_four=0))
    def test_no_inference_or_scoring_calls(self):
        tree=ast.parse((Path(__file__).parent/'analyze.py').read_text())
        forbidden={'score_rendering','score_benchmark','execute','http_request','urlopen','requests','http','socket','openai'}
        for node in ast.walk(tree):
            if isinstance(node,ast.Call):
                name=node.func.id if isinstance(node.func,ast.Name) else node.func.attr if isinstance(node.func,ast.Attribute) else ''
                self.assertNotIn(name,forbidden)
            if isinstance(node,ast.Import):
                for n in node.names:self.assertNotIn(n.name.split('.')[0],forbidden)

if __name__=='__main__':unittest.main(verbosity=2)
