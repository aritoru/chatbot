
### Requirement: Agent SHALL infer game_system from conversational signal

The Agent SHALL determine the `game_system` field by inferring it from any signal in the Customer's messages — direct edition names, oblique references, era markers, or mechanical references unique to an edition. The Agent SHALL NOT present the enumerated list of game systems to the Customer during the collection phase.

#### Scenario: Direct edition name

- **WHEN** the Customer says "I'm running D&D 5e"
- **THEN** the Agent calls `extract_field` with `field_name="game_system"` and `field_value="D&D 5e"` without asking a clarifying question

#### Scenario: Oblique reference

- **WHEN** the Customer says "the newest version of D&D"
- **THEN** the Agent infers `D&D 5e` and calls `extract_field` with that value

#### Scenario: Mechanical reference unique to an edition

- **WHEN** the Customer mentions "THAC0" or "second edition mechanics"
- **THEN** the Agent infers `AD&D 2e` and calls `extract_field` with that value

#### Scenario: Unsupported game system

- **WHEN** the Customer says "I play Pathfinder 2e"
- **THEN** the Agent calls `extract_field` with `field_value="Other"` and continues the Interview

### Requirement: Agent SHALL infer urgency_level from conversational signal

The Agent SHALL determine the `urgency_level` field by inferring it from cues in the Customer's description of their problem — explicit urgency words, time pressure, blocking impact, or absence of pressure. The Agent SHALL NOT present the list `Low / Medium / High` to the Customer during the collection phase.

#### Scenario: Explicit time pressure

- **WHEN** the Customer says "my session is tonight and we're stuck"
- **THEN** the Agent infers `High` and calls `extract_field` with `field_name="urgency_level"` and `field_value="High"`

#### Scenario: Affective urgency cue

- **WHEN** the Customer says "this is really annoying me, I want it sorted soon"
- **THEN** the Agent infers `Medium` and calls `extract_field` with that value

#### Scenario: No urgency signal

- **WHEN** the Customer says "just curious about a rule, no rush"
- **THEN** the Agent infers `Low` and calls `extract_field` with that value

### Requirement: Agent SHALL ask an open follow-up question when inference is impossible

When the Customer has described their problem but the Agent has gathered no signal for a constrained field, the Agent SHALL ask one open follow-up question targeted at that field. The Agent SHALL NOT list enum values in the follow-up.

#### Scenario: Game system signal absent

- **WHEN** the Customer has described a rules issue without naming the edition
- **AND** the Agent has no edition signal to infer from
- **THEN** the Agent asks an open question such as "Which edition are you playing?" without listing the enum values

#### Scenario: Urgency signal absent

- **WHEN** the Customer has described their problem with no time or impact cue
- **AND** the Agent has no urgency signal to infer from
- **THEN** the Agent asks an open question such as "How time-sensitive is this for you?" without listing Low/Medium/High

### Requirement: Confirmation Step SHALL display the inferred normalized values

The Confirmation Step summary SHALL show the Customer the normalized enum value the Agent inferred for `game_system` and `urgency_level`, labeled clearly, so an inference error can be caught before the Intake is saved.

#### Scenario: Inferred values are confirmed

- **WHEN** all four fields are collected and the Agent presents the summary
- **THEN** the summary includes lines such as "Game System: D&D 5e" and "Urgency Level: High" using the exact enum values

#### Scenario: Customer corrects an inferred value

- **WHEN** the Customer rejects the summary saying "the urgency should be lower"
- **THEN** the Agent collects the new value through the same inference flow
- **AND** the Agent calls `extract_field` with the corrected value
- **AND** the Agent re-presents the updated summary without restarting the Interview

### Requirement: Intake schema SHALL remain unchanged

The persisted Intake JSON SHALL continue to store `game_system` and `urgency_level` as their `GameSystem` and `UrgencyLevel` enum values. This change SHALL NOT modify the Intake schema, the API response shape, or the on-disk format.

#### Scenario: Intake JSON shape

- **WHEN** an Intake is saved after a successful Confirmation Step
- **THEN** the JSON file contains `game_system` as one of the `GameSystem` enum string values
- **AND** the JSON file contains `urgency_level` as one of `Low`, `Medium`, or `High`
- **AND** no new fields are added to the Intake document
