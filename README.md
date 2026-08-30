# zynko-oracle · `rust-crate-bytelock-oracle`

**A deterministic, re-checkable byte-lock attestation decider for independently execution-verified Rust crates.**

An **oracle** *deterministically decides* the truth of a case — it doesn't guess, it decides. This one decides,
for a given crate **byte-lock attestation**, whether it is a well-formed, internally-consistent record of an
independently execution-verified [crates.io](https://crates.io) crate.

## What it proves
Each verified crate carries a **byte-lock**: a `content_hash` (over the raw source tree, deterministically
recomputed by an independent 3-party recipe — `cuda` + `harvest` + `concorde`) plus a `content_sha256`, together
with the execution result (`green_level`, the passing tests, and the count of `independent_sources`). The oracle
decides an attestation **VALID** iff:

- `content_hash` is a valid 32-hex digest, **and**
- `content_sha256` is present, **and**
- `green_level` is a recognized execution-verification level (`execution-only` / `execution+independent-reproduction` / `execution-proven`), **and**
- `independent_sources >= 1` (at least one independent run passed the crate's own test-suite).

## Proven
Measured on a **discriminating** probe corpus of **25 cases (22 VALID + 3 planted-INVALID)** — verified by
*running* the oracle, not asserted:

```
recall = 1.000    false_positives = 0    non-degenerate = yes  →  PASS
```

`verify.py` (stdlib only, no network) is the CI gate: it exits `0` **iff** `recall == 1.0` **and**
`false_positives == 0` **and** the corpus contains both VALID and INVALID (non-degenerate). See
`.github/workflows/verify.yml`.

## Grounding (honest)
- This is an **empirical** attestation oracle over a **byte-lock**, not a formal proof. It certifies that a crate
  was independently execution-verified (its own test-suite passed) and pins the source by cryptographic hash.
- The underlying corpus holds **5575** GOOD crate attestations; this repo ships a 25-case discriminating sample.
- **No external crate source is included** here. Per the `external-code-license-gate` (crate code is redistributed
  only on an explicit per-license decision), this repo ships **only cryptographic attestations** (name, version,
  hashes, verification result) — never the crates' source. Each crate remains under its own upstream license on
  crates.io.

## Re-verify a crate live
The byte-lock is reproducible end-to-end (requires the Rust toolchain + network):

```sh
# 1. fetch the exact pinned version from crates.io
cargo fetch  # or: curl https://crates.io/api/v1/crates/<name>/<version>/download
# 2. recompute content_hash over the raw source tree and compare to the attestation
# 3. run the crate's own test-suite
cargo test
```

A match on all three reproduces the VALID verdict.

## License
The oracle code in this repository is **Apache-2.0** (see `LICENSE`). The attested crates remain under their own
respective upstream licenses.
