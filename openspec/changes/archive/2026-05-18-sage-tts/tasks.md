## 1. Voice Selection Hook

- [x] 1.1 In `Chat.tsx`, add a `voiceRef = useRef<SpeechSynthesisVoice | null>(null)` to store the selected voice
- [x] 1.2 Add a `useEffect([], [])` that calls `pickVoice()` on mount and registers a `voiceschanged` listener to re-run `pickVoice()` if voices load asynchronously
- [x] 1.3 Implement `pickVoice()`: iterate `window.speechSynthesis.getVoices()`, prefer first voice matching "Daniel", "George", "Arthur", or lang starting with "en-GB"; store result in `voiceRef`; guard the whole function with `'speechSynthesis' in window`

## 2. Speech Synthesis Effect

- [x] 2.1 Add `const [muted, setMuted] = useState(false)` to `Chat.tsx`
- [x] 2.2 Add a `useEffect([messages])` that checks if the last message has `role === 'agent'` and `!muted` and `'speechSynthesis' in window`
- [x] 2.3 Inside the effect: call `window.speechSynthesis.cancel()`, create a `SpeechSynthesisUtterance` with the message text, set `rate = 0.88`, `pitch = 0.9`, assign `voiceRef.current` if set, then call `window.speechSynthesis.speak(utterance)`
- [x] 2.4 Add a cleanup function to the effect that calls `window.speechSynthesis.cancel()`

## 3. Session Reset Cancellation

- [x] 3.1 In `handleRestart()`, call `window.speechSynthesis.cancel()` before `setIntake(null)` (guard with `'speechSynthesis' in window`)

## 4. Mute Toggle UI

- [x] 4.1 Add `.btn-mute` and `.btn-mute.muted` CSS classes to `theme.css`: same stone/gold base as `.btn-send`; muted state uses `--color-parchment-dark` background with reduced opacity text
- [x] 4.2 Add the mute toggle button to the `.chat-form` in `Chat.tsx`, after the send button: `<button className={`btn-mute${muted ? ' muted' : ''}`} type="button" onClick={handleMuteToggle} title={muted ? 'Unmute Sage' : 'Mute Sage'}>🔇</button>` (or text label)
- [x] 4.3 Implement `handleMuteToggle()`: toggle `muted` state; if becoming muted call `window.speechSynthesis.cancel()`
- [x] 4.4 Conditionally render the mute button only when `'speechSynthesis' in window`

## 5. Smoke Testing

- [x] 5.1 Load the app, wait for the opening Sage greeting, and verify it is spoken aloud
- [x] 5.2 Send a message and verify the Sage's reply is spoken (previous speech is cut off before the new one starts)
- [x] 5.3 Click the mute toggle and verify speech stops and subsequent messages are silent
- [x] 5.4 Click unmute and verify the next Sage message is spoken again
- [x] 5.5 Click "Begin a New Consultation" mid-speech and verify audio stops before the new session greeting starts
