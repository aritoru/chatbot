## Context

The chat frontend (`Chat.tsx`) currently renders Agent messages as text only. The browser's `window.speechSynthesis` API is available in all modern browsers at no cost and requires no additional dependencies. The goal is to narrate each new Agent message as it arrives and give the customer a mute toggle.

The existing theme uses CSS custom properties and class-based styling; any new UI element must follow the same pattern.

## Goals / Non-Goals

**Goals:**
- Narrate every incoming Agent message automatically using `window.speechSynthesis`
- Provide a themed mute/unmute toggle that persists for the session lifetime
- Cancel all queued or active speech on session reset and component unmount
- Zero new npm dependencies; zero backend changes

**Non-Goals:**
- Voice selection UI exposed to the customer (voice is chosen programmatically)
- Persistence of mute preference across sessions (localStorage)
- Support for browsers that don't implement Web Speech API (graceful degradation: button hidden, no errors thrown)
- Subtitles/captions beyond what the text bubbles already show

## Decisions

### D1 — Trigger speech in a `useEffect` watching the `messages` array

**Decision**: A `useEffect([messages])` compares the last message's role; if it is `'agent'` and the component is not muted, it enqueues a new `SpeechSynthesisUtterance`.

**Why**: React state is the single source of truth for messages. Triggering from the effect that fires after the state update guarantees the utterance text matches what is rendered. Triggering inside `handleSubmit` would require passing the response text through an extra channel.

**Alternative considered**: Triggering inside the `sendMessage` try block after the response arrives — rejected because it couples the speech side-effect to the API call handler rather than to the rendered state.

### D2 — Voice selection: prefer a deep/male voice by name matching, fall back to default

**Decision**: On first render, iterate `window.speechSynthesis.getVoices()` and pick the first voice whose name contains "Daniel", "George", "Arthur", or "en-GB" (voices that tend to sound authoritative and suit a sage character). Fall back to the browser default if none match.

**Why**: The Web Speech API does not have a stable cross-platform voice identifier. Name-matching against known good voices gives a reasonable result on Chrome/macOS/Windows without crashing on other platforms.

**Alternative considered**: Always using the default voice — acceptable fallback but misses the atmospheric opportunity on platforms where better voices are available.

### D3 — Rate 0.88, pitch 0.9 for the utterance

**Decision**: Slightly slower rate and slightly lower pitch than the browser default (1.0 / 1.0).

**Why**: Slower, deeper speech fits the sage/oracle persona. Values outside 0.7–1.1 range tend to sound robotic or comical.

### D4 — Mute state lives in React component state, not a ref

**Decision**: `const [muted, setMuted] = useState(false)` in `Chat.tsx`.

**Why**: The mute toggle button needs to re-render (icon change) when state flips, so it must be state not a ref. The `useEffect` speech trigger reads `muted` from the closure, which is fine since the effect re-runs on every `messages` change where muted would also be current.

### D5 — Cancel speech on unmount and on session reset

**Decision**: The `useEffect` cleanup function calls `window.speechSynthesis.cancel()`. The `handleRestart` function also calls it explicitly before resetting state.

**Why**: Without cancellation, an utterance queued for the previous session would continue playing after the confirmation scroll or a new session starts.

## Risks / Trade-offs

- **`getVoices()` returns empty array on first call in Chrome** → Mitigation: listen to the `voiceschanged` event and store the selected voice in a ref; re-select on the event.
- **Long Agent messages cause a slow narration that outlasts the customer's patience** → Mitigation: `cancel()` is called on the next incoming message before enqueueing the new one, so messages never pile up.
- **Firefox on some Linux distros has no TTS voices installed** → Mitigation: wrap all `speechSynthesis` calls in a `'speechSynthesis' in window` guard; hide the mute button if unsupported.
- **iOS Safari requires a user gesture before any audio** → Accepted limitation; the mute button itself counts as a gesture, so customers who click it once unlock audio. Mute toggle defaults to muted on iOS as a workaround is out of scope.
