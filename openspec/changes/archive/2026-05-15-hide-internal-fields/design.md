## Context

The interview flow is now driven by an inference-first prompt (shipped in `infer-constrained-fields`). Constrained fields are mapped silently from conversational cues, but the Confirmation Step still surfaces a labeled summary of all four collected values to the Customer — including the internal field names (`Game System`, `Problem Category`, `Urgency Level`) and their normalized enum strings.

That summary serves two purposes today:
1. **Verification gate** — the Customer must explicitly confirm before `confirm_intake` fires.
2. **Inference safety net** — a misread on `game_system` or `urgency_level` is catchable before it gets saved.

The Customer-facing intake panel after submission (`Chat.tsx`) shows the same four field labels.

The Customer never asked for taxonomy. The goal of the conversation, from their perspective, is to get help with a rule — not to label themselves. We want to keep the verification gate but redesign it around the *problem*, not the *data model*. The intake JSON shape must not change because internal consumers (analytics, future routing) depend on it.

## Goals / Non-Goals

**Goals:**
- Eliminate every Customer-facing reference to `Game System`, `Problem Category`, and `Urgency Level` as labels or values during the Interview *and* on the post-submission panel.
- Keep the explicit confirmation turn — the Agent still must hear a "yes" before `confirm_intake` fires.
- Restate the *problem* in natural language at the Confirmation Step so the Customer has something concrete to validate.
- Preserve all four fields in the saved JSON and the `extract_field` / `confirm_intake` tool contract.
- Preserve inference behavior for `game_system` and `urgency_level` (already shipped).

**Non-Goals:**
- Removing or renaming any of the four collected fields.
- Changing the Intake JSON schema or the API response shape.
- Removing the IRN from the Customer-facing thank-you screen.
- Adding a separate "review your data" admin view (out of scope; `GET /intakes/{irn}` already exposes everything for internal use).

## Decisions

### Decision 1: Confirmation Step becomes a single natural-language sentence

The Agent's confirmation turn will be a one-sentence paraphrase of the problem in the Customer's own framing, e.g., "So you're trying to figure out how grappling a giant works in your 5e game — does that sound right, and are you good to file this?". The sentence **MAY** echo the game system in the Customer's own phrasing (the customer said it themselves so it's not leaking schema) but **MUST NOT** name the urgency level, the problem category, or any field-label prefix.

**Alternative considered**: Two-step confirmation (paraphrase the problem, then quietly call `confirm_intake` on any positive reply). Rejected — the Agent already runs a tool loop on every turn; a single confirmation turn is simpler and matches the existing state machine.

**Alternative considered**: Auto-save on natural conversation close. Rejected up front in the brainstorm — losing the explicit gate makes the save invisible, which feels worse than the form-y status quo.

### Decision 2: Correction flow shifts from per-field to problem-paraphrase

Today, when a Customer rejects the summary, the Agent asks "which field do you want to correct?". Going forward, the Agent will ask "what did I get wrong about your problem?" — and re-infer all four fields from the corrected wording. The `extract_field` tool stays the same; the Agent simply re-fires it for any field whose value changes.

**Why**: The Customer doesn't have a mental model of four fields, so asking them to pick one breaks immersion. They have a *problem statement* and they can say what's wrong with the Agent's paraphrase of it.

### Decision 3: Prompt rewrite, no Python changes

Everything visible to the Customer comes from the system prompt and the post-submission React component. The state machine (`process_message`, `_apply_field`, `save_intake`) does not need to change. We rewrite the "Confirmation Step" rules and the correction-flow rule in `_build_system_prompt`, and trim three rows from the intake-success panel in `Chat.tsx`.

### Decision 4: Frontend intake panel shows only IRN + problem description

The existing panel (`Chat.tsx`) renders `Game System`, `Category`, `Urgency`, `Description` rows after submission. We remove the first three; keep `Reference number: IRN-...` and the problem description. The component still receives the full `intake` object from the API — we just don't render the three internal rows.

**Alternative considered**: Hide the entire post-submission summary, show only the IRN. Rejected — the Customer expects a recap of *what they reported*, just not in field-form. Keeping the problem description preserves that.

### Decision 5: Spec is a MODIFIED delta to `constrained-field-inference`

The existing `Requirement: Confirmation Step SHALL display the inferred normalized values` is being reversed. Per the OpenSpec workflow, MODIFIED requirements must include the full updated content; we rewrite that requirement in full and add one new requirement covering the customer-facing surface ban.

## Risks / Trade-offs

- **[Inference error survives unnoticed]** → Customer can no longer catch a wrong `game_system` directly. Mitigation: the paraphrase sentence may include the system in the Customer's own words if it was named explicitly; misreads on truly oblique signals are accepted as a fair UX trade. The Customer's primary need is the answer, not the taxonomy, and inference is already governed by the Confirmation gate on the problem statement (a wrong field strongly correlates with a wrong problem paraphrase).
- **[Customer says "no" without specifying what's wrong]** → The Agent re-asks for the corrected problem statement; the existing tool loop handles this naturally.
- **[Prompt regression — Agent reverts to listing fields]** → Covered by manual smoke tests (3.x in tasks.md) and by the MODIFIED spec requirement which any future change must respect.
- **[Frontend out of sync with backend]** → Both edits land in the same commit; the API still returns the full intake so admin consumers are unaffected.

## Migration Plan

Prompt + frontend rewrite. No data migration. Old Intake JSON files remain valid (schema unchanged). In-flight Sessions continue under the old prompt until the process restarts; the next session uses the new prompt. Rollback = revert the commit.

## Open Questions

- None.
