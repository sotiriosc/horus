import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
BASE='19c50c06caf99736acbf5c728da0148840e665a5'
SEED=1264087953
VALUES=['YES','NO','UNKNOWN']
FIELDS=['current_violation','prior_violation']
SCHEMA={'type':'object','properties':{k:{'enum':VALUES} for k in FIELDS},'required':FIELDS,'additionalProperties':False}
COMBINATIONS=[('YES','NO'),('NO','YES'),('NO','NO'),('UNKNOWN','YES'),('UNKNOWN','NO'),('YES','YES'),('NO','UNKNOWN'),('UNKNOWN','UNKNOWN')]
EXPECTED_COUNTS={'YES/NO':4,'NO/YES':12,'NO/NO':4,'UNKNOWN/YES':4,'UNKNOWN/NO':3,'YES/YES':3,'NO/UNKNOWN':3,'UNKNOWN/UNKNOWN':3}
FORBIDDEN_LABELS=['SUPPORTED_CURRENT_DEFECT','NO_SUPPORTED_DIAGNOSIS','INSUFFICIENT_EVIDENCE','HISTORICAL_DEFECT_NOT_CURRENT','INVALID_OR_CONTRADICTORY_EVIDENCE']
SCOPE={
 'trials':'The current_trial is explicitly deployed. Every non_current_trials entry is an already-bound prior trial within the same mechanism and contract scope. No opaque identifiers, unlisted trials or further evidence need to be resolved.',
 'knownness':'Whether the trial input is uniquely determined; observations do not imply that requirements were followed.',
 'alternative_completion':'Whether another admissible input besides the reference input exists. The reference input is admissible.',
 'observation_requirement':'The already-resolved equality of observed and required output at the reference input.',
 'evidence_sufficiency':'Whether all admissible inputs give the same truth value for the trial observation violating its requirement: DETERMINATE means one truth value; UNDERDETERMINED means both violation and compliance remain possible.',
 'consistency_scope':'Package consistency concerns separate immutable provenance assertions. It does not alter the supplied resolved trial propositions used for these two temporal fields, including when the package is CONTRADICTORY.'}
INSTRUCTION='Construct the two temporal violation fields from the supplied resolved primitive facts. Return only the JSON object satisfying the output schema.'
DEFINITIONS="""Output semantics:
YES = the supplied determinate facts establish that the relevant observation violates its requirement.
NO = the supplied determinate facts establish that the relevant observation complies with its requirement.
UNKNOWN = the supplied facts do not determine whether violation or compliance holds.
current_violation refers only to the explicitly current/deployed trial.
prior_violation summarizes whether at least one explicitly non-current prior trial has a demonstrated violation under the declared scope.
For multiple prior trials:
- YES if at least one prior trial is determinately violating.
- NO if all prior trials are determinately compliant.
- UNKNOWN if no prior violation is established and at least one prior trial remains underdetermined."""
def raw(x):return (json.dumps(x,indent=2,ensure_ascii=True)+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,x):p.write_bytes(raw(x))
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def semantic_signature(s):
 # Excludes formatting, schema spelling, explanatory text, identity decorations and identifiers.
 hist=s.get('non_current_trials')
 if hist is None:hist=[] if s.get('historical_trial') is None else [s['historical_trial']]
 return canonical([s['package']['consistency'],s['current_trial'],sorted(hist,key=canonical)])
