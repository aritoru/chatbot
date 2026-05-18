## Context

The AD&DHelp frontend is currently a bare React/Vite chat UI with no visual identity. The backend, API, and domain model are stable and require no changes. The only affected surface is the React component tree and CSS layer in `front/`.

The project uses no CSS framework — styles are authored in plain CSS. `Chat.tsx` is the single component that handles all chat state; `App.tsx` renders the shell. There is no existing design system to extend; the theme can be introduced cleanly via CSS custom properties.

## Goals / Non-Goals

**Goals:**
- Establish a cohesive AD&D fantasy aesthetic across the entire chat UI
- Keep all changes confined to `front/` — zero backend or API impact
- Use CSS custom properties as the single source of truth for the colour/typography palette so future tweaks require one-file changes
- Prefer web fonts available on Google Fonts (no self-hosted assets required in MVP)
- Preserve all existing functional behaviour (session flow, message sending, intake confirmation panel)

**Non-Goals:**
- Mobile-first or responsive breakpoints (desktop only for MVP)
- Animations or particle effects beyond simple CSS transitions
- Dark/light mode toggle
- Accessibility audit (stretch goal for a later change)
- Backend or API changes of any kind

## Decisions

### D1 — CSS Custom Properties in a dedicated theme file

**Decision**: Introduce `front/src/theme.css` imported globally in `main.tsx`. All colours, font families, border radii, and shadow values are CSS variables (`--color-parchment`, `--font-heading`, etc.) defined on `:root`.

**Why**: Keeps the palette in one place; component files reference variables rather than raw hex values, so the theme can be swapped or tweaked without touching component files.

**Alternative considered**: Tailwind CSS with a custom config — rejected because it introduces a build-time dependency and requires rewriting all class names in existing components.

### D2 — Google Fonts for headings and body

**Decision**: Import two fonts via `index.html` `<link>`:
- **Cinzel** (headings, UI labels) — small-cap Roman letterforms with a medieval feel
- **IM Fell English** (chat body text) — a historical serif that reads like hand-typeset prose

**Why**: Both are free, load from a CDN with no self-hosting, and pair well for the AD&D register. No licensing concerns.

**Alternative considered**: MedievalSharp — rejected because it lacks italic weights needed for agent responses.

### D3 — Background texture via CSS `background-image` data URI

**Decision**: The page background uses a subtle parchment-like repeating pattern authored as an inline SVG data URI in `theme.css`, not an external image file.

**Why**: Keeps the project asset-free (no `/public/` images to manage) while still providing texture. The SVG can be tweaked inline.

**Alternative considered**: A `.jpg` parchment texture in `/public/` — rejected to avoid binary assets in the repo.

### D4 — Message bubble differentiation by sender class

**Decision**: Customer messages get a `.msg-customer` class; Agent messages get `.msg-agent`. Styles are defined in `theme.css` and applied conditionally in `Chat.tsx`.

**Why**: The existing `Chat.tsx` already conditionally applies alignment classes; extending to themed classes is a minimal diff.

### D5 — No new npm dependencies

**Decision**: The entire theme is implemented in CSS and existing React/TypeScript — zero new packages.

**Why**: Minimises supply-chain risk and keeps `npm install` fast.

## Risks / Trade-offs

- **Google Fonts availability** → Mitigation: Define system-serif fallbacks in every `font-family` stack so the UI degrades gracefully in offline environments.
- **SVG data URI parchment may look generic** → Mitigation: Keep the texture subtle; the colour palette and typography carry more atmospheric weight than the texture.
- **Cinzel at small sizes can be hard to read** → Mitigation: Use Cinzel only for headings and labels ≥ 14 px; body text uses IM Fell English which is legible at 15–16 px.
- **CSS custom property browser support** → Not a concern; all modern browsers support them and the app already targets modern Chrome/Firefox/Safari.
