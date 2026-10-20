# STT evaluation spike (Bangla / Banglish)

> Phase 00 — plan and sample collection. Implementation of `run_eval.py` lands with AI platform providers (Phase 07) and voice pipeline (Phase 13).

## Goal

Choose a primary STT adapter (see ADR `docs/adr/0004-stt-provider-choice.md`) using real audio, not synthetic demos.

## Corpus (target: 30–50 clips)

| Requirement | Detail |
|-------------|--------|
| Consent | Written consent from speakers; no production customer data without approval |
| Languages | Standard Bangla, Banglish (Latin script), code-mixed shop phrases |
| Duration | 3–30 seconds each; include background noise samples |
| Format | WAV or FLAC, 16 kHz mono preferred; store outside git (e.g. encrypted drive or MinIO test bucket) |
| Ground truth | Human transcript per clip in `manifest.csv` |

### `manifest.csv` columns

```text
clip_id,filepath,locale,script,reference_text,notes
```

- `script`: `bn` | `latin` | `mixed`
- Store clips under `ai-platform/tests/eval/stt/samples/` (gitignored) or a documented local path.

## Providers to compare

| Provider | Adapter (future) | Notes |
|----------|------------------|-------|
| faster-whisper large-v3 | `ai_platform.providers.stt.faster_whisper` | Self-host; measure GPU vs CPU |
| Google Cloud STT | `ai_platform.providers.stt.google` | `bn-BD` / `bn-IN` locale tests |
| Azure Speech | `ai_platform.providers.stt.azure` | `bn-IN` / `bn-BD` |

## Metrics

| Metric | How |
|--------|-----|
| WER / CER | `jiwer` or equivalent on normalized text (lowercase, strip punctuation) |
| Latency | p50 / p95 wall time per clip + per minute of audio |
| Cost | Estimated $/min at expected monthly volume |
| Confidence | Distribution vs guard thresholds (empty/garbage transcript rate) |

## Script plan (`run_eval.py`)

Planned CLI (not yet implemented):

```bash
cd ai-platform
uv run python tests/eval/stt/run_eval.py \
  --manifest tests/eval/stt/manifest.csv \
  --providers faster_whisper,google,azure \
  --output tests/eval/stt/results/latest.json
```

Steps the script will perform:

1. Load manifest; skip missing files with a clear error.
2. For each provider, transcribe each clip (cold + warm timing optional).
3. Compute WER/CER vs `reference_text`.
4. Aggregate latency and cost estimates.
5. Write JSON + markdown summary for ADR 0004.

## Sample collection checklist

- [ ] Consent template approved
- [ ] 10 clips — clean Bangla
- [ ] 10 clips — Banglish / Latin
- [ ] 10 clips — noisy environment (market, street)
- [ ] 10 clips — product names, prices, addresses
- [ ] Manifest reviewed by native speaker
- [ ] Results recorded; ADR 0004 moved to **accepted**

## Privacy

Do not commit audio or transcripts containing PII. Use synthetic shop scenarios where live customer audio is unavailable.
