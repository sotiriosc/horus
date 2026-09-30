import json,subprocess,os,time,http.client,hashlib
from pathlib import Path
import jsonschema
P=Path('/tmp/horus-epistemic-primitive-cross-model-comparator-v0/research/epistemic-primitive-cross-model-comparator-v0');Q=Path('/tmp/horus-ministral-reasoning-qualification-v0');Q.mkdir(mode=0o700)
def sha(b):return hashlib.sha256(b).hexdigest()
def request(path,obj=None):
 c=http.client.HTTPConnection('127.0.0.1',18085,timeout=600)
 try:
  c.request('POST' if obj is not None else 'GET',path,body=json.dumps(obj).encode() if obj is not None else None,headers={'Content-Type':'application/json'});r=c.getresponse();b=r.read();assert r.status==200;return json.loads(b)
 finally:c.close()
launch=json.loads((P/'original-launch.json').read_bytes());req=json.loads((P/'decoding.json').read_bytes());schema=json.loads((P/'schemas.json').read_bytes())['IDENTITY_EQUALITY'];req.update(messages=[{'role':'system','content':'This is a synthetic native reasoning-channel transport test. Use the native [THINK] and [/THINK] channel before the final JSON response.'},{'role':'user','content':'Compute 173 times 239. Return same_referent true if the result is 41347, otherwise false. Return equal_value false. This is synthetic arithmetic, not evidence classification.'}],response_format={'type':'json_object','schema':schema});(Q/'request.json').write_text(json.dumps(req,indent=2)+'\n')
with (Q/'server.log').open('xb') as log:
 proc=subprocess.Popen(launch['command'],cwd=launch['cwd'],env={k:v for k,v in os.environ.items() if not k.startswith(('LLAMA_ARG_','LLAMA_LOG_'))},stdout=log,stderr=subprocess.STDOUT)
 try:
  start=time.monotonic()
  while b'listening on http://127.0.0.1:18085' not in (Q/'server.log').read_bytes():
   assert proc.poll() is None and time.monotonic()-start<180;time.sleep(.2)
  result=request('/v1/chat/completions',req);body=json.dumps(result,indent=2).encode();(Q/'envelope.json').write_bytes(body);m=result['choices'][0]['message'];reason=m.get('reasoning_content');assert isinstance(reason,str) and reason.strip(),'Native reasoning was not separated';obj=json.loads(m['content']);jsonschema.Draft7Validator(schema).validate(obj);assert obj=={'same_referent':True,'equal_value':False}
  report=dict(status='PASS',purpose='SYNTHETIC_NON_SCIENTIFIC_ONLY',synthetic_calls=1,scientific_calls=0,request_sha256=sha((Q/'request.json').read_bytes()),envelope_sha256=sha(body),reasoning_sha256=sha(reason.encode()),final_sha256=sha(m['content'].encode()),reasoning_separated=True,schema_valid=True,usage=result['usage'],native_reasoning_optional=True,semantic_benchmark_messages_unchanged=True)
  (P/'reasoning-qualification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
 finally:
  proc.terminate()
  try:proc.wait(timeout=30)
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
