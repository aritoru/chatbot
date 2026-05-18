## ADDED Requirements

### Requirement: Scroll/parchment confirmation panel
After the intake is confirmed, the post-confirmation panel SHALL be styled as an unrolled parchment scroll displaying the IRN and the problem description.

#### Scenario: Confirmation panel displays as scroll
- **WHEN** the intake status is `completed` and an IRN is present
- **THEN** the confirmation panel SHALL render with a parchment background, scroll-like top and bottom decorative edges, and a warm border
- **THEN** the panel SHALL display the IRN in bold Cinzel font prefixed with a label such as "Your Reference Scroll:"
- **THEN** the panel SHALL display the problem description in IM Fell English italic below the IRN

### Requirement: Confirmation panel excludes internal fields
The confirmation panel SHALL display only the IRN and problem description — it SHALL NOT display `game_system`, `urgency_level`, or `problem_category` enum values or field names.

#### Scenario: Internal fields absent from confirmation panel
- **WHEN** the confirmation panel is rendered after intake completion
- **THEN** the words "game_system", "urgency_level", "problem_category", "GameSystem", "UrgencyLevel" SHALL NOT appear anywhere in the rendered DOM of the panel
- **THEN** the IRN (formatted as `IRN-XXXXXXXX`) SHALL be visible and selectable by the user

### Requirement: New interview prompt after confirmation
Below the confirmation panel, a prompt SHALL appear inviting the customer to start a new session.

#### Scenario: New interview prompt visible
- **WHEN** the confirmation panel is rendered
- **THEN** a styled button or link SHALL appear with text such as "Begin a New Consultation"
- **THEN** clicking it SHALL reload or reset the chat to a fresh session
