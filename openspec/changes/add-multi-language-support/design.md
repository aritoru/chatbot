## Context

AD&DHelp's Agent is entirely Claude-driven: every turn regenerates the system prompt from Session state and sends it to `claude-sonnet-4-6`. Claude already handles multilingual text naturally — the only change required is telling Claude which language to use and passing that signal into the relevant components (system prompt, TTS voice picker).

The frontend TTS layer uses the Web Speech API (`speechSynthesis`). Voice selection is currently hard-coded to prefer `en-GB` voices (Daniel, George, Arthur). Extending it to pick the right locale voice per language requires knowing the session language on the frontend.

## Goals / Non-Goals

**Goals:**
- Detect Customer language from their first message and persist it on the Session.
- Conduct the full Interview in the detected language (all Agent turns).
- Select a TTS voice matching the detected language locale.
- Record `language` on the Intake for support staff visibility.
- Support: English (`en`), Spanish (`es`), French (`fr`), Italian (`it`).

**Non-Goals:**
- Mid-session language switching — language is detected once from the first Customer turn and locked for the Session.
- Translation of internal enum values, field names, or the IRN.
- UI language localisation (labels, buttons, error messages stay in English).
- Dynamic voice download or fallback to a remote TTS service.

## Decisions

### Decision 1: Claude detects language, stored as a Session field

**Chosen**: Add a `Language` enum (`en`, `es`, `fr`, `it`) and `language: Language = Language.EN` field to `Session`. Claude infers the language from the Customer's first message and calls `extract_field(field_name="language", field_value="es")` (extending the existing pattern). The detected language is injected into `_build_system_prompt` as a language directive on every turn.

**Alternatives considered**:
- *Dedicated `set_language(code)` tool*: cleaner semantically, but adds surface area; the `extract_field` pattern already handles this class of inference (same as `game_system`, `frustration_signal`).
- *Browser-side `navigator.language` detection*: available without an API call, but reflects the browser locale, not the language the Customer actually writes in — these diverge frequently.
- *Separate lightweight detection API call*: adds latency and cost for something Claude already does well as a side effect of reading the first message.

**Rationale**: Reusing `extract_field` keeps the tool surface minimal. Claude reads the first Customer message and infers language as part of its normal turn processing, at zero extra cost.

### Decision 2: Language is communicated to the frontend via the session-start response

**Chosen**: `POST /sessions` returns `{session_id, message, language}`. The frontend stores the `language` value and passes it to `pickVoice()`. This is the earliest the language can be known — the opening greeting is generated first, so the language must be inferred before or during that call.

**Problem**: Language detection from the Customer's first message happens in `process_message`, but the opening greeting is generated in `get_opening_message` before any Customer turn. The opening greeting is always in English unless we make the opening language-aware.

**Resolution**: For the opening greeting, default to English. Language detection fires on the Customer's *first reply*, not the initial greeting. The frontend receives the detected language in the first `POST /sessions/{id}/messages` response and switches the TTS voice at that point. This means the opening greeting is always spoken in English; all subsequent Agent turns use the detected voice.

**Alternatives considered**:
- *Ask language preference explicitly before the Interview*: adds friction; Claude can detect naturally.
- *Detect from browser `Accept-Language` header*: same locale-vs-writing-language problem as navigator.language.

### Decision 3: `language` field added to the message response, not a new endpoint

**Chosen**: `POST /sessions/{id}/messages` response gains an optional `language` field that is populated on the first turn (when detection fires) and omitted on subsequent turns. Frontend reads it once, stores it in state.

**Rationale**: No new endpoint, no breaking change to existing callers — the field is additive.

### Decision 4: TTS voice locale map hard-coded in the frontend

**Chosen**: A static map in `Chat.tsx`: `{ en: 'en-GB', es: 'es-ES', fr: 'fr-FR', it: 'it-IT' }`. `pickVoice()` uses the active language to find the best matching voice. Falls back to `en-GB` if no matching voice is found.

**Rationale**: The Web Speech API voice list is browser/OS-dependent; a simple locale-prefix match (`v.lang.startsWith(locale)`) is more reliable than name matching across languages.

## Risks / Trade-offs

- **Short first message inconclusive** → Customer writes "hi" or a single word; Claude cannot detect language. Mitigation: default to `en`, re-detect on the next Customer turn if still `en` and the new message gives a clear signal.
- **Mixed-language messages** → Customer switches language mid-session. Accepted trade-off: language is locked after first detection. The Agent stays in the detected language; the Customer can clarify if needed.
- **TTS voice unavailable for locale** → Browser has no Spanish/French/Italian voice installed. Mitigation: graceful fallback to `en-GB`; no error thrown.
- **Opening greeting always English** → First Agent message is in English before language is known. Accepted trade-off for this iteration; a future change could pass a `?lang=` hint from the browser.

## Open Questions

- Should `language` appear in `GET /intakes` (summary list) or only `GET /intakes/{irn}` (full record)? (Propose: full record only — same pattern as `frustration_signal`.)
- Re-detection: if Claude fails to detect on turn 1 (returns `en` by default) and detects `es` on turn 2, should `language` update? (Propose: yes — update until the first non-`en` detection, then lock.)
