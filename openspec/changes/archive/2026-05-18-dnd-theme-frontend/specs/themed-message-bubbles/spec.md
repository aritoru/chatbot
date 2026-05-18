## ADDED Requirements

### Requirement: Customer message bubble style
Customer messages SHALL be styled with a warm, slightly darker parchment background and right-aligned, suggesting the player speaking at the table.

#### Scenario: Customer bubble renders right-aligned
- **WHEN** a message with role `user` is rendered in the chat
- **THEN** the bubble SHALL be right-aligned within the message list
- **THEN** the bubble SHALL use `--color-parchment-dark` as its background
- **THEN** the bubble SHALL have a rounded-corner border styled with a thin gold-toned border

### Requirement: Agent message bubble style
Agent (sage/wizard NPC) messages SHALL be styled with a dark stone/slate background and light gold or cream text, left-aligned, giving the impression of ancient inscriptions or a wizard's pronouncement.

#### Scenario: Agent bubble renders left-aligned
- **WHEN** a message with role `assistant` is rendered in the chat
- **THEN** the bubble SHALL be left-aligned within the message list
- **THEN** the bubble SHALL use `--color-stone` as its background
- **THEN** text SHALL render in `--color-parchment` or `--color-gold`
- **THEN** an optional decorative glyph or icon (e.g., a d20 or scroll icon) SHALL prefix the bubble label "The Sage"

### Requirement: Thinking/loading indicator
While the agent is processing a response, a thematic loading indicator SHALL appear in place of a regular bubble.

#### Scenario: Loading state shown during API call
- **WHEN** the user has sent a message and the API response is pending
- **THEN** a pulsing or animated indicator SHALL appear styled as a glowing rune or crystal-ball orb
- **THEN** the indicator SHALL be left-aligned (agent side)
- **THEN** no partial or empty text bubble SHALL appear
