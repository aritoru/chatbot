## 1. Prompt rewrite

- [ ] 1.1 In `back/services/agent.py`, replace the bullet describing **Game System** in the prompt's `## Rules` section with inference-first guidance: emphasize mapping any signal (direct, oblique, mechanical) to a `GameSystem` enum value, map non-AD&D/D&D references to `Other`, and explicitly prohibit listing the enum values to the Customer.
- [ ] 1.2 Replace the bullet describing **Urgency Level** with inference-first guidance: emphasize mapping urgency cues (time pressure, blocking impact, casual tone) to `Low` / `Medium` / `High`, and explicitly prohibit listing the three values.
- [ ] 1.3 Add a new prompt rule covering the fallback: if the Customer has described their problem with no signal for a constrained field, ask one open follow-up question that does **not** enumerate the valid values.
- [ ] 1.4 Add three to five concrete mapping examples directly in the prompt (e.g., "newest D&D" → `D&D 5e`, "THAC0" → `AD&D 2e`, "session tonight" → `High`) so Claude has anchors.

## 2. Confirmation summary wording

- [ ] 2.1 Update the prompt's Confirmation Step instruction to require a labeled summary line per field, using the exact enum values for `game_system` and `urgency_level` ("Game System: D&D 5e", "Urgency Level: High").
- [ ] 2.2 Verify the existing rejection/correction flow handles the new value through the same inference path — no code change expected, but read through `process_message` once to confirm.

## 3. Manual smoke testing

- [ ] 3.1 Start a session and answer "I play the one with THAC0, my session is in an hour and we're stuck on a grappling rule." Verify the Agent extracts `AD&D 2e` and `High` without listing enum values.
- [ ] 3.2 Start a session, describe a rules problem without naming the edition or expressing urgency. Verify the Agent asks an open follow-up ("Which edition are you running?") that does **not** list the enum options.
- [ ] 3.3 Start a session, say "I play Pathfinder 2e." Verify the Agent extracts `Other` and continues the Interview.
- [ ] 3.4 Reach the Confirmation Step, reject the urgency value ("actually it's not that urgent"), verify the Agent collects the new value and re-presents the summary without restarting.
- [ ] 3.5 Inspect the resulting Intake JSON in `back/data/intakes/` and confirm `game_system` and `urgency_level` hold valid enum string values and that no new fields were added.

## 4. Documentation

- [ ] 4.1 Add a one-line note to the "Agent Architecture" section of `CLAUDE.md` stating that `game_system` and `urgency_level` are inferred from conversation and only surfaced explicitly at the Confirmation Step.
- [ ] 4.2 No ADR change — the LLM choice and session-storage ADRs are unaffected.
