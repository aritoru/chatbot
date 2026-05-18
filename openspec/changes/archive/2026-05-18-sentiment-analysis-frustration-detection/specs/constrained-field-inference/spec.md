## MODIFIED Requirements

### Requirement: Agent SHALL infer urgency_level from conversational signal

The Agent SHALL determine the `urgency_level` field by inferring it from cues in the Customer's description of their problem — explicit urgency words, time pressure, blocking impact, or absence of pressure. The Agent SHALL NOT present the list `Low / Medium / High` to the Customer during the collection phase.

When `Session.frustration_signal` is `High`, the Agent SHALL bias toward inferring `High` urgency from any ambiguous cue, treating the Customer's frustration itself as implicit time pressure when no other urgency signal is present.

#### Scenario: Explicit time pressure

- **WHEN** the Customer says "my session is tonight and we're stuck"
- **THEN** the Agent infers `High` and calls `extract_field` with `field_name="urgency_level"` and `field_value="High"`

#### Scenario: Affective urgency cue

- **WHEN** the Customer says "this is really annoying me, I want it sorted soon"
- **THEN** the Agent infers `Medium` and calls `extract_field` with that value

#### Scenario: No urgency signal

- **WHEN** the Customer says "just curious about a rule, no rush"
- **THEN** the Agent infers `Low` and calls `extract_field` with that value

#### Scenario: Frustration-biased inference — ambiguous cue

- **WHEN** `Session.frustration_signal` is `High`
- **AND** the Customer's urgency signal is ambiguous (e.g., "I guess I need this soon")
- **THEN** the Agent infers `High` rather than `Medium` and calls `extract_field` accordingly

#### Scenario: Frustration-biased inference — no urgency signal

- **WHEN** `Session.frustration_signal` is `High`
- **AND** the Customer has provided no urgency signal at all
- **THEN** the Agent infers `High` based on the frustration level alone and calls `extract_field`
