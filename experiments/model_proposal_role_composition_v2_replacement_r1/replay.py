"""Zero-inference replay compatibility for tuple fields serialized as JSON arrays.

The frozen v2 Replay compares raw Python tuples against decoded JSON lists. That
comparison was never exercised by v1's zero-commit campaign. Compare canonical
JSON representations of structured call metadata, preserving all JSON types and
values. All final evidence files still must match byte-for-byte in the frozen R1
runner. Scientific sources, raw responses and live recording are unchanged.
"""
import sys
from experiments.model_proposal_role_composition_v2.transport import Replay
from .durable import compact
from . import run


class RecordedJSONReplay(Replay):
    def generate(self,call):
        prior=self.rows[self.requests];self.requests+=1
        for key in call:
            if key not in ('raw_output','parsed','parse_error','transport_error','response_metadata'):
                assert compact(call[key])==compact(prior[key]),key
        return {k:prior[k] for k in ('raw_output','transport_error','response_metadata')}


def main():
    if '--live' in sys.argv or '--replay' not in sys.argv:
        raise SystemExit('This module permits recorded-response replay only; no live transport.')
    # Process-local transport selection only; run.main and every scientific source
    # remain frozen. RecordedJSONReplay performs no network requests.
    run.Replay=RecordedJSONReplay
    run.main()


if __name__=='__main__':main()
