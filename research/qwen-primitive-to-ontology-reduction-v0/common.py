import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
SEED=739182647
BASE='67053bb802a7851e91b4e7aeb675a687875b8115'
CLASSES=['SUPPORTED_CURRENT_DEFECT','NO_SUPPORTED_DIAGNOSIS','INSUFFICIENT_EVIDENCE','HISTORICAL_DEFECT_NOT_CURRENT','INVALID_OR_CONTRADICTORY_EVIDENCE']
DEFS=['Available current evidence supports a specific active structural or mechanical defect and distinguishes it from materially plausible benign alternatives.','The internally valid evidence is sufficient within the declared contract/input scope and supports no current defect. Unusual or undesirable behavior alone is insufficient.','The evidence is internally valid but a current defect and a materially plausible benign explanation remain observationally indistinguishable.','A defect is demonstrated for an older version, while supplied current mechanisms and observations show it is no longer active within the stated scope.','The supplied evidence package contains incompatible immutable, version, capture or provenance facts and cannot support a valid operational diagnosis.']
D,N,U,T,X=CLASSES
SCHEMA={'type':'object','properties':{'classification':{'enum':CLASSES}},'required':['classification'],'additionalProperties':False}
def raw(v):return (json.dumps(v,indent=2,ensure_ascii=True)+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,v):p.write_bytes(raw(v))
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
SCOPE={
 'package':'The two mark assertions are independent of trial inputs. same_referent compares their immutable subjects; equal_value compares their asserted values. consistency is the already-resolved consistency of the entire package, including other immutable provenance assertions.',
 'trials':'All component, version and event bindings are already resolved. current_trial is the deployed trial; historical_trial, when present, is an older trial of the same mechanism and contract scope. There are no other trials or defects within this declared scope.',
 'knownness':'Whether the trial input is uniquely determined by its supplied evidence; no assumption that observations obey requirements.',
 'alternative_completion':'Whether an admissible input other than the reference input exists. The reference input is admissible in these states.',
 'observation_requirement':'Already-resolved equality of observed and required output at the reference input.',
 'evidence_sufficiency':'Whether all admissible inputs imply the same truth value for this trial observation violating its requirement. DETERMINATE means one truth value; UNDERDETERMINED means both violation and compliance remain possible.'}
