## ADDED Requirements

### Requirement: Auto-narrate Agent messages
The chat interface SHALL automatically narrate each new Agent message using `window.speechSynthesis` as soon as the message is added to the message list, unless the customer has muted speech or the browser does not support the Web Speech API.

#### Scenario: Agent message spoken on arrival
- **WHEN** a new message with role `agent` is appended to the message list
- **THEN** the message text SHALL be enqueued as a `SpeechSynthesisUtterance` and spoken aloud
- **THEN** any previously queued utterance SHALL be cancelled before the new one is enqueued

#### Scenario: Muted — no speech on agent message
- **WHEN** the customer has activated the mute toggle
- **THEN** new Agent messages SHALL NOT trigger any speech

#### Scenario: Unsupported browser — no errors
- **WHEN** `window.speechSynthesis` is not present in the browser
- **THEN** no speech SHALL be attempted
- **THEN** no JavaScript error SHALL be thrown

### Requirement: Sage voice selection
The speech synthesis SHALL attempt to use a voice suitable for a sage/oracle character — preferring deep, authoritative English voices — and fall back to the browser default if no preferred voice is found.

#### Scenario: Preferred voice available
- **WHEN** `speechSynthesis.getVoices()` contains a voice whose name includes "Daniel", "George", "Arthur", or whose lang starts with "en-GB"
- **THEN** the first matching voice SHALL be used for all utterances

#### Scenario: No preferred voice available
- **WHEN** no preferred voice is found in the available voices list
- **THEN** the utterance SHALL use the browser default voice (no `voice` property set)

#### Scenario: Voices load asynchronously (Chrome)
- **WHEN** `getVoices()` returns an empty array on initial call
- **THEN** the component SHALL listen for the `voiceschanged` event and re-select the voice when voices become available

### Requirement: Speech rate and pitch
All utterances SHALL use a rate of 0.88 and a pitch of 0.9 to produce a slower, deeper delivery fitting the sage persona.

#### Scenario: Utterance properties set correctly
- **WHEN** a `SpeechSynthesisUtterance` is created for an Agent message
- **THEN** `utterance.rate` SHALL equal 0.88
- **THEN** `utterance.pitch` SHALL equal 0.9

### Requirement: Speech cancelled on session reset and unmount
Active and queued speech SHALL be cancelled when the customer resets to a new session or when the Chat component unmounts.

#### Scenario: Speech stops on new consultation
- **WHEN** the customer clicks "Begin a New Consultation"
- **THEN** `window.speechSynthesis.cancel()` SHALL be called before the session state is reset

#### Scenario: Speech stops on component unmount
- **WHEN** the Chat component unmounts
- **THEN** `window.speechSynthesis.cancel()` SHALL be called via the `useEffect` cleanup
