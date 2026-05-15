## 1. Prompt rewrite — Confirmation Step

- [x] 1.1 In `back/services/agent.py`, rewrite the Confirmation Step rule in `_build_system_prompt` so the Agent paraphrases the Customer's problem in one or two natural sentences instead of listing labeled fields. Explicitly forbid the strings "Game System:", "Problem Category:", "Urgency Level:" and the labeled enum values.
- [x] 1.2 Update the labeled-summary example block in the prompt to a natural-language confirmation example (e.g., "So you're working through grappling rules in your 5e game — does that sound right, and are you good to file this?").
- [x] 1.3 Rewrite the correction-flow rule: when the Customer rejects the paraphrase, the Agent asks what was wrong with the problem statement, re-infers any affected fields silently, and re-presents an updated paraphrase. Forbid naming the internal field that was corrected.
- [x] 1.4 Add a new prompt rule covering all turns: the Agent never names the internal fields or labels enum values to the Customer; open follow-ups stay natural ("How time-sensitive is this for you?").

## 2. Frontend — post-submission panel

- [x] 2.1 In `front/src/components/Chat.tsx`, in the `if (intake) { return ... }` block, remove the rows that render `Game System`, `Category`, and `Urgency` to the Customer. Keep the IRN line and the problem description.
- [x] 2.2 Visually verify the panel in the running frontend after a successful submission.

## 3. Documentation

- [x] 3.1 Update the "Agent Architecture" section of `CLAUDE.md` to note that the Confirmation Step confirms the problem statement only; all four internal fields are kept off the Customer-facing surface.

## 4. Manual smoke testing

- [x] 4.1 Run a session through to confirmation. Verify the Agent's confirmation turn does NOT contain "Game System:", "Problem Category:", or "Urgency Level:" and does NOT list `Low/Medium/High` or any `GameSystem` enum as a labeled line.
- [x] 4.2 Reach confirmation, reject with "no, the urgency is lower than that". Verify the Agent re-paraphrases naturally (no field names), and the saved Intake JSON reflects the corrected `urgency_level`.
- [x] 4.3 After a successful confirmation, inspect the Customer-facing post-submission panel and verify only the IRN and problem description are shown (no `Game System`, `Category`, `Urgency` rows).
- [x] 4.4 Inspect the saved JSON in `back/data/intakes/` and confirm all four fields are still present with valid enum values — internal data model unchanged.
