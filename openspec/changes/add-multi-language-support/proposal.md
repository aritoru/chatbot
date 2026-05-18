## Why

AD&DHelp currently operates exclusively in English, limiting accessibility to Spanish, French, and Italian-speaking customers who may struggle to describe their AD&D problems fluently. Adding multi-language support broadens reach and improves Intake quality by letting Customers communicate in their native language.

## What Changes

- The Agent detects the Customer's language from their first message and conducts the entire Interview in that language.
- The opening greeting is generated in the detected language.
- TTS narration matches the detected language, selecting a voice appropriate for that locale.
- Supported languages at launch: English, Spanish, French, Italian.
- The Intake JSON records the detected language so support staff know which language the session was conducted in.
- Internal field values (enum strings, IRN) remain in English; only the conversational surface is localised.

## Capabilities

### New Capabilities

- `language-detection`: Detects the Customer's language from their first message and stores it on the Session. Supported values: `en`, `es`, `fr`, `it`. Defaults to `en` if detection is inconclusive.
- `localised-agent-conversation`: Agent conducts the full Interview — all questions, paraphrases, and the Confirmation Step — in the detected language.
- `localised-tts-voice`: TTS voice selection uses the detected language locale to pick the most appropriate voice from the browser's `speechSynthesis` API.

### Modified Capabilities

- `sage-speech-synthesis`: Voice selection logic extended to match detected language locale (currently hard-coded to `en-GB`).

## Impact

- **`back/services/agent.py`** — `get_opening_message` and `process_message` receive language context; `_build_system_prompt` injects a language directive instructing Claude to respond in the detected language.
- **`back/models/interview.py`** — add `Language` enum (`en`, `es`, `fr`, `it`) and `language` field to `Session` and `Intake`.
- **`back/services/storage.py`** — include `language` when serialising Intake to JSON.
- **`front/src/components/Chat.tsx`** — `pickVoice()` updated to match session language; language communicated from backend via existing message response or a new session-start field.
- No new API endpoints required; language is an internal Session property surfaced on the Intake.
