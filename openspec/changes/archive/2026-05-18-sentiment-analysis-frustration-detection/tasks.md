## 1. Data Model

- [x] 1.1 Add `FrustrationSignal` enum (`None`, `Mild`, `High`) to `back/models/interview.py`, following the same pattern as `UrgencyLevel`
- [x] 1.2 Add `frustration_signal: FrustrationSignal = FrustrationSignal.NONE` field to `Session` in `back/models/interview.py`
- [x] 1.3 Add `frustration_signal` field to the `Intake` model so it is persisted in the JSON written to disk

## 2. Tool Extension

- [x] 2.1 Add `"frustration_signal"` to the `field_name` enum in the `extract_field` tool definition in `back/services/agent.py`
- [x] 2.2 Add a `FrustrationSignal` dispatch branch to `_apply_field` in `back/services/agent.py`: map `"None"` → `FrustrationSignal.NONE`, `"Mild"` → `FrustrationSignal.MILD`, `"High"` → `FrustrationSignal.HIGH`; ignore invalid values silently

## 3. System Prompt Integration

- [x] 3.1 In `_build_system_prompt`, inject a Frustration Signal directive block when `session.frustration_signal` is `Mild` or `High` (no directive for `None`)
- [x] 3.2 `Mild` directive: acknowledge any difficulty, ask at most one clarifying question, use empathetic tone
- [x] 3.3 `High` directive: skip optional clarifying questions, bias `urgency_level` inference toward `High`, move to Confirmation Step as quickly as possible
- [x] 3.4 Add system prompt instruction instructing Claude to call `extract_field(field_name="frustration_signal", ...)` on every Customer turn based on the Customer's tone, word choice, and message length

## 4. Constrained Field Inference Update

- [x] 4.1 Update the `urgency_level` inference section of the system prompt to bias toward `High` when `frustration_signal` is `High` and no explicit urgency signal is present

## 5. Intake Persistence

- [x] 5.1 In `back/services/storage.py`, include `frustration_signal` when serialising the `Session` to an Intake JSON file

## 6. Tests

- [x] 6.1 Add `_apply_field` dispatch tests in `back/tests/test_agent.py`: `extract_field(frustration_signal, "Mild")` sets `session.frustration_signal`; invalid value is ignored
- [x] 6.2 Add agent behaviour tests: `Mild`-signal turn includes empathetic directive in prompt; `High`-signal turn skips clarifying question and fast-tracks confirmation
- [x] 6.3 Add test: `frustration_signal` is absent from the `POST /sessions/{id}/messages` HTTP response body
- [x] 6.4 Add test: `frustration_signal` is present in the Intake JSON after `confirm_intake`

## 7. Verification

- [x] 7.1 Run full test suite (`pytest back/tests/`) — all tests pass
- [x] 7.2 Manual smoke test: start a session, send progressively frustrated messages, verify Agent tone shifts and Intake is confirmed without extra questions
- [x] 7.3 Check `GET /intakes/{irn}` response includes `frustration_signal` field
