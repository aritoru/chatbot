## ADDED Requirements

### Requirement: Agent SHALL conduct the Interview in the detected language

From the turn on which `Session.language` is first set to a non-English value, every subsequent Agent response SHALL be in that language. The opening greeting is always in English (language is unknown before the first Customer turn); all Agent turns from turn 1 onward SHALL be in the detected language.

#### Scenario: Agent replies in Spanish after Spanish first message

- **WHEN** `Session.language` is `es`
- **THEN** all Agent responses from that turn onward SHALL be written in Spanish
- **AND** the Agent SHALL ask for missing Interview fields in Spanish

#### Scenario: Agent replies in French after French first message

- **WHEN** `Session.language` is `fr`
- **THEN** all Agent responses SHALL be written in French

#### Scenario: Agent replies in Italian after Italian first message

- **WHEN** `Session.language` is `it`
- **THEN** all Agent responses SHALL be written in Italian

#### Scenario: Agent replies in English when language is en

- **WHEN** `Session.language` is `en`
- **THEN** Agent responses SHALL be in English (existing behaviour, unchanged)

### Requirement: Agent system prompt SHALL include a language directive

`_build_system_prompt` SHALL include a language instruction block whenever `Session.language` is set. The directive SHALL instruct Claude to respond in the specified language for all Customer-facing text.

#### Scenario: Language directive present for non-English session

- **WHEN** `Session.language` is `es`, `fr`, or `it`
- **THEN** the system prompt contains a directive such as "Respond in Spanish. All your messages to the customer must be in Spanish."

#### Scenario: No language directive for English session

- **WHEN** `Session.language` is `en`
- **THEN** the system prompt contains no explicit language directive (English is the default)

### Requirement: Internal field values SHALL remain in English

The Agent SHALL call `extract_field` with English enum values regardless of the session language. Field names, enum values, and the Issue Reference Number are never translated.

#### Scenario: extract_field called with English enum in Spanish session

- **WHEN** `Session.language` is `es`
- **AND** Claude infers the game system is D&D 5e
- **THEN** Claude calls `extract_field(field_name="game_system", field_value="D&D 5e")` — NOT a Spanish equivalent

### Requirement: Confirmation Step paraphrase SHALL be in the detected language

When all four Interview fields are collected and the Agent presents the Confirmation Step summary, the natural-language paraphrase SHALL be written in `Session.language`.

#### Scenario: Confirmation paraphrase in Spanish

- **WHEN** `Session.language` is `es` and all fields are collected
- **THEN** the Agent's confirmation paraphrase is in Spanish
- **AND** it does NOT contain the strings "Game System:", "Problem Category:", "Urgency Level:" in any language
