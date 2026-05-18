## ADDED Requirements

### Requirement: Global theme CSS variables
The application SHALL define a central `theme.css` file imported in `main.tsx` that exposes CSS custom properties for all visual tokens: background colours, text colours, accent colours, font families, border radii, and box shadow values. No component SHALL hardcode colour hex values or font-family strings — all must reference these variables.

#### Scenario: Theme variables present on :root
- **WHEN** the application renders in a browser
- **THEN** `--color-parchment`, `--color-stone`, `--color-ink`, `--color-gold`, `--font-heading`, and `--font-body` SHALL be resolvable CSS custom properties on the document root

### Requirement: Parchment background texture
The page background SHALL use a parchment-like warm cream/tan colour with a subtle repeating SVG texture overlay, conveying aged paper rather than a flat white screen.

#### Scenario: Background renders on page load
- **WHEN** the page loads
- **THEN** the document body background SHALL display a warm off-white to tan gradient or texture (no plain white)

### Requirement: Google Fonts loaded
The application SHALL load Cinzel (headings) and IM Fell English (body) from Google Fonts via a `<link>` in `index.html`, with system-serif fallbacks defined in `theme.css`.

#### Scenario: Fonts applied to headings
- **WHEN** the application renders
- **THEN** all `h1`–`h3` elements SHALL render in Cinzel or its fallback
- **THEN** all body/chat text elements SHALL render in IM Fell English or its fallback

#### Scenario: Font fallback on offline load
- **WHEN** Google Fonts is unavailable
- **THEN** headings SHALL fall back to a system serif font (e.g., Georgia)
- **THEN** body text SHALL fall back to a system serif font
