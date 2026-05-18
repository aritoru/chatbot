## ADDED Requirements

### Requirement: System SHALL classify Frustration Signal after each Customer turn via `extract_field`

After each Customer message is received, Claude SHALL classify the Customer's current Frustration Signal as `None`, `Mild`, or `High` by calling `extract_field(field_name="frustration_signal", field_value=...)` within the normal tool loop. The result SHALL be stored in `Session.frustration_signal` before the Agent system prompt is rebuilt for subsequent loop iterations, so Claude sees the updated signal in the same turn's tool-result pass.

#### Scenario: Calm message — no frustration detected

- **WHEN** the Customer sends a normal, unhurried message with no frustration signals
- **THEN** Claude calls `extract_field(field_name="frustration_signal", field_value="None")`
- **AND** `Session.frustration_signal` is set to `None`

#### Scenario: Short curt reply after a clarifying question

- **WHEN** the Customer replies with a dismissive message (e.g., "just fix it" or "I already told you")
- **THEN** Claude calls `extract_field(field_name="frustration_signal", field_value="Mild")` or `"High"` depending on signal strength
- **AND** `Session.frustration_signal` is updated accordingly

#### Scenario: Explicit frustration expression

- **WHEN** the Customer uses words such as "frustrated", "annoyed", "wasting my time", "how many times", or types in ALL CAPS
- **THEN** Claude calls `extract_field(field_name="frustration_signal", field_value="High")`
- **AND** `Session.frustration_signal` is set to `High`

#### Scenario: Frustration de-escalation

- **WHEN** `Session.frustration_signal` was `Mild` or `High` and the next Customer turn is calm and cooperative
- **THEN** Claude calls `extract_field(field_name="frustration_signal", field_value="Mild")` or `"None"` as appropriate
- **AND** `Session.frustration_signal` is reduced accordingly

#### Scenario: Claude omits frustration_signal call

- **WHEN** Claude does not call `extract_field` with `field_name="frustration_signal"` on a given turn
- **THEN** `Session.frustration_signal` retains its previous value (graceful degradation — no forced reset)

### Requirement: Frustration Signal SHALL be recorded on the Intake

When an Intake is created at the Confirmation Step, the `frustration_signal` field SHALL be included in the Intake JSON written to disk, reflecting the final value of `Session.frustration_signal` at the time of confirmation.

#### Scenario: Intake created after frustrated session

- **WHEN** the Customer confirms their Intake and `Session.frustration_signal` is `High`
- **THEN** the Intake JSON contains `"frustration_signal": "High"`

#### Scenario: Intake created after calm session

- **WHEN** the Customer confirms their Intake and `Session.frustration_signal` is `None`
- **THEN** the Intake JSON contains `"frustration_signal": "None"`

### Requirement: Frustration Signal SHALL NOT be exposed in the HTTP message response

`Session.frustration_signal` SHALL NOT appear in any JSON response body returned by `POST /sessions` or `POST /sessions/{id}/messages`. It SHALL appear in `GET /intakes/{irn}` as part of the full Intake record.

#### Scenario: Message response does not include frustration_signal

- **WHEN** a Customer turn is processed and `Session.frustration_signal` is `High`
- **THEN** the JSON response from `POST /sessions/{id}/messages` does NOT contain the key `frustration_signal`
