"""Prospectively specified synthetic mechanical mutations, never diagnostic cases."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from support import P,run,synthetic,normalize,replace,ids,pack,independent_checks,read,canonical_map
from dependency_audit import audit_source,LABELS

class Mechanics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.case=synthetic();cls.base,cls.raw=run(cls.case)
    def mutated(self,change):
        case=copy.deepcopy(self.case);change(case);out,raw=run(case);return case,out,raw
    def test_00_independent_inventories(self):
        self.assertTrue(all(independent_checks(self.case,self.base).values()))
        paths={e['json_pointer_relative_to_data']:e['exact_type'] for e in self.base['field_inventory'] if e['record_id']==self.case['records'][1]['id']}
        self.assertEqual(paths['/a~1b~0c/0'],'boolean');self.assertEqual(paths['/a~1b~0c/1'],'number')
    def test_reverse_records(self):
        c,o,_=self.mutated(lambda c:c['records'].reverse());self.assertEqual(normalize(self.base,self.case),normalize(o,c));independent_checks(c,o)
    def test_reverse_components(self):
        c,o,_=self.mutated(lambda c:c['components'].reverse());self.assertEqual(normalize(self.base,self.case),normalize(o,c))
    def test_reverse_versions(self):
        c,o,_=self.mutated(lambda c:c['versions'].reverse());self.assertEqual(normalize(self.base,self.case),normalize(o,c))
    def test_rename_opaque_labels(self):
        mapping={old:'z'+format(1000+i,'016x') for i,old in enumerate(sorted(ids(self.case)))};case=replace(self.case,mapping);out,_=run(case)
        self.assertEqual(normalize(self.base,self.case),normalize(out,case,{v:k for k,v in mapping.items()}));self.assertFalse(ids(out)&ids(self.case))
    def test_introduce_unknown(self):
        c,o,_=self.mutated(lambda c:c['records'][1]['data'].update(measurement='UNKNOWN'))
        self.assertEqual(len(o['unknown_locations']),1);self.assertEqual(o['unknown_locations'][0]['full_json_pointer'],'/records/1/data/measurement');self.assertEqual(c['records'][1]['data']['measurement'],'UNKNOWN')
    def test_remove_unknown(self):
        c=copy.deepcopy(self.case);c['records'][1]['data']['measurement']='UNKNOWN';run(c);c['records'][1]['data']['measurement']=1
        self.assertEqual(run(c)[1],self.raw)
    def test_switch_deployment(self):
        c,o,_=self.mutated(lambda c:c['records'][0]['data'].update(current_version=c['versions'][0]['id']))
        self.assertEqual(o['current_version'],c['versions'][0]['id']);self.assertIn(c['records'][4]['id'],o['current_record_ids']);self.assertIn(c['records'][1]['id'],o['historical_record_ids'])
        self.assertTrue(any(f['check']=='capture_snapshot_binding' and f['consistent'] is False for f in o['integrity_findings']))
    def test_break_event_equality(self):
        c,o,_=self.mutated(lambda c:c['records'][3]['data'].update(immutable_event_id=c['records'][0]['id']))
        self.assertEqual(o['capture_links'],[]);self.assertIn('missing_capture_output',[x['code'] for x in o['ambiguities']])
    def test_payload_conflict(self):
        c,o,_=self.mutated(lambda c:c['records'][3]['data']['captured_event_data'].update(measurement=2))
        f=next(f for f in o['integrity_findings'] if f['check']=='immutable_event_payload');self.assertIs(f['consistent'],False)
        self.assertEqual({v['path'] for v in f['differences'][0]['values']},{'/records/2/data/measurement','/records/3/data/captured_event_data/measurement'})
        self.assertEqual({v['value'] for v in f['differences'][0]['values']},{1,2})
    def test_digest_conflict(self):
        c,o,_=self.mutated(lambda c:c['records'][3]['data'].update(recorded_digest='changed'))
        self.assertTrue(any(f['check']=='digest_equality' and f['consistent'] is False for f in o['integrity_findings']))
    def test_remove_explicit_event_link(self):
        c,o,_=self.mutated(lambda c:c['records'][3]['data'].pop('immutable_event_id'))
        self.assertEqual(o['capture_links'],[]);self.assertIn('missing_event_link',[x['code'] for x in o['ambiguities']]);self.assertEqual(o['integrity_consistent'],'unknown')
    def test_multiple_input_candidates(self):
        def change(c):
            new=copy.deepcopy(c['records'][1]);new.update(id='z0000000000000099',at=19);c['records'].append(new)
        c,o,_=self.mutated(change);row=next(x for x in o['input_output_candidates'] if x['output_record_id']==c['records'][2]['id']);self.assertEqual(len(row['candidates']),2);self.assertTrue(row['ambiguous'])
    def test_remove_deployment(self):
        c,o,_=self.mutated(lambda c:c['records'].pop(0));self.assertIsNone(o['current_version']);self.assertEqual(o['current_record_ids'],[]);self.assertEqual(len(o['unresolved_record_ids']),5)
    def test_conflicting_deployment(self):
        def change(c):c['records'].append(dict(id='z0000000000000098',kind='deployment',data={'current_version':c['versions'][0]['id']}))
        c,o,_=self.mutated(change);self.assertIsNone(o['current_version']);self.assertIn('unresolved_current_deployment',[x['code'] for x in o['ambiguities']])
    def test_typed_payload_conflict(self):
        c,o,_=self.mutated(lambda c:c['records'][3]['data']['captured_event_data'].update(measurement=True));f=next(x for x in o['integrity_findings'] if x['check']=='immutable_event_payload');self.assertIs(f['consistent'],False)
    def test_unknown_payload(self):
        c,o,_=self.mutated(lambda c:c['records'][3]['data']['captured_event_data'].update(measurement='UNKNOWN'));f=next(x for x in o['integrity_findings'] if x['check']=='immutable_event_payload');self.assertEqual(f['consistent'],'unknown');self.assertEqual(o['integrity_consistent'],'unknown')
    def test_reorder_object_keys(self):
        def rev(v):
            if isinstance(v,dict):return {k:rev(x) for k,x in reversed(list(v.items()))}
            if isinstance(v,list):return [rev(x) for x in v]
            return v
        self.assertEqual(run(rev(self.case))[1],self.raw)
    def test_unknown_prose_substring(self):
        c,o,_=self.mutated(lambda c:c['records'][1]['data'].update(note='Contains UNKNOWN but is not that exact value'));self.assertEqual(o['unknown_locations'],[])
    def test_duplicate_record_id(self):
        c,o,_=self.mutated(lambda c:c['records'].append(copy.deepcopy(c['records'][1])));self.assertEqual(len(o['record_index']),9);self.assertIn('duplicate_record_id',[x['code'] for x in o['ambiguities']])
    def test_static_audit_rejects_forbidden_dependencies(self):
        for source in ['import os','open("grading.json")','x="version_selection"','x="z0000000000000001"',*[f'x={v!r}' for v in LABELS]]:self.assertEqual(audit_source(source)['status'],'FAIL')
        self.assertEqual(audit_source((P/'compiler.py').read_text())['status'],'PASS')
    def test_dynamic_guard_blocks_file_and_import(self):
        for source in ['def compile_evidence(case, contract):\n return open("/forbidden/materialized/grading.json").read()\n','import os\ndef compile_evidence(case, contract):\n return {}\n','import socket\ndef compile_evidence(case, contract):\n return {}\n']:
            with tempfile.TemporaryDirectory(prefix='compiler-boundary-test-') as d:
                path=Path(d);(path/'worker.py').write_bytes((P/'worker.py').read_bytes());(path/'compiler.py').write_text(source)
                with self.assertRaisesRegex(RuntimeError,'PermissionError'):run(self.case,path/'worker.py')
    def test_canonical_label_and_order_normalization(self):
        case=copy.deepcopy(self.case);case['records'][1]['data']['lookup']={'z0000000000000070':16,'z0000000000000071':23};case['records'][1]['data']['references']=['z0000000000000071','z0000000000000070']
        output,_=run(case);expected=normalize(output,case,canonical_map(case))
        mapping={old:'z'+format(2000-i,'016x') for i,old in enumerate(sorted(ids(case)))}
        renamed=replace(case,mapping)
        for name in ('records','components','versions'):renamed[name].reverse()
        result,_=run(renamed);self.assertEqual(normalize(result,renamed,canonical_map(renamed)),expected)
    def test_conflict_provenance_normalizes_across_labels(self):
        case=copy.deepcopy(self.case);case['records'][3]['data']['captured_event_data']['measurement']=2
        output,_=run(case);expected=normalize(output,case,canonical_map(case))
        mapping={old:'z'+format(3000-i,'016x') for i,old in enumerate(sorted(ids(case)))}
        renamed=replace(case,mapping);renamed['records'].reverse();result,_=run(renamed)
        self.assertEqual(normalize(result,renamed,canonical_map(renamed)),expected)
    def test_mutation_inventory_complete(self):
        for row in read(P/'mutation-contract.json')['tests']:self.assertTrue(hasattr(self,'test_'+row['id']))

if __name__=='__main__':unittest.main(verbosity=2)
