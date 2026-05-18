## 1. Fonts and Theme Foundation

- [x] 1.1 Add Google Fonts `<link>` for Cinzel and IM Fell English to `front/index.html`
- [x] 1.2 Create `front/src/theme.css` with `:root` CSS custom properties: `--color-parchment`, `--color-parchment-dark`, `--color-stone`, `--color-ink`, `--color-gold`, `--color-accent`, `--font-heading`, `--font-body`
- [x] 1.3 Add parchment SVG texture as a CSS `background-image` data URI on `body` in `theme.css`
- [x] 1.4 Import `theme.css` in `front/src/main.tsx` before `index.css`

## 2. Global Base Styles

- [x] 2.1 Update `front/src/index.css` to apply `--font-body` to `body` and `--font-heading` to `h1`–`h3`
- [x] 2.2 Set `body` background colour to `--color-parchment` with the texture overlay
- [x] 2.3 Set default text colour to `--color-ink`

## 3. Header Banner (`App.tsx`)

- [x] 3.1 Add a `<header>` element in `App.tsx` above the chat panel with title "AD&DHelp" and tagline "Consult the Sage — Your AD&D Oracle"
- [x] 3.2 Style the header title in Cinzel, ≥ 28 px, `--color-ink` or `--color-gold`
- [x] 3.3 Style the tagline in IM Fell English italic, smaller size
- [x] 3.4 Add a decorative `<hr>` divider styled with `--color-gold` between the header and the chat panel

## 4. Message Bubbles (`Chat.tsx` + `theme.css`)

- [x] 4.1 Add `.msg-customer` and `.msg-agent` CSS classes in `theme.css` with appropriate background colours, text colours, border radii, and borders per spec
- [x] 4.2 Update `Chat.tsx` message rendering to apply `.msg-customer` for `role === 'user'` and `.msg-agent` for `role === 'assistant'`
- [x] 4.3 Add an agent label "The Sage" (with optional glyph) to agent bubbles via a `<span>` in the bubble header
- [x] 4.4 Add `.msg-loading` CSS class in `theme.css` for the pulsing rune/crystal-ball loading indicator (CSS keyframe animation)
- [x] 4.5 Update `Chat.tsx` loading state to render a `.msg-loading` indicator instead of any empty bubble

## 5. Input Controls (`Chat.tsx` + `theme.css`)

- [x] 5.1 Add `.input-field` CSS class in `theme.css`: parchment background, ornamental border, `--font-body`, focus ring in `--color-gold`
- [x] 5.2 Apply `.input-field` class to the `<textarea>` or `<input>` in `Chat.tsx`
- [x] 5.3 Add `.btn-send` CSS class in `theme.css`: dark stone background, gold/cream text, hover glow via CSS `transition` and `filter: brightness()`
- [x] 5.4 Apply `.btn-send` class to the send button in `Chat.tsx`; update button label to a fantasy label (e.g., "Send ᛦ" or "Speak")
- [x] 5.5 Verify input and button are disabled and visually dimmed when `isLoading` is true (existing logic, confirm styling matches spec)

## 6. Intake Confirmation Panel (`Chat.tsx` + `theme.css`)

- [x] 6.1 Add `.confirmation-scroll` CSS class in `theme.css` styled as a parchment scroll with top/bottom decorative borders and warm background
- [x] 6.2 Apply `.confirmation-scroll` to the confirmation panel in `Chat.tsx` that renders on `status === 'completed'`
- [x] 6.3 Update the IRN display to use Cinzel font and label it "Your Reference Scroll:"
- [x] 6.4 Display the problem description below the IRN in IM Fell English italic
- [x] 6.5 Verify no internal field names (`game_system`, `urgency_level`, `problem_category`) appear in the confirmation panel DOM
- [x] 6.6 Add a "Begin a New Consultation" styled button/link below the confirmation panel that reloads or resets the session

## 7. Smoke Testing

- [x] 7.1 Start both backend (`uvicorn main:app --reload`) and frontend (`npm run dev`) servers
- [x] 7.2 Verify header banner, fonts, and background texture render correctly in browser
- [x] 7.3 Send a chat message and verify customer bubble (right, parchment) and agent bubble (left, stone) render correctly
- [x] 7.4 Verify loading indicator appears while agent is responding
- [x] 7.5 Complete a full interview and verify confirmation scroll displays IRN and description (no internal fields)
- [x] 7.6 Verify "Begin a New Consultation" button starts a fresh session
