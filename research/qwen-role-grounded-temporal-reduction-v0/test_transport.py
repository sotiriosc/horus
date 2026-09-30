"""Zero-model HTTP qualification of the actual R2 orchestration and helper."""
import ast,http.server,json,socket,tempfile,threading,time,unittest
from pathlib import Path
from unittest.mock import patch,Mock
import transport
from transport import execute,http_request,load_requests,sha
from guard import P
B=P
from score import load_raw
from run_campaign import RealRuntime

class MockRuntime:
 def __init__(self,fail_at=None,final='MOCK ONLY\n{malformed',finish='length',health_status=200,erase_status=200,bad_envelope=False,drop=False,slots=1):
  self.requests=[];self.completions=0;self.starts=0;self.stops=0;self.running=False;self.release=threading.Event();owner=self
  class Handler(http.server.BaseHTTPRequestHandler):
   def log_message(self,*args):pass
   def handle_one(self):
    body=self.rfile.read(int(self.headers.get('Content-Length','0')));owner.requests.append((self.command,self.path,body))
    code=200
    if self.path=='/health':code=health_status;data={'status':'ok'}
    elif self.path=='/props':data={'total_slots':slots,'build_info':'QUALIFICATION_ONLY'}
    elif self.path=='/slots/0?action=erase':code=erase_status;data={'id_slot':0,'n_erased':getattr(owner,'erased',0)}
    elif self.path=='/slots':data=[{'id':0,'is_processing':False}]
    elif self.path=='/slow':owner.release.wait(2);data={}
    elif self.path=='/v1/chat/completions':
     owner.completions+=1
     if drop:self.connection.shutdown(socket.SHUT_RDWR);self.connection.close();return
     if fail_at==owner.completions:code=500;data={'error':'mock transport failure'}
     elif bad_envelope:data={'choices':[]}
     else:data={'choices':[{'message':{'content':final,'reasoning_content':'MOCK PRIVATE, NEVER SCIENCE'},'finish_reason':finish}],'usage':{'prompt_tokens':1,'completion_tokens':2}}
    else:code=404;data={'error':'mock not found'}
    raw=json.dumps(data).encode();self.send_response(code);self.send_header('Content-Length',str(len(raw)));self.end_headers()
    try:self.wfile.write(raw)
    except (BrokenPipeError,ConnectionResetError):pass
   do_GET=handle_one;do_POST=handle_one
  self.server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);self.host,self.port=self.server.server_address;self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
 def start(self,private):self.starts+=1;self.running=True;self.thread.start()
 def ready(self):return self.running
 def alive(self):return self.running
 def stop(self):
  self.stops+=1;self.release.set()
  if self.running:self.server.shutdown();self.thread.join(timeout=3)
  self.server.server_close();self.running=False

class Qualification(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.schedule,cls.payloads=load_requests(B)
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='epistemic-qualification-');self.root=Path(self.tmp.name);self.out=self.root/'QUALIFICATION_ONLY';self.out.mkdir();self.private=self.root/'private';self.runtime=None
 def tearDown(self):
  if self.runtime is not None and self.runtime.alive():self.runtime.stop()
  self.tmp.cleanup()
 def run_mock(self,n=2,**kw):
  self.runtime=MockRuntime(**kw);ids=self.schedule[:n]
  return execute(ids,{r:self.payloads[r] for r in ids},self.out,self.private,self.runtime,'QUALIFICATION_ONLY')
 def test_01_actual_readiness_path_regresses_shadowing(self):
  self.runtime=MockRuntime();self.runtime.start(self.private)
  status,headers,raw=http_request(self.runtime.host,self.runtime.port,'GET','/health')
  self.assertEqual(status,200);self.assertEqual(json.loads(raw),{'status':'ok'})
  self.assertEqual(transport.http_client.HTTPConnection.__module__,'http.client')
  self.assertNotIn('http',vars(transport));self.assertTrue(callable(transport.http_request))
 def test_02_full_50_path_qualification_no_model(self):
  result=self.run_mock(90);self.assertIsNone(result['stop']);self.assertEqual(result['completed_calls'],90);self.assertEqual(self.runtime.completions,90)
  paths=[x[1] for x in self.runtime.requests];self.assertEqual(paths[:3],['/health','/props','/slots'])
  self.assertEqual(paths[3:],['/slots/0?action=erase','/slots','/v1/chat/completions']*90)
  self.assertEqual(self.runtime.starts,1);self.assertEqual(self.runtime.stops,1);self.assertFalse(self.runtime.alive())
 def test_03_exact_saved_request_bytes(self):
  self.run_mock();sent=[x[2] for x in self.runtime.requests if x[1]=='/v1/chat/completions']
  self.assertEqual(sent,[self.payloads[r] for r in self.schedule[:2]])
  for rid in self.schedule:self.assertEqual(self.payloads[rid],(B/'materialized/requests'/(rid+'.json')).read_bytes())
 def test_04_malformed_completed_final_is_preserved(self):
  final=' \n```json\n{bad\n ';result=self.run_mock(final=final);self.assertEqual(result['completed_calls'],2)
  for rid in self.schedule[:2]:self.assertEqual((self.out/'raw/finals'/(rid+'.txt')).read_bytes(),final.encode())
  self.assertEqual(self.runtime.completions,2)
 def test_05_transport_failure_stops_remaining_no_retry(self):
  result=self.run_mock(3,fail_at=2);self.assertEqual(result['attempted_calls'],2);self.assertEqual(result['completed_calls'],1);self.assertEqual(result['statuses'][self.schedule[2]],'NOT_RUN');self.assertEqual(self.runtime.completions,2);self.assertEqual(self.runtime.stops,1)
 def test_06_duplicate_dispatch_rejected_before_start(self):
  self.runtime=MockRuntime();rid=self.schedule[0]
  with self.assertRaises(ValueError):execute([rid,rid],{rid:self.payloads[rid]},self.out,self.private,self.runtime,'QUALIFICATION_ONLY')
  self.assertEqual(self.runtime.starts,0);self.runtime.server.server_close()
 def test_07_rerun_refused(self):
  self.run_mock();self.runtime=MockRuntime()
  with self.assertRaises(FileExistsError):execute(self.schedule[:2],{r:self.payloads[r] for r in self.schedule[:2]},self.out,self.private,self.runtime,'QUALIFICATION_ONLY')
  self.assertEqual(self.runtime.starts,0);self.runtime.server.server_close()
 def test_08_previous_answer_never_enters_next_request(self):
  sentinel='MOCK-SECRET-RESPONSE-DO-NOT-FORWARD';self.run_mock(final=sentinel)
  for method,path,body in self.runtime.requests:
   if path=='/v1/chat/completions':self.assertNotIn(sentinel.encode(),body)
 def test_09_raw_hashes_readonly_before_any_scoring(self):
  self.run_mock();freeze=json.loads((self.out/'raw-freeze.json').read_bytes());self.assertFalse(freeze['scoring_has_occurred']);self.assertEqual(freeze['purpose'],'QUALIFICATION_ONLY')
  for name,want in freeze['sha256'].items():
   path=self.out/'raw'/name;self.assertEqual(sha(path.read_bytes()),want);self.assertEqual(path.stat().st_mode&0o222,0)
  self.assertFalse((self.out/'scores.json').exists());self.assertFalse((self.out/'raw/finals'/self.schedule[0]).exists())
 def test_10_mock_cannot_enter_scientific_score_host(self):
  self.run_mock()
  with self.assertRaisesRegex(AssertionError,'Mock evidence'):load_raw(self.out)
 def test_11_status_code_handling_without_retry(self):
  result=self.run_mock(health_status=400);self.assertEqual(result['attempted_calls'],0);self.assertIn('Readiness HTTP 400',result['stop']['reason']);self.assertEqual(len(self.runtime.requests),1);self.assertEqual(self.runtime.stops,1)
 def test_12_slot_clear_failure_no_completion(self):
  result=self.run_mock(erase_status=500);self.assertEqual(result['attempted_calls'],0);self.assertEqual(self.runtime.completions,0);self.assertIn('Slot erase HTTP 500',result['stop']['reason'])
 def test_13_json_envelope_error_stops(self):
  result=self.run_mock(bad_envelope=True);self.assertEqual(result['attempted_calls'],1);self.assertEqual(result['completed_calls'],0);self.assertEqual(self.runtime.stops,1)
 def test_14_connection_drop_no_retry_and_cleanup(self):
  result=self.run_mock(drop=True);self.assertEqual(result['attempted_calls'],1);self.assertEqual(self.runtime.completions,1);self.assertEqual(self.runtime.stops,1);self.assertTrue(result['server_terminated'])
 def test_15_actual_http_timeout(self):
  self.runtime=MockRuntime();self.runtime.start(self.private)
  with self.assertRaises(TimeoutError):http_request(self.runtime.host,self.runtime.port,'GET','/slow',timeout=.03)
  self.assertEqual(len(self.runtime.requests),1);self.runtime.release.set()
 def test_16_inference_imports_no_gold_or_scorer(self):
  for name in ('transport.py','run_campaign.py'):
   text=(P/name).read_text();tree=ast.parse(text)
   imports=[node.module for node in ast.walk(tree) if isinstance(node,ast.ImportFrom)]
   self.assertNotIn('scorer',imports)
   for forbidden in ('grading.json','case-manifest.json','matched-pairs.json','score_benchmark','world_generator','generator.generate'):self.assertNotIn(forbidden,text)
 def test_17_single_slot_required(self):
  result=self.run_mock(slots=2);self.assertEqual(result['attempted_calls'],0);self.assertIn('one isolated slot',result['stop']['reason']);self.assertEqual(self.runtime.stops,1)
 def test_18_real_lifecycle_exact_command_mocked_popen(self):
  runtime=RealRuntime();mock_slots=self.root/'mock-slots';mock_slots.mkdir();runtime.launch['slot_directory']=str(mock_slots);runtime.launch['command']=json.loads((P/'original-launch.json').read_bytes())['command'][:-1]+[str(mock_slots)];proc=Mock();proc.poll.side_effect=[None,None,0];proc.wait.return_value=0
  self.private.mkdir()
  with patch('run_campaign.subprocess.Popen',return_value=proc) as popen,patch('run_campaign.socket.socket') as sock:
   sock.return_value.__enter__.return_value.connect_ex.return_value=111
   runtime.start(self.private);runtime.stop()
   inherited=json.loads((P/'original-launch.json').read_bytes());self.assertEqual(popen.call_args.args[0],inherited['command'][:-1]+[runtime.launch['slot_directory']]);self.assertEqual(popen.call_args.kwargs['cwd'],inherited['cwd']);proc.terminate.assert_called_once();proc.wait.assert_called_once()
 def test_19_normal_truncation_is_data(self):
  result=self.run_mock(final='',finish='length');self.assertEqual(result['completed_calls'],2);self.assertIsNone(result['stop'])
 def test_20_payload_hash_mismatch_prevents_dispatch(self):
  mock_benchmark=self.root/'copied-benchmark';(mock_benchmark/'materialized/requests').mkdir(parents=True)
  (mock_benchmark/'materialized/render-manifest.json').write_bytes((B/'materialized/render-manifest.json').read_bytes())
  for rid,payload in self.payloads.items():(mock_benchmark/'materialized/requests'/(rid+'.json')).write_bytes(payload)
  (mock_benchmark/'materialized/requests'/(self.schedule[0]+'.json')).write_bytes(b'changed')
  with self.assertRaisesRegex(transport.TransportFailure,'hash mismatch'):load_requests(mock_benchmark)
 def test_21_error_body_preserved_before_status_failure(self):
  result=self.run_mock(erase_status=501);self.assertEqual(result['attempted_calls'],0)
  control=json.loads((self.out/'raw/control-metadata.json').read_bytes())
  error=next(x for x in control if x['http_status']==501)
  body=(self.private/error['private_body_file']).read_bytes();self.assertEqual(sha(body),error['response_sha256']);self.assertEqual(json.loads(body),{'id_slot':0,'n_erased':0})
  self.assertEqual(self.runtime.stops,1)
 def test_22_nonzero_erase_count_is_allowed(self):
  self.runtime=MockRuntime();self.runtime.erased=42
  ids=self.schedule[:2];result=execute(ids,{r:self.payloads[r] for r in ids},self.out,self.private,self.runtime,'QUALIFICATION_ONLY')
  self.assertEqual(result['completed_calls'],2)
  self.assertEqual(json.loads((self.out/'raw/metadata'/(ids[0]+'.json')).read_bytes())['n_erased'],42)
 def test_23_incorrect_science_namespace_rejected(self):
  self.runtime=MockRuntime()
  with self.assertRaises(ValueError):execute(self.schedule,self.payloads,self.out,self.private,self.runtime,'SCIENTIFIC_ROLE_TEMPORAL_V0')
  self.assertEqual(self.runtime.starts,0);self.runtime.server.server_close()

if __name__=='__main__':unittest.main(verbosity=2)
