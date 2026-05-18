## Context

The AD&D Help Agent runs a short interview to collect four fields before filing an Intake. Currently the Agent treats all sessions identically regardless of how the Customer is communicating. Some Customers are time-pressured, repeating themselves, or expressing impatience — signals that predict session abandonment if the Agent continues asking clarifying questions at normal pace.

The backend uses a tool-loop pattern in `agent.py`: build system prompt → send to Claude → handle tool calls → repeat until `end_turn`. The system prompt is **regenerated on every request** from the current `Session` state, making it cheap to inject new signals without changing the API surface.

## Goals / Non-Goals

**Goals:**
- Detect Frustration Signal (`None`, `Mild`, `High`) from Customer message content on every turn.
- Expose Frustration Signal to the Agent via the system prompt so Claude can modulate tone and question density.
- Record Frustration Signal on the Intake for support staff visibility.
- When Frustration Signal is `High`, skip optional clarifying questions and bias `urgency_level` inference toward `High`.

**Non-Goals:**
- Customer-facing display of Frustration Signal — this is invisible in conversation.
- Retrospective analysis of historical sessions.
- Replacing the existing field-inference approach; this is additive.

## Decisions

### Decision 1: Claude infers Frustration Signal via the existing `extract_field` tool

**Chosen**: Add `frustration_signal` as a valid `field_name` value in the `extract_field` tool enum. Claude calls `extract_field(field_name="frustration_signal", field_value="None"|"Mild"|"High")` on each turn after assessing the Customer's message. No separate heuristic service or additional API call is required.

**Alternatives considered**:
- *Dedicated `update_frustration_signal(level)` tool*: cleaner semantic separation between customer-provided fields and Agent observations, but adds surface area for no functional gain since the tool loop handles both identically.
- *Heuristic classifier in `frustration.py` + Claude-assisted fallback*: zero-cost fast path for obvious cases, but adds a new service file and a parsing step for Claude's response token. The two-phase design is harder to test and maintain.

**Rationale**: The existing tool loop already handles `extract_field` calls on every turn. Extending its enum costs one line and keeps the detection entirely within Claude's inference — consistent with how `urgency_level` and `game_system` are already inferred from conversational signals.

### Decision 2: `FrustrationSignal` enum on `Session` and `Intake`

**Chosen**: Add `FrustrationSignal` enum (`None`, `Mild`, `High`) to `back/models/interview.py`. Add `frustration_signal: FrustrationSignal = FrustrationSignal.NONE` to `Session`. Include `frustration_signal` in the `Intake` JSON written to disk so support staff can see the Customer's emotional state when reviewing filed Intakes.

**Alternatives considered**:
- *Float score (0.0–1.0)*: more granular but harder to reason about in the system prompt and in tests.
- *Boolean flag*: too coarse — `Mild` allows a softer tone shift before drastic shortcutting.
- *Session-only, not in Intake*: simpler, but loses useful context for support staff triaging the Intake.

**Rationale**: Three levels map cleanly to three Agent behaviors (normal / softer tone / fast-track). Mirroring `UrgencyLevel`'s capitalization pattern keeps the model layer consistent. Recording on the Intake costs nothing and provides durable signal for triage.

### Decision 3: Frustration Signal is updated after each Customer turn within the tool loop

**Chosen**: Claude calls `extract_field(field_name="frustration_signal", ...)` as part of the normal tool loop on each Customer turn. `_apply_field` writes the result to `session.frustration_signal`. Because the system prompt is regenerated at the top of each loop iteration, the updated signal is visible to Claude in the same turn's tool-result pass.

**Rationale**: No change to the loop structure is required — the existing `_apply_field` dispatch handles the new field name.

### Decision 4: Frustration Signal is NOT exposed in the HTTP message response

**Chosen**: `frustration_signal` does NOT appear in `POST /sessions/{id}/messages` responses. It IS included in `GET /intakes/{irn}` (the full Intake record), which is accessible to internal callers only.

**Rationale**: The Customer-facing API surface stays unchanged. Support staff can retrieve the signal via the existing Intake endpoint.

## Risks / Trade-offs

- **False positives (High frustration mis-classified)** → Agent may truncate the interview prematurely, producing a lower-quality Intake. Mitigation: tune the system prompt instruction conservatively; require clear multi-signal evidence before Claude escalates to `High`.
- **Claude omits the frustration_signal call** → If Claude doesn't call `extract_field` for frustration on a given turn, `session.frustration_signal` retains its previous value. This is acceptable — the signal degrades gracefully to the last known state.

## Open Questions

- Should `frustration_signal` appear in `GET /intakes` (the summary list), or only in `GET /intakes/{irn}` (the full record)? (Currently: full record only — revisit if dashboard tooling requests it.)
- De-escalation: **resolved** — signal only changes when Claude explicitly calls `extract_field` with the new level. No automatic de-escalation logic in `_apply_field`. The system prompt strongly instructs Claude to re-assess and call `extract_field(frustration_signal, ...)` on every Customer turn.
