## Why

The Sage is a fantasy oracle character but speaks only in silent text — adding voice narration via the browser's built-in Web Speech API would deepen immersion without any backend changes, API keys, or cost.

## What Changes

- Each Agent message is read aloud automatically as it arrives, using the browser `SpeechSynthesis` API with a voice and rate tuned for a sage/oracle character
- A mute/unmute toggle button is added to the chat UI so customers can silence speech without refreshing
- Speech is cancelled when the customer starts a new session or closes the tab
- No backend changes; no new npm dependencies

## Capabilities

### New Capabilities

- `sage-speech-synthesis`: Automatic narration of Agent messages using `window.speechSynthesis`, with voice selection, rate/pitch tuning, and queue management
- `tts-mute-toggle`: A persistent mute/unmute control in the chat UI that suppresses or restores speech narration without disrupting the session

### Modified Capabilities

## Impact

- `front/src/components/Chat.tsx` — trigger speech on new agent messages; wire up mute toggle state
- `front/src/theme.css` — style the mute toggle button to match the AD&D theme
- No backend, API, or domain model changes
- No new npm packages — Web Speech API is a browser standard (Chrome, Edge, Safari, Firefox all support it)
