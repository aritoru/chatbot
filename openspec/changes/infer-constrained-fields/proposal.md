## Why

The Agent currently treats `game_system` and `urgency_level` as menu pickers — when the Customer's response doesn't cleanly map to an enum value, the system prompt instructs the Agent to "present the list and re-ask." This breaks the natural conversational tone of the Interview: a Customer who says "it's pretty bad, my whole party is stuck" gets asked to pick Low/Medium/High instead of being heard. We want the Agent to infer these fields from the natural flow of the conversation, only asking a direct question when inference genuinely fails.

## What Changes

- Agent stops presenting enumerated options for `game_system` and `urgency_level` as the default behavior.
- Agent infers both fields from any signal in the conversation — game edition references ("3.5", "newest D&D", "the one with THAC0"), urgency cues ("urgent", "no rush", "blocking my game tonight").
- Agent only falls back to a direct question (still without showing the menu) when no signal is present after the Customer has spoken about their problem.
- At the **Confirmation Step**, the inferred normalized value is shown back to the Customer ("Game System: D&D 5e — is that right?"), giving them a chance to correct an inference error without ever seeing the menu during the interview.
- The Intake JSON shape is **unchanged** — `game_system` remains a `GameSystem` enum, `urgency_level` remains a `UrgencyLevel` enum. Only the collection UX changes.
- System prompt in `back/services/agent.py` is rewritten to describe inference behavior instead of menu-driven validation.

## Capabilities

### New Capabilities
- `constrained-field-inference`: How the Agent collects fields backed by closed enumerations (`game_system`, `urgency_level`) by inferring values from conversational signals rather than presenting menus, with explicit confirmation as the safety net.

### Modified Capabilities
<!-- None — no prior specs exist for the interview flow. -->

## Impact

- **Code**: `back/services/agent.py` system prompt rewritten. No changes to `back/models/interview.py`, routers, or storage.
- **API**: No HTTP contract changes. Intake JSON shape unchanged.
- **Frontend**: No changes required — the chat UI already renders free-form Agent messages.
- **Docs**: `CLAUDE.md` agent-architecture section needs a one-line note that constrained fields are inferred. ADRs unchanged.
- **Risk**: Inference can be wrong. Mitigated by mandatory confirmation at the summary step; field-by-field correction on rejection already exists and is reused for inference errors.
