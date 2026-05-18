## ADDED Requirements

### Requirement: Fantasy-styled text input
The message input field SHALL be styled to resemble a parchment scroll or stone tablet entry — warm background, serif font, ornamental border — rather than a plain `<input>`.

#### Scenario: Input field has theme styling
- **WHEN** the user focuses the message input
- **THEN** the input SHALL display with a parchment-toned background (`--color-parchment`)
- **THEN** the input border SHALL use a gold or dark-brown ornamental style on focus
- **THEN** text typed in the input SHALL render in `--font-body` (IM Fell English or fallback)

### Requirement: Fantasy-styled send button
The send button SHALL be styled as a fantasy action element — a wax-seal, arcane sigil, or sword icon — rather than a plain text "Send" button.

#### Scenario: Send button has theme styling
- **WHEN** the send button is rendered
- **THEN** it SHALL display with a dark stone or deep red background (`--color-stone` or `--color-accent`)
- **THEN** the button label or icon SHALL use gold or cream text
- **THEN** on hover the button SHALL lighten or glow slightly via a CSS transition

### Requirement: Disabled state during loading
Both the input and send button SHALL be visually disabled while the agent is processing a response.

#### Scenario: Controls disabled during loading
- **WHEN** the agent response is pending
- **THEN** the send button SHALL be `disabled` and visually dimmed
- **THEN** the text input SHALL be `disabled` and visually dimmed
- **THEN** no new message can be submitted until the response arrives
