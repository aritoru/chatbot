## MODIFIED Requirements

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

## ADDED Requirements

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
