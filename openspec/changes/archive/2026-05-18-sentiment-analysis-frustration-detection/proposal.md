## Why

Customers who are frustrated during an AD&D Help interview may disengage or abandon the session before the Intake is captured. Detecting frustration signals early allows the Agent to adapt its tone, pace fewer questions, and offer a faster resolution path — improving Intake completion rates and Customer satisfaction.

## What Changes

- Claude classifies the Customer's Frustration Signal (`None`, `Mild`, `High`) on every turn by calling `extract_field` with `field_name="frustration_signal"` — no separate service or heuristic pass.
- A `frustration_signal` property will be added to the `Session` model and stored in the Intake JSON for support staff visibility.
- The Agent system prompt will be augmented with the current `frustration_signal` so Claude can modulate its conversational style accordingly.
- When `frustration_signal` reaches `High`, the Agent will skip optional clarifying questions and move directly toward Intake confirmation.
- The Frustration Signal is invisible to the Customer in conversation; it appears only in the Intake record accessible to support staff.

## Capabilities

### New Capabilities

- `frustration-detection`: Claude infers the Customer's Frustration Signal (`None`/`Mild`/`High`) from each turn and records it via `extract_field(field_name="frustration_signal", ...)`. Updates `Session.frustration_signal` on every turn.
- `adaptive-agent-tone`: Adjusts the Agent's conversational style and question density based on the current `frustration_signal` injected into the system prompt.

### Modified Capabilities

- `constrained-field-inference`: When `frustration_signal` is `High`, the inference step must accept weaker evidence for `urgency_level` (bias toward `High`) to reduce the number of follow-up questions needed.

## Impact

- **`back/models/interview.py`** — add `FrustrationSignal` enum (`None`, `Mild`, `High`) and `frustration_signal` field to `Session` and `Intake`.
- **`back/services/agent.py`** — add `frustration_signal` to the `extract_field` tool enum; inject `frustration_signal` into the system prompt; short-circuit clarifying questions when signal is `High`.
- No new service file required — detection is handled by Claude via the existing tool loop.
- No frontend changes required.
