# Phase 13 — Voice Message Pipeline (STT)

> **Prompt header:** Apply `docs/GLOBAL_RULES.md`. Phase: 13. Modules: `conversations` (voice stage), `channels` (media download), `usage`; uses `AIClient.transcribe`. No git/Docker.

## Goal
Customers send voice notes; the platform validates audio, transcribes (Bangla/Banglish-capable provider), and feeds the transcript into the **same** Guard → Rules → Engine pipeline. Out-of-rule or failed transcripts never reach the LLM. STT is metered.

## Prerequisites
Phase 12 (complete text pipeline), Phase 07 STT providers, ADR 0004 (provider choice), Phase 10 (Messenger attachments).

## Requirements covered
PDF locked decision 1–2, §11.7, §27.1 (steps 1–8), §27.2, §27.3 (meter STT, never STT on blocked/closed, short max duration), §27.4 (provider behind interface, retention), §27.5 checklist, §23 media type in panel, §17 STT success rate.

## Scope
**In:** voice pipeline stage placed **before** guard, pre-check (skip STT if conversation BLOCKED/CLOSED-policy or AI disabled → store only), download from channel (allow-listed hosts), validate format/size/duration, store audio in object storage with `retention_until`, enqueue `stt` job, transcribe via `AIClient`, persist transcript + confidence + provider, low-confidence/empty handling, usage metering, resume pipeline with transcript as text, voice badge + transcript in UI, retention purge.
**Out:** image recognition (future).

## Tasks
1. Stage `VoiceStage`: if media_type=voice → pre-check guard status → validate (`voice.allowed_formats`, `voice.max_file_mb`, `voice.max_duration_seconds`) → enqueue STT (job id `stt:{message_id}`) → pipeline pauses for this message.
2. STT job: audio from storage → (optional transcode via ffmpeg to provider format) → `AIClient.transcribe(language_hint=bn)` → `voice_transcripts` row → event `conversations.voice.transcribed` → pipeline resumes from guard with normalised text.
3. Failure/low confidence (< `voice.min_confidence`) or empty → `voice.low_confidence_action`: soft "please type" template or human alert; **no LLM**; log `error_events` for provider failures.
4. Usage: STT seconds + request recorded (from AI platform event); metering mode per P08.
5. Retention: cron purges audio after `retention.audio_days`, transcript after `retention.transcript_days`.
6. UI: voice badge, audio player (if retained), transcript toggle (`voice.show_transcript`), same take-over/urgency controls; sandbox supports uploading/recording audio.
7. Metrics: STT success rate, avg confidence, latency, cost per minute.

## DB changes
`voice_transcripts` (message_id, audio_key, duration, transcript, confidence, language, provider, model, retention_until, purged_at).

## Settings & templates
Tenant (bounded): `voice.enabled` (entitlement), `voice.max_duration_seconds`, `voice.min_confidence`, `voice.low_confidence_action`, `voice.show_transcript`. Platform: `voice.allowed_formats`, `voice.max_file_mb`, provider routing `ai.routing.voice.stt`. Templates: `voice.please_type_message` (bn/en).

## Tests
PDF §27.2 rows for voice; blocked conversation → no STT call; oversize/too long rejected; low confidence path; transcript enters same pipeline (assert identical decisions as typed text); metering; retention purge.

## Acceptance criteria
- [ ] Voice question about a product gets the same answer as the typed question
- [ ] Out-of-rule voice → no LLM, seller action applied, transcript stored
- [ ] STT units visible in usage; success rate on dashboard

## Rules checklist
- [ ] R-AI-03/09 · R-SEC-04/10 · R-CFG-01 · tests · PROGRESS_LOG · no git/Docker
