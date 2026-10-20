# ADR 0004 — STT provider choice (Bangla / Banglish)

- Status: proposed
- Date: 2026-10-13
- Phase: 00
- Related rules: R-AI-01, R-AI-05, R-AI-09

## Context

Voice messages must use the same text pipeline as typed chat (R-AI-09). Bangla and Banglish recognition quality varies widely across providers; wrong choice increases cost, latency, and guard-rule false positives.

## Options considered

1. **faster-whisper (large-v3, self-hosted)** — OSS; GPU/CPU cost under our control; quality TBD on real samples.
2. **Google Cloud Speech-to-Text** — strong multilingual; pay-per-minute; needs GCP credentials.
3. **Azure Speech** — competitive bn support; pay-per-minute; enterprise billing.
4. **Single provider without evaluation** — rejected (PDF §27.4).

## Decision (interim)

Run the **evaluation spike** defined in `ai-platform/tests/eval/stt/README.md` before locking production defaults. Compare candidates on **WER/CER**, **p95 latency**, and **cost per minute** on 30–50 **consented** real seller/customer-style samples (Bangla + Banglish + code-mixed).

**Production default:** *pending spike results* — update this ADR to `accepted` with the chosen primary and fallback adapter.

## Consequences

- **Positive:** Evidence-based provider choice; documents fallback if primary fails (R-AI-10).
- **Negative:** Spike delays Phase 13 voice work slightly if samples are hard to collect.
- **Follow-ups:** Complete sample corpus; implement `run_eval.py` (Phase 07/13); set `stt.default_provider` via settings registry only (R-CFG-01).
