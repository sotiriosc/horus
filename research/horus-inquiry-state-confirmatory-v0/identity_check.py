"""Read-only rehash of preserved A0 artifacts and runtime package identity."""
import time,importlib.metadata
from common import *
def verify():
 start=time.monotonic();expected=json.loads((ACTIVE/'identity-preflight.json').read_text());base=ADAPTER.parents[2]/expected['base_revision']
 for name,digest in expected['base_files_sha256'].items():assert filehash(base/name)==digest,name
 assert filehash(ADAPTER)==ADAPTER_SHA
 assert filehash(ADAPTER.parent/'adapter_config.json')==expected['adapter_configuration_sha256']
 assert {k:importlib.metadata.version(k) for k in expected['packages']}==expected['packages']
 expected.update(seconds=round(time.monotonic()-start,2),parameter_updates=0,limitations='Independent disk and package identity check; loaded base/adapter tensor fingerprints are checked at each worker launch.')
 return expected
if __name__=='__main__':print(canon(verify()))
