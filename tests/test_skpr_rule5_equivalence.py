#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""Alias entrypoint — runs Phase-1 equivalence suite."""
from test_horus_bitexact import main

if __name__ == "__main__":
    raise SystemExit(main())
