# NEXUSAI — REALTIME VOICE CONVERSATION ROADMAP

**Status: PLANNED — NOT IMPLEMENTED.** This is architecture research, not a shipped feature.

## Core rule
Voice = interface layer only. Speech-to-text and text-to-speech feed OUR Core-01 brain. They must never silently replace it with a third-party AI chatbot.

## Architecture (target)
```
Mic → VAD → STT (local/open) → text → Core-01 inference → text → TTS → Speaker
                ↑ turn detection, interruption, language detect (EN/BN/Banglish)
```

## Components to research (license/resource check required)
- **STT:** Whisper (OpenAI, MIT — but verify "no external AI" policy: Whisper is a model, not API; running locally is allowed as interface? POLICY DECISION NEEDED — owner must decide if third-party speech models are acceptable as non-core interface components)
- Alternatives: Vosk (Apache-2.0, lightweight, offline), Coqui STT, wav2vec2 local
- **TTS:** Coqui TTS, Piper (MIT, fast CPU), eSpeak — Bengali voice support varies
- **VAD/turn-taking:** Silero VAD (MIT), browser Web Audio API

## Requirements checklist
- Real-time STT/TTS, streaming audio, turn detection, interruption, low latency
- Bengali + English + Banglish understanding (depends on Core-01 quality first)
- Language detection, speaker/mic controls, accessibility
- User consent, privacy, audio storage policy, offline options

## Dependencies
- Phase E (reasoning) + Phase H (local inference) should precede voice
- Bengali TTS voices are scarce — research needed
- Latency budget: STT <300ms, model <1s for short replies, TTS <300ms

## Current status
No voice code exists. Do not claim implemented.
