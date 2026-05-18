## ADDED Requirements

### Requirement: Mute/unmute toggle button
The chat interface SHALL display a mute/unmute toggle button that allows the customer to suppress or restore Sage speech narration at any time during a session.

#### Scenario: Toggle starts unmuted
- **WHEN** the chat interface loads
- **THEN** the mute toggle SHALL be in the unmuted state by default (speech is active)

#### Scenario: Customer mutes speech
- **WHEN** the customer clicks the mute toggle while speech is active
- **THEN** the toggle SHALL switch to the muted state
- **THEN** any active or queued speech SHALL be cancelled immediately
- **THEN** subsequent Agent messages SHALL NOT be spoken

#### Scenario: Customer unmutes speech
- **WHEN** the customer clicks the mute toggle while speech is muted
- **THEN** the toggle SHALL switch to the unmuted state
- **THEN** the next incoming Agent message SHALL be spoken aloud

#### Scenario: Button hidden when Web Speech API is unsupported
- **WHEN** `window.speechSynthesis` is not present
- **THEN** the mute toggle button SHALL NOT be rendered in the DOM

### Requirement: Themed mute toggle styling
The mute toggle button SHALL be styled consistently with the AD&D fantasy theme defined in `theme.css`.

#### Scenario: Button uses theme variables
- **WHEN** the mute toggle is rendered
- **THEN** it SHALL use `--color-stone` background, `--color-gold` icon/text, and the `--font-heading` font family
- **THEN** in muted state, the button SHALL use a visually distinct style (e.g., reduced opacity or `--color-parchment-dark` background) to make the muted state obvious at a glance

### Requirement: Mute toggle placement
The mute toggle SHALL be positioned in the chat form bar, adjacent to the send button, so it is always visible without scrolling.

#### Scenario: Toggle visible in chat form
- **WHEN** the chat interface is rendered
- **THEN** the mute toggle SHALL appear in the `.chat-form` row alongside the input field and send button
