
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

### Requirement: Confirmation Step SHALL confirm the problem statement, not internal fields

The Confirmation Step SHALL present a single natural-language paraphrase of the Customer's problem and ask the Customer whether the paraphrase is correct and ready to be filed. The Confirmation Step SHALL NOT show the Customer any field label (`Game System`, `Problem Category`, `Urgency Level`), any normalized enum value as a labeled line, or a list of the internal fields collected. The paraphrase MAY echo the Customer's own description of their game system or urgency where that phrasing was supplied by the Customer, but MUST NOT name the internal field or its enum value.

#### Scenario: Problem statement is paraphrased without field labels

- **WHEN** all four fields are collected and the Agent presents the confirmation turn
- **THEN** the Agent's message paraphrases the Customer's problem in one or two natural sentences
- **AND** the message does NOT contain the strings "Game System:", "Problem Category:", or "Urgency Level:"
- **AND** the message does NOT list `Low`, `Medium`, `High` or any `GameSystem` enum value as a labeled line

#### Scenario: Customer confirms the paraphrase

- **WHEN** the Customer responds affirmatively (e.g., "yes that's right", "go ahead")
- **THEN** the Agent calls `confirm_intake`

#### Scenario: Customer corrects the paraphrase

- **WHEN** the Customer rejects the paraphrase saying something like "no, that's not quite it" or "the urgency is lower than that"
- **THEN** the Agent asks an open question about what was wrong with the problem statement
- **AND** the Agent re-infers any of the four fields whose value changes and fires `extract_field` for each one
- **AND** the Agent re-presents an updated paraphrase without restarting the Interview
- **AND** the Agent does NOT name the internal field that was corrected (e.g., does NOT say "I'll update the urgency level")

### Requirement: Agent SHALL NOT reveal internal field names to the Customer

At no point during the Interview, Confirmation Step, or post-submission turn SHALL the Agent name an internal field (`game_system`, `problem_category`, `problem_description`, `urgency_level`) or its label form (`Game System`, `Problem Category`, `Problem Description`, `Urgency Level`) to the Customer. The Agent SHALL also avoid presenting the enum values `Low` / `Medium` / `High` or any `GameSystem` enum string as a labeled line.

#### Scenario: Inference and collection are silent

- **WHEN** the Agent infers a value and calls `extract_field`
- **THEN** the Agent's next Customer-facing message does NOT announce what field was just stored

#### Scenario: Open follow-up does not name the field

- **WHEN** the Agent must ask an open follow-up because inference failed for `urgency_level`
- **THEN** the Agent asks a natural question like "How time-sensitive is this for you?"
- **AND** the Agent does NOT say "What urgency level should I record?" or anything that names the internal field

### Requirement: Post-submission UI SHALL show only the IRN and problem description

The Customer-facing post-submission panel SHALL display the Issue Reference Number and the problem description the Agent recorded. The panel SHALL NOT display the `game_system`, `problem_category`, or `urgency_level` field values to the Customer.

#### Scenario: Submission panel after successful confirmation

- **WHEN** the Customer confirms and the Intake is saved
- **THEN** the post-submission panel shows the IRN
- **AND** the panel shows the problem description text
- **AND** the panel does NOT show the strings "Game System:", "Category:", or "Urgency:" or their values

### Requirement: Intake schema SHALL remain unchanged

The persisted Intake JSON SHALL continue to store `game_system` and `urgency_level` as their `GameSystem` and `UrgencyLevel` enum values. This change SHALL NOT modify the Intake schema, the API response shape, or the on-disk format.

#### Scenario: Intake JSON shape

- **WHEN** an Intake is saved after a successful Confirmation Step
- **THEN** the JSON file contains `game_system` as one of the `GameSystem` enum string values
- **AND** the JSON file contains `urgency_level` as one of `Low`, `Medium`, or `High`
- **AND** no new fields are added to the Intake document
