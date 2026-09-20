"""Fsync-before-progress journal, exclusive writer, atomic state and restart audit."""
import fcntl
import hashlib
import json
import os
from pathlib import Path

CAMPAIGN='HORUS_COMPOSITION_V2_REPLACEMENT_R1'
ZERO='0'*64


class DurabilityFailure(BaseException):
    """Must not be swallowed by scientific framework proposal-rejection handlers."""


def encoded(value):return json.dumps(value,sort_keys=True,indent=2)+'\n'
def compact(value):return json.dumps(value,sort_keys=True,separators=(',',':'))+'\n'
def digest(data):return hashlib.sha256(data).hexdigest()
def file_digest(path):return digest(Path(path).read_bytes())
def call_id(campaign,episode,decision,role):return f'{campaign}:e{episode:02d}:d{decision:02d}:{role}'


def fsync_dir(directory):
    try:
        fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(fd)
        finally:os.close(fd)
    except OSError as exc:raise DurabilityFailure(str(exc)) from exc


def atomic_write(path,value):
    path=Path(path);temporary=path.with_name(path.name+'.durable-new')
    try:
        with temporary.open('w') as stream:
            stream.write(encoded(value));stream.flush();os.fsync(stream.fileno())
        os.replace(temporary,path);fsync_dir(path.parent)
    except OSError as exc:raise DurabilityFailure(str(exc)) from exc


def append_line(stream,value):
    try:stream.write(compact(value));stream.flush();os.fsync(stream.fileno())
    except OSError as exc:raise DurabilityFailure(str(exc)) from exc


def require_durable(directory,root=None):
    p=Path(directory).resolve()
    if any(p.is_relative_to(Path(t)) for t in ('/tmp','/var/tmp','/dev/shm','/run')):
        raise ValueError('ephemeral evidence location forbidden')
    if root is not None and p.is_relative_to(Path(root).resolve()):raise ValueError('private archive must be outside public worktree')
    return p


class Journal:
    def __init__(self,directory,campaign=CAMPAIGN):
        self.directory=Path(directory);self.campaign=campaign;self.episode=None;self.decision=None
        self.previous=ZERO;self.sequence=0
        self.directory.mkdir(parents=True,exist_ok=False);fsync_dir(self.directory.parent)
        self.lock=(self.directory/'writer.lock').open('x');fcntl.flock(self.lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        self.stream=(self.directory/'journal.jsonl').open('x');self.stream.flush();os.fsync(self.stream.fileno());fsync_dir(self.directory)
        self.calls={}
        atomic_write(self.directory/'campaign-state.json',dict(campaign_id=campaign,status='REGISTERED_NO_CALLS',
            last_completed_episode=None,last_completed_decision=None,real_call_counts=dict(Explorer=0,Map=0,Recovery=0),episode_terminations={},ambiguous_calls=[]))

    def append(self,status,payload,call=None):
        row=dict(sequence=self.sequence,campaign_id=self.campaign,episode=self.episode,decision=self.decision,
                 call_id=call,status=status,payload=payload,previous_sha256=self.previous)
        row['record_sha256']=digest(compact(row).encode())
        append_line(self.stream,row);self.sequence+=1;self.previous=row['record_sha256']
        return row

    def snapshot(self,memory):
        text=encoded(memory);sha=digest(text.encode());folder=self.directory/'memory-snapshots'
        if not folder.exists():folder.mkdir();fsync_dir(self.directory)
        path=folder/(sha+'.json')
        if path.exists():assert path.read_text()==text
        else:atomic_write(path,memory)
        return dict(sha256=sha,snapshot_reference='memory-snapshots/'+path.name)

    def intent(self,call):
        cid=call_id(self.campaign,call['episode'],call['decision'],call['role'])
        if cid in self.calls:raise DurabilityFailure('duplicate call ID; automatic reissue forbidden')
        self.calls[cid]='INTENT'
        body=dict(model=call['model'],system=call['system'],prompt=call['exact_prompt'],stream=False,options=call['options'])
        payload=dict(episode=call['episode'],decision=call['decision'],role=call['role'],mapping=call['mapping'],
            seed=call['options']['seed'],current_authorized_state=call['current_state'],memory=self.snapshot(call['memory']),
            structured_projection=call['input'],exact_system=call['system'],exact_user=call['exact_prompt'],options=call['options'],
            request=body,exact_request_json=json.dumps(body))
        self.append('REQUEST_INTENT_RECORDED',payload,cid);return cid

    def response(self,cid,result):
        if self.calls.get(cid)!='INTENT':raise DurabilityFailure('response without one intent')
        self.append('RESPONSE_RECEIVED',result,cid);self.calls[cid]='RESPONSE'

    def parsed(self,call):
        cid=call_id(self.campaign,call['episode'],call['decision'],call['role'])
        if self.calls.get(cid)!='RESPONSE':raise DurabilityFailure('parse before durable response')
        self.append('PARSED',dict(parse_result=call['parsed'],parse_error=call['parse_error'],
            admission='REJECTED' if call['parsed'] is None else 'FINITE_PROPOSAL_ACCEPTED',call=call),cid)
        self.calls[cid]='PARSED'

    def finalize(self,row,calls,terminations):
        for c in calls:
            if (c['episode'],c['decision'])==(row['episode'],row['decision']):
                if self.calls.get(call_id(self.campaign,c['episode'],c['decision'],c['role']))!='PARSED':
                    raise DurabilityFailure('transaction finalized before all responses parsed')
        protected=row['probe']['after'];memory=protected['memory'];counts={role:sum(c['role']==role for c in calls) for role in ('Explorer','Map','Recovery')}
        payload=dict(row=row,protected_state_sha256=digest(encoded(protected).encode()),memory_sha256=digest(encoded(memory).encode()),
            continuation=row['probe']['authorization']['continued'],bounds=row['probe']['bounds'],real_call_counts=counts)
        self.append('TRANSACTION_FINALIZED',payload)
        stats={name:dict(bytes=(self.directory/name).stat().st_size,sha256=file_digest(self.directory/name)) for name in ('journal.jsonl','model-calls.jsonl','steps.jsonl') if (self.directory/name).exists()}
        completed=[int(ep) for ep,term in terminations.items() if term!='ONGOING']
        atomic_write(self.directory/'campaign-state.json',dict(campaign_id=self.campaign,status='TRANSACTION_FINALIZED',
            last_completed_episode=max(completed) if completed else None,last_finalized_episode=row['episode'],
            last_completed_decision=row['decision'],real_call_counts=counts,episode_terminations=terminations,
            protected_state_sha256=payload['protected_state_sha256'],memory_sha256=payload['memory_sha256'],
            evidence_files=stats,journal_records=self.sequence,journal_head_sha256=self.previous,ambiguous_calls=[]))

    def close(self):
        self.stream.close();fcntl.flock(self.lock,fcntl.LOCK_UN);self.lock.close()


def inspect(directory,expected_call=None):
    """Read-only recovery inspection. Never authorizes or performs model I/O."""
    directory=Path(directory);path=directory/'journal.jsonl';calls={};rows=[];previous=ZERO;error=None;finalized=set()
    data=path.read_bytes() if path.exists() else b''
    try:
        if data and not data.endswith(b'\n'):raise ValueError('incomplete trailing journal record')
        for line in data.splitlines():
            row=json.loads(line);sha=row.pop('record_sha256')
            if row['sequence']!=len(rows) or row['previous_sha256']!=previous or digest(compact(row).encode())!=sha:raise ValueError('journal chain mismatch')
            row['record_sha256']=sha;rows.append(row);previous=sha;cid=row['call_id'];status=row['status']
            if status=='REQUEST_INTENT_RECORDED':
                if cid in calls:raise ValueError('duplicate intent')
                calls[cid]='REQUEST_INTENT_RECORDED'
            elif status=='RESPONSE_RECEIVED':
                if calls.get(cid)!='REQUEST_INTENT_RECORDED':raise ValueError('response ordering')
                calls[cid]=status
            elif status=='PARSED':
                if calls.get(cid)!='RESPONSE_RECEIVED':raise ValueError('parse ordering')
                calls[cid]=status
            elif status=='TRANSACTION_FINALIZED':
                key=(row['episode'],row['decision']);finalized.add(key)
                for item in rows:
                    if item['call_id'] and (item['episode'],item['decision'])==key:
                        if calls[item['call_id']] not in ('PARSED','TRANSACTION_FINALIZED'):raise ValueError('unparsed finalized call')
                        calls[item['call_id']]='TRANSACTION_FINALIZED'
    except (ValueError,KeyError,TypeError) as exc:error=str(exc)
    ambiguous=[cid for cid,status in calls.items() if status=='REQUEST_INTENT_RECORDED']
    state=json.loads((directory/'campaign-state.json').read_text()) if (directory/'campaign-state.json').exists() else None
    state_matches=bool(state and (not rows or state.get('journal_head_sha256')==previous))
    return dict(journal_valid=error is None,journal_error=error,records=len(rows),call_states=calls,
        expected_call_status=calls.get(expected_call,'NOT_ISSUED') if expected_call else None,
        ambiguous_calls=ambiguous,finalized_decisions=len(finalized),campaign_state_matches_journal=state_matches,
        automatic_reissue_allowed=False,automatic_resume_allowed=False,
        disposition='STOP_INTERRUPTED_AMBIGUOUS' if error or ambiguous else 'INSPECT_COMPLETE_RECORDS_NO_AUTOMATIC_RERUN')
