"""Fail-closed source/dependency audit; forbidden tokens exist here solely for absence tests."""
import ast
import json
from pathlib import Path
import re
P=Path(__file__).resolve().parent
LABELS=['SUPPORTED_CURRENT_DEFECT','NO_SUPPORTED_DIAGNOSIS','INSUFFICIENT_EVIDENCE','HISTORICAL_DEFECT_NOT_CURRENT','INVALID_OR_CONTRADICTORY_EVIDENCE']
FAMILIES=['version_selection','authority_precedence','entity_binding','publication_update','operation_idempotence','boundary_comparison']
FORBIDDEN=['grading.json','scores.json','secondary-analysis.json','scorer','matched-pairs','postmortem','used_config','returned_value','command_issued']
CALLS={'open','eval','exec','compile','__import__','getattr','setattr','delattr','globals','locals','vars','input','breakpoint'}
def audit_source(source,case_ids=()):
    errors=[]
    for value in LABELS+FAMILIES+FORBIDDEN+list(case_ids):
        if value in source:errors.append('forbidden literal: '+value)
    if re.search(r'\bz[0-9a-f]{16}\b',source):errors.append('opaque ID literal')
    tree=ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            if any(n.name!='json' or n.asname for n in node.names):errors.append('non-allowlisted import')
        if isinstance(node,ast.ImportFrom):errors.append('from-import denied')
        if isinstance(node,ast.Attribute) and node.attr.startswith('_'):errors.append('reflection attribute')
        if isinstance(node,ast.Call):
            name=node.func.id if isinstance(node.func,ast.Name) else node.func.attr if isinstance(node.func,ast.Attribute) else ''
            if name in CALLS:errors.append('forbidden call: '+name)
    return dict(status='PASS' if not errors else 'FAIL',errors=sorted(set(errors)))
def main():
    fixtures=json.loads((P/'fixture-manifest.json').read_bytes());ids={x['render_id'] for x in fixtures['entries']}|{x['semantic_group'] for x in fixtures['entries']}
    result=audit_source((P/'compiler.py').read_text(),ids)
    assert result['status']=='PASS',result
    print(json.dumps(dict(**result,compiler_allowed_imports=['json'],case_and_group_ids_scanned=len(ids),operational_gold_access=False,opaque_id_literals=0)))
if __name__=='__main__':main()
