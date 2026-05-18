## 1. Data Model

- [x] 1.1 Add `Language` enum (`EN = "en"`, `ES = "es"`, `FR = "fr"`, `IT = "it"`) to `back/models/interview.py`, following the same pattern as `UrgencyLevel`
- [x] 1.2 Add `language: Language = Language.EN` field to `Session` in `back/models/interview.py`
- [x] 1.3 Add `language` field to the `Intake` model so it is persisted in the Intake JSON

## 2. Tool Extension

- [x] 2.1 Add `"language"` to the `field_name` enum in the `extract_field` tool definition in `back/services/agent.py`
- [x] 2.2 Add a `Language` dispatch branch to `_apply_field`: map `"en"` → `Language.EN`, `"es"` → `Language.ES`, `"fr"` → `Language.FR`, `"it"` → `Language.IT`; ignore invalid values silently

## 3. System Prompt Integration

- [x] 3.1 Pass `session` (or `session.language`) into `_build_system_prompt` (currently takes `fields` and `status` only — add `language` parameter)
- [x] 3.2 In `_build_system_prompt`, inject a language directive when `session.language` is not `en`: e.g., "Respond in Spanish. All your messages to the customer must be in Spanish."
- [x] 3.3 Add a system prompt instruction telling Claude to call `extract_field(field_name="language", ...)` on the first Customer turn and on subsequent turns if language is still `en`
- [x] 3.4 Add system prompt rule: internal field values (`extract_field` arguments, enum values) must always be in English regardless of session language
- [x] 3.5 Update all `_build_system_prompt` call sites in `agent.py` to pass the language parameter

## 4. Language Lock Logic

- [x] 4.1 In `_apply_field`, implement language lock: only update `session.language` if current value is `Language.EN` (allow re-detection until first non-English value is set)

## 5. API Response

- [x] 5.1 Add optional `language` field to the `POST /sessions/{id}/messages` response schema in `back/routers/chat.py`
- [x] 5.2 Populate `language` in the response on the turn where `Session.language` first changes from `Language.EN` to a non-English value (or on turn 1 if English is confirmed)

## 6. Intake Persistence

- [x] 6.1 In `back/services/storage.py`, include `language` when serialising the Session to an Intake JSON file

## 7. Frontend — Language State

- [x] 7.1 Add `language` state (`useState<string>('en')`) to `Chat.tsx`
- [x] 7.2 Read `language` from the `POST /sessions/{id}/messages` response when present and update state
- [x] 7.3 Update `front/src/services/api.ts` types to include optional `language` in the message response

## 8. Frontend — Localised TTS Voice

- [x] 8.1 Add a locale map constant in `Chat.tsx`: `{ en: 'en-GB', es: 'es-ES', fr: 'fr-FR', it: 'it-IT' }`
- [x] 8.2 Update `pickVoice()` to accept the current language and select the first voice whose `lang` starts with the mapped locale prefix
- [x] 8.3 Fall back to `en-GB` / named preferred voices (Daniel, George, Arthur) if no locale-matching voice is found
- [x] 8.4 Call `pickVoice()` again when `language` state updates so the voice switches before the next utterance

## 9. Tests

- [x] 9.1 Add `_apply_field` tests in `back/tests/test_agent.py`: `extract_field(language, "es")` sets `session.language`; invalid code is ignored; language stays locked once non-English is set
- [x] 9.2 Add system prompt tests: language directive present for `es`/`fr`/`it`; absent for `en`
- [x] 9.3 Add router test: `language` field present in message response on first detection turn
- [x] 9.4 Add storage test: `language` field included in Intake JSON

## 10. Verification

- [x] 10.1 Run full test suite (`pytest back/tests/`) — all tests pass
- [ ] 10.2 Manual smoke test (Spanish): send "Hola" as first message, verify Agent replies in Spanish and TTS uses a Spanish voice
- [ ] 10.3 Manual smoke test (French): send "Bonjour" as first message, verify French Agent reply and French TTS voice
- [ ] 10.4 Manual smoke test (Italian): verify Italian reply and Italian TTS voice
- [ ] 10.5 Verify `GET /intakes/{irn}` response includes `language` field
