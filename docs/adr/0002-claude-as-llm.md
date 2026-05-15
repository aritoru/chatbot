# Claude (Anthropic API) as the LLM

The README left the LLM choice open. We chose Claude (`claude-sonnet-4-6` via the Anthropic API) over OpenAI GPT-4o. The Interview requires strict multi-step instruction following — the Agent must collect constrained fields in order, detect Knowledge Queries mid-flow without losing Interview State, re-ask pending questions correctly, and enforce Low/Medium/High and game system enumerations. Claude's instruction-following fidelity for this kind of structured conversational state machine was the deciding factor.

## Considered Options

- **OpenAI GPT-4o** — strong structured output support, widely familiar. Rejected because the Interview's dual-mode behavior (interview driver + knowledge responder) and field-level constraint enforcement benefit more from Claude's instruction adherence.
- **Claude `claude-sonnet-4-6` (chosen)** — strong at multi-step role-following, native tool use, and structured extraction via the Anthropic SDK.
