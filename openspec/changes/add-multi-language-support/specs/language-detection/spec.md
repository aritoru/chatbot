## ADDED Requirements

### Requirement: System SHALL detect Customer language from their first message

On the Customer's first turn, Claude SHALL infer the language being written and call `extract_field(field_name="language", field_value=<code>)` with one of the supported language codes: `en`, `es`, `fr`, `it`. The detected language SHALL be stored in `Session.language`. If detection is inconclusive, Claude SHALL default to `en`.

#### Scenario: Spanish message detected

- **WHEN** the Customer's first message is written in Spanish (e.g., "Hola, tengo una pregunta sobre D&D")
- **THEN** Claude calls `extract_field(field_name="language", field_value="es")`
- **AND** `Session.language` is set to `es`

#### Scenario: French message detected

- **WHEN** the Customer's first message is written in French (e.g., "Bonjour, j'ai une question")
- **THEN** Claude calls `extract_field(field_name="language", field_value="fr")`
- **AND** `Session.language` is set to `fr`

#### Scenario: Italian message detected

- **WHEN** the Customer's first message is written in Italian (e.g., "Ciao, ho un problema con le regole")
- **THEN** Claude calls `extract_field(field_name="language", field_value="it")`
- **AND** `Session.language` is set to `it`

#### Scenario: English or inconclusive message

- **WHEN** the Customer's first message is in English or too short to detect (e.g., "hi", "hello")
- **THEN** `Session.language` remains `en` (default)

#### Scenario: Re-detection on second turn if still default

- **WHEN** `Session.language` is still `en` after turn 1 (inconclusive first message)
- **AND** the Customer's second message is clearly in a supported non-English language
- **THEN** Claude calls `extract_field(field_name="language", field_value=<code>)` to update the language
- **AND** `Session.language` is updated to the detected value

#### Scenario: Language locked after first non-English detection

- **WHEN** `Session.language` has been set to a non-English value (e.g., `es`)
- **AND** a subsequent Customer turn appears to be in a different language
- **THEN** `Session.language` is NOT updated — the first non-English detection is locked

### Requirement: Detected language SHALL be recorded on the Intake

When an Intake is created at the Confirmation Step, the `language` field SHALL be included in the Intake JSON, reflecting the value of `Session.language` at confirmation time.

#### Scenario: Intake created after Spanish session

- **WHEN** the Customer confirms their Intake and `Session.language` is `es`
- **THEN** the Intake JSON contains `"language": "es"`

#### Scenario: Intake created after default-language session

- **WHEN** `Session.language` was never updated from the default
- **THEN** the Intake JSON contains `"language": "en"`

### Requirement: Detected language SHALL be communicated to the frontend on the first Customer turn

The `POST /sessions/{id}/messages` response SHALL include a `language` field on the turn where language is first detected (i.e., when `Session.language` changes from its initial value or is confirmed as `en`). The field MAY be omitted on subsequent turns.

#### Scenario: Language field present on first reply

- **WHEN** the first Customer turn is processed and language is detected
- **THEN** the response body from `POST /sessions/{id}/messages` includes `"language": "<code>"`

#### Scenario: Language field absent on subsequent turns

- **WHEN** a subsequent Customer turn is processed and language has already been communicated
- **THEN** the response body does NOT need to include `language` (frontend retains the value from the first detection)
