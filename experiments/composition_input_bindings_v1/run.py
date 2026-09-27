"""Zero-call campaign and exact recorded synthetic response replay."""
import argparse
import json
from pathlib import Path
from .campaign import check, encoded


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--replay',type=Path)
    args=parser.parse_args()
    if args.output.resolve().is_relative_to(Path(__file__).resolve().parents[2]):
        raise ValueError('full evidence must remain outside public tree')
    replay=json.loads((args.replay/'synthetic-calls.json').read_text()) if args.replay else None
    result,details,calls=check(replay)
    # A is the campaign verdict, conditional on verification.json subsequently
    # recording exact replay, source preservation and all historical regressions.
    args.output.mkdir(parents=True,exist_ok=False)
    for name,value in (('results.json',result),('transactions.json',details),('synthetic-calls.json',calls)):
        content=encoded(value)
        if args.replay: assert content==(args.replay/name).read_text(),name
        (args.output/name).write_text(content)
    print(encoded(result))


if __name__=='__main__':main()
