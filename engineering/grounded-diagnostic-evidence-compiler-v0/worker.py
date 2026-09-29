"""Isolated stdlib-only transport; runtime accepts evidence plus frozen contract only."""
import builtins
import json
from pathlib import Path
import sys

source=Path(__file__).with_name('compiler.py').read_text()
module=compile(source,'<evidence-compiler>','exec')
request=json.loads(sys.stdin.read())
allowed={'case','contract'}
if set(request)!=allowed:raise ValueError('Unexpected compiler input envelope')

def blocked(event,args):
    if event=='open' or event=='import' or event.startswith(('os.','subprocess.','socket.','ctypes.')):
        raise PermissionError('Compiler runtime access denied: '+event)

sys.addaudithook(blocked)
def safe_import(name, *args, **kwargs):
    if name != 'json': raise PermissionError('Compiler import denied: '+name)
    return json

safe_builtins=dict(builtins.__dict__);safe_builtins['__import__']=safe_import
namespace={'__builtins__':safe_builtins}
exec(module,namespace)
answer=namespace['compile_evidence'](request['case'],request['contract'])
sys.stdout.write(json.dumps(answer,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n')
