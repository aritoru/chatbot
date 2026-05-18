## ADDED Requirements

### Requirement: Branded page header
The page SHALL display a header banner at the top containing the application title "AD&DHelp" (or a stylised variant), a short tagline (e.g., "Consult the Sage — Your AD&D Oracle"), and a decorative divider.

#### Scenario: Header visible on load
- **WHEN** the application renders
- **THEN** a header element SHALL be visible above the chat panel
- **THEN** the title SHALL render in Cinzel font at a large size (≥ 28 px)
- **THEN** a tagline SHALL render below the title in a smaller, italic IM Fell English style

### Requirement: Decorative divider between header and chat
A horizontal decorative rule (styled as a runic or ornamental divider) SHALL separate the header banner from the chat panel.

#### Scenario: Divider renders between header and chat
- **WHEN** the application renders
- **THEN** a decorative `<hr>` or styled `<div>` SHALL appear between the header and the chat container
- **THEN** the divider SHALL use gold or amber tones consistent with `--color-gold`
