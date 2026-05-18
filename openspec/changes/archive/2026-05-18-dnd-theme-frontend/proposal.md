## Why

The current chat UI is a generic, unstyled interface that gives no sense of the AD&D world. Customers engaging with an AD&D help agent expect atmosphere — the look and feel should reinforce that they are in a fantasy realm, not a support ticket system.

## What Changes

- Replace the plain white/grey chat UI with a parchment-and-dark-stone D&D aesthetic (fonts, colours, textures, iconography)
- Restyle the chat bubble layout to feel like a tavern conversation between a player and a sage/wizard NPC
- Replace generic button and input styles with fantasy-styled equivalents (scroll-like input, wax-seal send button, runic decorations)
- Add a thematic page header/banner (title, tagline, atmospheric illustration or icon)
- Introduce a loading/thinking indicator themed as a crystal ball or glowing rune
- Adjust the post-confirmation panel to display the IRN and problem summary in a scroll/parchment style

## Capabilities

### New Capabilities

- `dnd-chat-theme`: Visual theme layer applied to the entire chat interface — colours, typography, background textures, and decorative elements that establish the AD&D atmosphere
- `themed-message-bubbles`: Restyled message bubbles differentiating Customer messages from Agent (sage/wizard NPC) messages with distinct visual treatment
- `themed-header-banner`: Page-level header with game title, tagline, and atmospheric branding
- `themed-input-controls`: Fantasy-styled text input and send button replacing the generic form controls
- `themed-intake-confirmation`: Scroll/parchment display for the post-confirmation IRN and problem summary panel

### Modified Capabilities

## Impact

- `front/src/components/Chat.tsx` — primary restyling target
- `front/src/App.tsx` — header/banner addition
- `front/index.html` — Google Fonts import (e.g., MedievalSharp or Cinzel for headings, IM Fell English for body)
- `front/src/index.css` or new `front/src/theme.css` — CSS custom properties, background textures, global resets
- No backend changes; no API changes; no domain-model changes
