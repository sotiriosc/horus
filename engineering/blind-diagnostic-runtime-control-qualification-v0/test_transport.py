"""Mock-only tests of exact control helper and body-before-validation preservation."""
import http.server,json,tempfile,threading,unittest
from pathlib import Path
from unittest.mock import patch
from qualify import ALLOWED,control_request,observe,sha
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='horus-control-mock-');self.output=Path(self.tmp.name);self.calls=[];self.code=200;self.raw=b'{"status":"ok"}';owner=self
  class Handler(http.server.BaseHTTPRequestHandler):
   def log_message(self,*args):pass
   def do_GET(self):self.reply()
   def do_POST(self):self.reply()
   def reply(self):
    body=self.rfile.read(int(self.headers.get('Content-Length','0')));owner.calls.append((self.command,self.path,body));self.send_response(owner.code);self.send_header('Content-Length',str(len(owner.raw)));self.end_headers();self.wfile.write(owner.raw)
  self.server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start();self.port=self.server.server_address[1]
 def tearDown(self):self.server.shutdown();self.thread.join();self.server.server_close();self.tmp.cleanup()
 def test_health_actual_http_path(self):
  result=observe(self.output,1,'GET','/health',self.port);self.assertEqual(result['http_status'],200);self.assertEqual((self.output/'1-response.txt').read_bytes(),self.raw)
 def test_501_body_preserved_before_raising(self):
  self.code=501;self.raw=b'{"error":{"code":501,"message":"mock complete body"}}'
  with self.assertRaises(RuntimeError):observe(self.output,4,'POST','/slots/0?action=erase',self.port)
  self.assertEqual((self.output/'4-response.txt').read_bytes(),self.raw);meta=json.loads((self.output/'4-metadata.json').read_bytes());self.assertEqual(meta['response_body_sha256'],sha(self.raw));self.assertEqual(meta['http_status'],501);self.assertEqual(len(self.calls),1)
 def test_generation_and_unapproved_endpoints_never_connect(self):
  with patch('qualify.http_client.HTTPConnection') as connection:
   for path in ('/v1/chat/completions','/completion','/completions','/v1/responses','/tokenize','/slots/0?action=restore','/slots/0?action=save'):
    with self.assertRaises(ValueError):control_request('127.0.0.1',self.port,'POST',path,b'{}')
   connection.assert_not_called()
 def test_prompt_body_rejected_before_connect(self):
  with patch('qualify.http_client.HTTPConnection') as connection:
   with self.assertRaises(ValueError):control_request('127.0.0.1',self.port,'POST','/slots/0?action=erase',b'{"prompt":"forbidden"}')
   connection.assert_not_called()
 def test_all_four_paths_and_erase_empty_slot(self):
  responses=[b'{"status":"ok"}',b'{"total_slots":1,"build_info":"b11242-526c43b8f"}',b'[{"id":0,"is_processing":false}]',b'{"id_slot":0,"n_erased":0}']
  for i,((method,path),body) in enumerate(zip(ALLOWED,responses),1):self.raw=body;observe(self.output,i,method,path,self.port)
  self.assertEqual([(m,p) for m,p,b in self.calls],list(ALLOWED));self.assertEqual(len(self.calls),4)
 def test_malformed_success_body_still_preserved(self):
  self.raw=b'not JSON\n'
  with self.assertRaises(json.JSONDecodeError):observe(self.output,1,'GET','/health',self.port)
  self.assertEqual((self.output/'1-response.txt').read_bytes(),self.raw);self.assertEqual(len(self.calls),1)
if __name__=='__main__':unittest.main(verbosity=2)
