## Why

The current Confirmation Step shows the Customer a labeled breakdown of every internal field the Agent has inferred — `Game System: D&D 5e`, `Problem Category: rules clarification`, `Urgency Level: High`. This leaks the shape of our internal data model into the conversation, makes the Agent feel like a form rather than a support contact, and forces the Customer to validate enum labels they never asked to see. We want the Agent to focus on solving the problem and confirm only the *problem statement* with the Customer — keeping `game_system`, `problem_category`, and `urgency_level` entirely internal.

## What Changes

- Agent stops surfacing the labels `Game System`, `Problem Category`, and `Urgency Level` (and their normalized values) to the Customer at any point in the conversation.
- Confirmation Step is reworded to confirm only the **problem statement** in natural language — e.g., "So you're trying to figure out how grappling a giant works in your campaign — let me get this filed." No field-name list.
- Agent still collects all four fields internally via `extract_field`, still infers `game_system` / `urgency_level` from conversational signal, and still calls `confirm_intake` when the Customer signals the problem statement is accurate.
- IRN is still shown at the end. The post-submission UI panel (`Chat.tsx` intake summary block) is updated to **stop displaying** `Game System`, `Category`, `Urgency` rows to the Customer — only the IRN and problem description remain visible.
- Correction flow shifts from "which field do you want to change" to natural problem-statement correction — "tell me what I got wrong about your problem" — and the Agent silently re-infers the constrained fields from the corrected wording.
- Intake JSON schema and on-disk format remain **unchanged** — all four fields persist exactly as before, only the Customer-facing surface changes.
- **BREAKING** for the spec: `constrained-field-inference`'s "Confirmation Step SHALL display the inferred normalized values" requirement is reversed.

## Capabilities

### New Capabilities
<!-- None — this is a UX/behavioral change to an existing capability. -->

### Modified Capabilities
- `constrained-field-inference`: Confirmation Step requirement is rewritten to confirm the problem statement only, never the labeled normalized values. New requirement added forbidding the Agent from naming any internal field to the Customer.

## Impact

- **Code**: `back/services/agent.py` system prompt rewritten — Confirmation Step + correction-flow rules. `front/src/components/Chat.tsx` intake-success panel trimmed to IRN + problem description only.
- **API**: No HTTP contract changes. `GET /intakes/{irn}` still returns all four fields (internal/admin use).
- **Backend storage**: No change. JSON files store the same shape.
- **Frontend**: Post-submission UI loses three rows but stays the same component.
- **Risk**: Customer can no longer catch an inference error on `game_system` / `urgency_level` directly. Mitigated by: (1) the Agent re-inferring from corrected problem statements; (2) internal-only fields tolerate occasional misreads since the Customer's primary need is the answer, not perfect taxonomy.
- **Docs**: `CLAUDE.md` Agent Architecture note updated to reflect the new confirmation surface.
