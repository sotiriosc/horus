"""Fail a publication branch if staged or reachable blobs contain forbidden private material."""
from argparse import ArgumentParser
from pathlib import PurePosixPath
import re,subprocess

FORBIDDEN_NAMES={'authority.key','model-calls.private.jsonl','events.jsonl',
    'training-records.jsonl','checkpoint.json','memory.sqlite3'}
FORBIDDEN_SUFFIXES={'.sqlite3','.safetensors','.pem','.p12','.pfx','.env','.key'}
SENSITIVE_PATTERNS=(
    re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(rb'\b(?:ghp_|github_pat_|sk-)[A-Za-z0-9_-]{20,}'),
    re.compile(rb'Bearer\s+[A-Za-z0-9._~-]{20,}'),
    re.compile(rb'(?i)(?:api[_-]?key|access[_-]?token|password|client[_-]?secret)\s*[:=]\s*["\x27][A-Za-z0-9_./+-]{20,}["\x27]'),
)

def git(*args):return subprocess.check_output(['git',*args])

def audit(staged=False):
    if staged:
        paths=[x.decode() for x in git('ls-files','--cached','-z').split(b'\0') if x]
        blobs=[(p,git('show',':'+p)) for p in paths]
        commits=[]
    else:
        commits=git('rev-list','HEAD').decode().splitlines()
        blobs=[];seen=set()
        for commit in commits:
            tree=git('ls-tree','-r','-z','--name-only',commit).split(b'\0')
            for raw in tree:
                if not raw:continue
                p=raw.decode()
                if (commit,p) in seen:continue
                seen.add((commit,p));blobs.append((p,git('show',f'{commit}:{p}')))
    failures=[]
    for path,content in blobs:
        filename=PurePosixPath(path).name
        if filename in FORBIDDEN_NAMES or PurePosixPath(path).suffix in FORBIDDEN_SUFFIXES or filename.endswith('model-calls.jsonl'):
            failures.append(f'forbidden filename: {path}')
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(content):failures.append(f'credential pattern: {path}')
    return dict(status='PASS' if not failures else 'FAIL',mode='staged' if staged else 'reachable_history',
        reachable_commits=len(commits),scanned_blobs=len(blobs),failures=failures)

if __name__=='__main__':
    import json,sys
    p=ArgumentParser();p.add_argument('--staged',action='store_true');a=p.parse_args()
    result=audit(a.staged);print(json.dumps(result,indent=2,sort_keys=True))
    sys.exit(0 if result['status']=='PASS' else 1)
