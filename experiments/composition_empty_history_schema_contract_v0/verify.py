"""Zero-inference checks of registration, noncoercion and descriptive categories."""
import argparse
from copy import deepcopy
from .protocol import read, validate_registration, classify, metrics
from experiments.model_map_proposal_v0.adapter import INVALID, parse


def verify(reg):
    validate_registration(reg)
    rejected=0
    for raw in (*INVALID, '{"next_state":1,"consequence":"0"}',
                '{"next_state":1,"consequence":0,"consequence":1}',
                '{"next_state":1,"consequence":null}',
                '{"next_state":1,"consequence":false}'):
        try:parse(raw)
        except ValueError:rejected+=1
        else:raise AssertionError('non-contract response admitted')
    assert rejected==13
    entry=reg['plan'][0]
    cases=['{"next_state":true,"consequence":false}',
           '{"next_state":1,"consequence":2}',
           '{"next_state":1,"consequence":"K2"}',
           '{"next_state":1,"consequence":"K1 is executed."}',
           '{"next_state":1,"consequence":0}']
    counts=metrics([classify(entry,dict(response=s)) for s in cases])
    assert counts['valid']==1 and counts['integer_next_state']==4 and counts['in_domain_next_state']==4
    assert counts['integer_consequence']==2 and counts['in_domain_consequence']==1
    assert counts['opaque_token_consequence']==counts['prose_string_consequence']==1
    assert counts['other_categories']['out_of_domain_integer']==1
    changed=deepcopy(reg);changed['plan'][1]['request']['prompt']+=' '
    try:validate_registration(changed)
    except AssertionError:pass
    else:raise AssertionError('paired payload tamper accepted')
    print('PASS: 18-request registration, 13 noncoercion cases, five category cases, paired-byte tamper rejection. ZERO INFERENCE.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--registration',required=True)
    from pathlib import Path
    verify(read(Path(p.parse_args().registration)))
