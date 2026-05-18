## ADDED Requirements

### Requirement: TTS voice selection SHALL match the session language locale

When a session language is detected and communicated to the frontend, `pickVoice()` SHALL select the best available voice for that language locale. The locale map is: `en` → `en-GB`, `es` → `es-ES`, `fr` → `fr-FR`, `it` → `it-IT`.

#### Scenario: Spanish voice selected for Spanish session

- **WHEN** the detected session language is `es`
- **THEN** `pickVoice()` selects the first available voice whose `lang` starts with `es`
- **AND** all subsequent Agent utterances use that voice

#### Scenario: French voice selected for French session

- **WHEN** the detected session language is `fr`
- **THEN** `pickVoice()` selects the first available voice whose `lang` starts with `fr`

#### Scenario: Italian voice selected for Italian session

- **WHEN** the detected session language is `it`
- **THEN** `pickVoice()` selects the first available voice whose `lang` starts with `it`

#### Scenario: Fallback to en-GB when no locale voice available

- **WHEN** the detected session language is `es`, `fr`, or `it`
- **AND** the browser has no voice matching that locale
- **THEN** `pickVoice()` falls back to the first `en-GB` or named preferred voice (Daniel, George, Arthur)
- **AND** if no preferred English voice is available, the browser default is used (no voice property set)

### Requirement: Voice SHALL be re-selected when session language is updated

When the frontend receives a detected language from the backend, `pickVoice()` SHALL be called again with the new language so the voice switches before the next Agent utterance is spoken.

#### Scenario: Voice switches on language detection

- **WHEN** the `POST /sessions/{id}/messages` response includes `"language": "fr"`
- **THEN** the frontend updates its stored language to `fr`
- **THEN** `pickVoice()` is called with locale `fr-FR`
- **THEN** the next Agent utterance uses the selected French voice
