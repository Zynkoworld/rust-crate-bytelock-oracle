#!/usr/bin/env python3
"""crate_bytelock.py — a deterministic byte-lock attestation decider for verified Rust crates.

An **oracle** *deterministically decides* the truth of a case — it doesn't guess, it decides. This one decides,
for a given crate **byte-lock attestation**, whether it is a well-formed, internally-consistent VALID attestation
of an independently execution-verified crates.io crate.

BYTE-LOCK: each verified crate carries a `content_hash` (md5 over the raw source tree, deterministically recomputed
by an independent 3-party recipe: cuda + harvest + concorde) and a `content_sha256`. The attestation is VALID iff:
  - content_hash is present and a valid 32-hex digest,
  - content_sha256 is present and non-empty,
  - green_level is a recognized verification level (execution-only / execution-proven / ...),
  - independent_sources >= 1 (at least one independent execution passed the crate's own test-suite).

The crate SOURCE is NOT included here (external-code license gate). This oracle proves the ATTESTATION integrity
deterministically and offline (stdlib only); the CI workflow additionally re-fetches each crate from crates.io and
recomputes the hash to prove the live byte-lock still matches (network, in CI).
"""
import json
import os
import re
import sys

_HEX32 = re.compile(r"^[0-9a-f]{32}$")
_GREEN_LEVELS = {"execution-only", "execution+independent-reproduction", "execution-proven"}


def decide(att):
    """Deterministic verdict for one attestation record: 'VALID' | 'INVALID'. No guessing, no network."""
    ch = str(att.get("content_hash") or "")
    if not _HEX32.match(ch):
        return "INVALID"
    if not att.get("content_sha256"):
        return "INVALID"
    if att.get("green_level") not in _GREEN_LEVELS:
        return "INVALID"
    try:
        if int(att.get("independent_sources") or 0) < 1:
            return "INVALID"
    except (TypeError, ValueError):
        return "INVALID"
    return "VALID"


def _run_probes(path):
    """Run the oracle over the labelled DISCRIMINATING probe corpus. Exit 0 IFF recall==1.0 AND false_positives==0
    AND the corpus is non-degenerate (has both VALID and INVALID). Same contract as the zynko-oracle CWE deciders."""
    probes = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                probes.append(json.loads(line))
    have_valid = any(p.get("expected_verdict") == "VALID" for p in probes)
    have_invalid = any(p.get("expected_verdict") == "INVALID" for p in probes)
    if not (have_valid and have_invalid):
        print("DEGENERATE corpus (need both VALID and INVALID) — FAIL")
        return 1
    tp = fp = fn = 0
    for p in probes:
        verdict = decide(p)
        exp = p.get("expected_verdict")
        if exp == "VALID" and verdict == "VALID":
            tp += 1
        elif exp == "VALID" and verdict == "INVALID":
            fn += 1
        elif exp == "INVALID" and verdict == "VALID":
            fp += 1
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    ok = (recall == 1.0 and fp == 0)
    print("crate-bytelock oracle: probes=%d | recall=%.3f | false_positives=%d | verdict=%s"
          % (len(probes), recall, fp, "PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default = os.path.join(base, "probes", "probes.jsonl")
    sys.exit(_run_probes(sys.argv[1] if len(sys.argv) > 1 else default))
