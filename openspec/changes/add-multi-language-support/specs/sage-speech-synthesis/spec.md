## MODIFIED Requirements

### Requirement: Sage voice selection
The speech synthesis SHALL attempt to use a voice matching the current session language locale, falling back to the preferred English sage voices (Daniel, George, Arthur / en-GB) and then to the browser default.

#### Scenario: Preferred voice available for session language

- **WHEN** `speechSynthesis.getVoices()` contains a voice whose `lang` starts with the session language locale prefix (e.g., `es` for Spanish)
- **THEN** the first matching voice SHALL be used for all utterances in that session

#### Scenario: No voice for session language — English fallback

- **WHEN** no voice is found matching the session language locale
- **THEN** `pickVoice()` SHALL fall back to the first voice whose name includes "Daniel", "George", "Arthur", or whose `lang` starts with "en-GB"

#### Scenario: No preferred voice available at all

- **WHEN** no voice matches either the session language locale or the English fallback preferences
- **THEN** the utterance SHALL use the browser default voice (no `voice` property set)

#### Scenario: Voices load asynchronously (Chrome)

- **WHEN** `getVoices()` returns an empty array on initial call
- **THEN** the component SHALL listen for the `voiceschanged` event and re-select the voice when voices become available
