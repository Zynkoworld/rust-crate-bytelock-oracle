# Changelog

## 0.1.0 — 2026-08-30
- Initial release: deterministic byte-lock attestation decider for independently execution-verified Rust crates.
- 25-case discriminating probe corpus (22 VALID + 3 planted-INVALID), non-degenerate.
- `verify.py` CI gate: recall=1.000, false_positives=0 → PASS. Stdlib only, no network.
- Attestation-only (no external crate source; per external-code-license-gate). Apache-2.0 oracle code.
