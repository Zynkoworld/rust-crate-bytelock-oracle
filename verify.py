#!/usr/bin/env python3
"""verify.py — CI gate for the Rust crate byte-lock attestation oracle. Runs the deterministic oracle over the
labelled DISCRIMINATING attestation corpus (VALID + planted-INVALID) and exits 0 IFF recall==1.0 AND
false_positives==0 AND the corpus is non-degenerate. No network, stdlib only."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "oracle"))
import crate_bytelock as oracle  # noqa: E402

if __name__ == "__main__":
    probes = os.path.join(os.path.dirname(os.path.abspath(__file__)), "probes", "probes.jsonl")
    sys.exit(oracle._run_probes(sys.argv[1] if len(sys.argv) > 1 else probes))
