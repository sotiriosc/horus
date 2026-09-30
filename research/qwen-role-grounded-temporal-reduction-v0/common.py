import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
SEED=1846059237
BASE='01112fa7770ae885418d20e91a3227e15a8c3ba3'
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
 'trials':'All component, version and event bindings are already resolved. current_trial is the deployed trial; each non_current_trials entry is an already-bound older trial of the same mechanism and contract scope. List positions carry no identity-resolution task. There are no other trials or defects within this declared scope.',
 'knownness':'Whether the trial input is uniquely determined by its supplied evidence; no assumption that observations obey requirements.',
 'alternative_completion':'Whether an admissible input other than the reference input exists. The reference input is admissible in these states.',
 'observation_requirement':'Already-resolved equality of observed and required output at the reference input.',
 'evidence_sufficiency':'Whether all admissible inputs imply the same truth value for this trial observation violating its requirement. DETERMINATE means one truth value; UNDERDETERMINED means both violation and compliance remain possible.'}

ARMS=['A','B','C']
BARE='Select the diagnostic classification justified by the supplied primitive state.'
GENERIC="""You are currently performing the epistemic-reduction stage of a diagnostic system.
The supplied primitive propositions have already been established and are authoritative inputs for this stage.
Your responsibility is to determine what diagnostic status those propositions jointly justify.
Do not re-derive the primitive propositions.
Do not predict missing evidence.
Do not choose an action.
Do not modify the supplied state.
Your output represents the epistemic status justified by the supplied state."""
TEMPORAL="""Preserve distinctions between facts about the currently active system and facts about explicitly non-current prior states.
Evidence about a non-current state remains part of the diagnostic record even when the current state differs.
Do not collapse “no demonstrated defect anywhere” and “a demonstrated defect belongs only to a non-current state” into the same interpretation."""
CHARTERS={'A':BARE,'B':BARE+'\n\n'+GENERIC,'C':BARE+'\n\n'+GENERIC+'\n\n'+TEMPORAL}
