"""Full reachable-history audit using unchanged publication.audit secret rules."""
from pathlib import PurePosixPath
from collections import defaultdict
import json,subprocess,sys
from publication.audit import FORBIDDEN_NAMES,FORBIDDEN_SUFFIXES,SENSITIVE_PATTERNS

def git(*args):return subprocess.check_output(['git',*args])
commits=git('rev-list','HEAD').decode().splitlines()
paths=defaultdict(set);scanned=0;failures=[]
for commit in commits:
    for entry in git('ls-tree','-r','-z',commit).split(b'\0'):
        if not entry:continue
        metadata,name=entry.split(b'\t',1);typ,oid=metadata.split()[1:3]
        if typ!=b'blob':continue
        path=name.decode();paths[oid.decode()].add(path);scanned+=1
        filename=PurePosixPath(path).name
        if filename in FORBIDDEN_NAMES or PurePosixPath(path).suffix in FORBIDDEN_SUFFIXES or filename.endswith('model-calls.jsonl'):
            failures.append('forbidden filename: '+path)
proc=subprocess.Popen(['git','cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
for oid,associated in paths.items():
    proc.stdin.write((oid+'\n').encode());proc.stdin.flush()
    header=proc.stdout.readline().split()
    assert len(header)==3 and header[0].decode()==oid and header[1]==b'blob'
    content=proc.stdout.read(int(header[2]));assert proc.stdout.read(1)==b'\n'
    for pattern in SENSITIVE_PATTERNS:
        if pattern.search(content):failures.extend('credential pattern: '+path for path in associated)
proc.stdin.close();assert proc.wait()==0
result=dict(status='PASS' if not failures else 'FAIL',mode='reachable_history',reachable_commits=len(commits),scanned_blobs=scanned,unique_blobs=len(paths),failures=sorted(set(failures)),audited_head=git('rev-parse','HEAD').decode().strip(),audit_method='All reachable commit/path names and all unique blobs; unchanged publication.audit rules')
print(json.dumps(result,indent=2,sort_keys=True))
sys.exit(0 if not failures else 1)
