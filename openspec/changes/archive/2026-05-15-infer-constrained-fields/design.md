## Context

The Agent today (in `back/services/agent.py`) is driven by a system prompt that hard-codes the `GameSystem` and `UrgencyLevel` enums and instructs Claude to "present the list and re-ask" when the Customer's response is ambiguous. The prompt also says to map close phrasings (e.g., "second edition" → `AD&D 2e`) — so partial inference already exists, but the menu-fallback is reached too eagerly and the menu wording leaks into the conversation.

The Intake JSON contract is consumed downstream (analytics, future routing) and depends on normalized enum values. That contract must not change.

The interview state machine, tool loop, and storage are already in place and working. This change is isolated to the **system prompt** and the wording of the **confirmation summary**.

## Goals / Non-Goals

**Goals:**
- Eliminate menu presentation for `game_system` and `urgency_level` during the collection phase.
- Have the Agent infer enum values from any conversational signal — direct ("D&D 5e"), oblique ("the newest version"), thematic ("THAC0"), or affective ("urgent", "blocking my game").
- Keep the Intake JSON shape exactly as it is.
- Surface every inferred value at the Confirmation Step so the Customer can correct misreads.
- Preserve the existing field-correction flow on rejection (already implemented for any field).

**Non-Goals:**
- Changing the four collected fields, their order, or the Intake schema.
- Changing the `extract_field` / `confirm_intake` tool interface.
- Adding new tools (e.g., a separate `infer_field`).
- Inference for `problem_category` or `problem_description` (those are already free-text).
- Frontend changes.

## Decisions

### Decision 1: Keep `extract_field` as the sole write path

The existing tool already accepts a `field_name` + `field_value` where `field_value` must be a valid enum string. We reuse it as-is: inference happens **inside Claude**, and the tool call is fired only when Claude has settled on a normalized value. The Python `_apply_field` function silently drops invalid enum values today (a `try/except ValueError: pass`) — this stays as a defensive backstop, since Claude is the one choosing values.

**Alternative considered**: Adding a `confidence` field to `extract_field` and short-circuiting low-confidence calls. Rejected — confidence prompts model self-reporting which is notoriously unreliable, and the Confirmation Step already serves as the verification gate.

**Alternative considered**: A two-tool design (`infer_field` for low-signal cases, `extract_field` for direct statements). Rejected — adds prompt complexity for no behavior gain; the model can decide internally when it has enough signal to call the existing tool.

### Decision 2: Rewrite the prompt's rules section, not the tool description

The current prompt has explicit per-field rules ("if the customer says something close, map it") that already license inference but also reference the menu as a fallback. We rewrite the rules to:

- Drop every mention of "present the list."
- Replace "Game System: ..." and "Urgency Level: ..." rules with explicit inference guidance and example mappings.
- Add a "do not ask the Customer to pick from a menu" prohibition.
- Add an "ask an open follow-up question" instruction for the fallback case ("which edition are you running?" not "is it 1e, 2e, 3/3.5, 4e, 5e, or Other?").

Tool description is left untouched — the schema is unchanged.

### Decision 3: Show normalized values at confirmation, accept correction in any phrasing

The summary already lists collected fields. We change the wording from a flat list to a labeled list of normalized values ("Game System: D&D 5e"). On rejection, the existing field-by-field correction flow handles the new value — and that new value goes through the same inference path. No new code is needed for correction.

### Decision 4: Inference happens at the model layer, not in Python

We do **not** add Python-side normalization (e.g., a fuzzy mapper from "third edition" → `D&D 3/3.5`). All mapping lives in Claude's response to the prompt. This keeps the Python code as a thin state machine and avoids two parallel sources of truth for what counts as "close enough."

## Risks / Trade-offs

- **[Inference is wrong silently]** → Confirmation Step is mandatory. Every Intake passes through `confirm_intake`, so an inference error must survive the Customer reviewing a labeled summary that includes the normalized value.
- **[Customer references an unsupported system, e.g., Pathfinder]** → Prompt explicitly maps "anything not in the AD&D/D&D family" to `Other`. The customer sees `Other` in the confirmation summary and can clarify in `problem_description`.
- **[Prompt regression — Claude reverts to menu behavior]** → Tasks include a manual smoke test for the three trickiest inputs: oblique edition ("the one with THAC0"), affective urgency ("my session is tonight"), and unsupported system ("Pathfinder 2e").
- **[Token cost slightly higher per turn]** → Inference rules add ~50 tokens to the system prompt. Negligible.

## Migration Plan

No data migration. The change is a prompt rewrite plus a confirmation-summary wording tweak — both purely runtime. Existing in-flight Sessions in memory continue with the old prompt until the process restarts; the next session uses the new prompt. Old Intake JSON files are byte-for-byte compatible with new ones.

Rollback: revert the commit. No schema, storage, or API state to undo.

## Open Questions

- None.
