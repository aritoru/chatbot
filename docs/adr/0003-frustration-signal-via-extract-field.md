# ADR 0003: Frustration Signal recorded via the existing `extract_field` tool

## Status

Accepted

## Context

The Frustration Signal feature requires Claude to classify the Customer's emotional state (`None`, `Mild`, `High`) on every turn and store the result in `Session.frustration_signal`. The question was whether to introduce a dedicated `update_frustration_signal(level)` tool or extend the existing `extract_field` tool's `field_name` enum with `"frustration_signal"`.

## Decision

Extend `extract_field` — add `"frustration_signal"` as a valid `field_name` value.

## Rationale

The tool loop processes `extract_field` calls identically regardless of which field is named: call `_apply_field`, append a tool result, loop. Adding `frustration_signal` to the enum requires one line in the tool schema and one branch in `_apply_field`. A dedicated tool would add the same processing path with a different name and no functional difference.

The semantic objection — that `frustration_signal` is an Agent observation rather than a customer-provided field — is real but not load-bearing. `urgency_level` and `game_system` are already inferred by Claude rather than stated by the Customer; `extract_field` has always been "Claude calls this when it settles on a value," not "Customer provided this value."

## Consequences

- Future developers reading `_TOOLS` will see `frustration_signal` alongside customer-interview fields and may wonder why. This ADR provides the explanation.
- If a future Agent observation cannot be cleanly expressed as a string value matched to an enum, a dedicated tool will be needed at that point. `extract_field` should not be extended further without revisiting this decision.
