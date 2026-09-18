# SPDX-License-Identifier: CERN-OHL-S-2.0
"""NFE-13 pack/unpack + encode/decode aligned to format_zoo + skpr_golden."""
from __future__ import annotations

import math
import sys
from pathlib import Path

_SIM = Path(__file__).resolve().parent
if str(_SIM) not in sys.path:
    sys.path.insert(0, str(_SIM))

from format_zoo import nfe_dec as _nfe_dec_fields
from format_zoo import nfe_enc as _nfe_enc_fields

EXP_W, MANT_W = 6, 6
EXP_MASK, MANT_MASK = 0x3F, 0x3F
MANT_MAX = 0b111111
NFE_BIAS = 32


def pack(sign: int, exp: int, mant: int) -> int:
    return ((sign & 1) << 12) | ((exp & EXP_MASK) << 6) | (mant & MANT_MASK)


def unpack(e13: int) -> tuple[int, int, int]:
    return (e13 >> 12) & 1, (e13 >> 6) & EXP_MASK, e13 & MANT_MASK


def encode_float(v: float) -> int:
    s, e, f = _nfe_enc_fields(float(v))
    return pack(s, e, f)


def decode_float(e13: int) -> float:
    s, e, f = unpack(e13)
    if e == 0:
        return -0.0 if s else 0.0
    return _nfe_dec_fields(s, e, f)


def encode_array(values) -> list[int]:
    return [encode_float(float(v)) for v in values]


def decode_array(words: list[int]) -> list[float]:
    return [decode_float(w) for w in words]


def exponents(words: list[int]) -> list[int]:
    return [(w >> 6) & EXP_MASK for w in words]
