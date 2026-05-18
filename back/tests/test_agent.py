from unittest.mock import MagicMock, patch

import pytest

from models.interview import (
    FrustrationSignal,
    GameSystem,
    InterviewStatus,
    Language,
    Session,
    UrgencyLevel,
)
from services import agent


def _text_block(text: str) -> MagicMock:
    block = MagicMock()
    block.type = "text"
    block.text = text
    block.model_dump.return_value = {"type": "text", "text": text}
    return block


def _tool_block(name: str, tool_id: str, inputs: dict) -> MagicMock:
    block = MagicMock()
    block.type = "tool_use"
    block.name = name
    block.id = tool_id
    block.input = inputs
    block.model_dump.return_value = {"type": "tool_use", "name": name, "id": tool_id, "input": inputs}
    return block


def _response(*blocks) -> MagicMock:
    r = MagicMock()
    r.content = list(blocks)
    return r


# ── Helpers ───────────────────────────────────────────────────────────────────

def _new_session() -> Session:
    return Session("s1")


# ── Tracer bullet ──────────────────────────────────────────────────────────────

async def test_text_reply_returns_text_and_not_confirmed():
    session = Session("s1")
    mock_response = _response(_text_block("Which edition are you playing?"))

    with patch.object(agent._client.messages, "create", return_value=mock_response):
        reply, confirmed = await agent.process_message(session, "Hello")

    assert reply == "Which edition are you playing?"
    assert confirmed is False
    assert session.transcript[-1].role == "agent"
    assert session.transcript[-1].content == "Which edition are you playing?"


# ── Field extraction ───────────────────────────────────────────────────────────

async def test_extract_field_tool_call_sets_game_system():
    session = _new_session()
    responses = [
        _response(_tool_block("extract_field", "t1", {"field_name": "game_system", "field_value": "D&D 5e"})),
        _response(_text_block("Got it — what's the problem?")),
    ]

    with patch.object(agent._client.messages, "create", side_effect=responses):
        await agent.process_message(session, "I play 5e")

    assert session.fields.game_system == GameSystem.DND_5


async def test_extract_field_with_invalid_enum_value_is_ignored():
    session = _new_session()
    responses = [
        _response(_tool_block("extract_field", "t1", {"field_name": "game_system", "field_value": "NotAnEdition"})),
        _response(_text_block("Which edition are you playing?")),
    ]

    with patch.object(agent._client.messages, "create", side_effect=responses):
        await agent.process_message(session, "I play some RPG")

    assert session.fields.game_system is None


# ── Status transitions ─────────────────────────────────────────────────────────

async def test_all_fields_extracted_transitions_status_to_awaiting_confirmation():
    session = _new_session()
    responses = [
        _response(
            _tool_block("extract_field", "t1", {"field_name": "game_system", "field_value": "D&D 5e"}),
            _tool_block("extract_field", "t2", {"field_name": "problem_category", "field_value": "rules"}),
            _tool_block("extract_field", "t3", {"field_name": "problem_description", "field_value": "How does flanking work?"}),
            _tool_block("extract_field", "t4", {"field_name": "urgency_level", "field_value": "High"}),
        ),
        _response(_text_block("Does that sound right?")),
    ]

    with patch.object(agent._client.messages, "create", side_effect=responses):
        await agent.process_message(session, "I need help fast")

    assert session.status == InterviewStatus.AWAITING_CONFIRMATION


async def test_confirm_intake_returns_confirmed_and_sets_status_completed():
    session = _new_session()
    responses = [
        _response(
            _tool_block("confirm_intake", "t1", {}),
            _text_block("Your intake has been filed!"),
        ),
    ]

    with patch.object(agent._client.messages, "create", side_effect=responses):
        reply, confirmed = await agent.process_message(session, "yes, that's right")

    assert confirmed is True
    assert reply == "Your intake has been filed!"
    assert session.status == InterviewStatus.COMPLETED


# ── Frustration signal dispatch ────────────────────────────────────────────────

async def test_extract_frustration_signal_mild_sets_session_field():
    session = _new_session()
    responses = [
        _response(_tool_block("extract_field", "t1", {"field_name": "frustration_signal", "field_value": "Mild"})),
        _response(_text_block("I understand — let me help.")),
    ]

    with patch.object(agent._client.messages, "create", side_effect=responses):
        await agent.process_message(session, "ugh, I already said it's 5e")

    assert session.frustration_signal == FrustrationSignal.MILD


async def test_extract_frustration_signal_high_sets_session_field():
    session = _new_session()
    responses = [
        _response(_tool_block("extract_field", "t1", {"field_name": "frustration_signal", "field_value": "High"})),
        _response(_text_block("I hear you — let's get this sorted quickly.")),
    ]

    with patch.object(agent._client.messages, "create", side_effect=responses):
        await agent.process_message(session, "THIS IS TAKING FOREVER")

    assert session.frustration_signal == FrustrationSignal.HIGH


async def test_extract_frustration_signal_invalid_value_is_ignored():
    session = _new_session()
    responses = [
        _response(_tool_block("extract_field", "t1", {"field_name": "frustration_signal", "field_value": "Furious"})),
        _response(_text_block("Got it.")),
    ]

    with patch.object(agent._client.messages, "create", side_effect=responses):
        await agent.process_message(session, "whatever")

    assert session.frustration_signal == FrustrationSignal.NONE


# ── Frustration directive in system prompt ─────────────────────────────────────

def test_system_prompt_contains_no_frustration_directive_when_none():
    session = _new_session()
    prompt = agent._build_system_prompt(session)
    # The rules section always references "Frustration Signal" for the extract_field instruction;
    # what must be absent is the level-specific directive block.
    assert "Frustration Signal: Mild" not in prompt
    assert "Frustration Signal: High" not in prompt


def test_system_prompt_contains_mild_directive():
    session = _new_session()
    session.frustration_signal = FrustrationSignal.MILD
    prompt = agent._build_system_prompt(session)
    assert "Frustration Signal: Mild" in prompt
    assert "empathetic" in prompt


def test_system_prompt_contains_high_directive():
    session = _new_session()
    session.frustration_signal = FrustrationSignal.HIGH
    prompt = agent._build_system_prompt(session)
    assert "Frustration Signal: High" in prompt
    assert "Skip any optional clarifying questions" in prompt


def test_system_prompt_high_frustration_biases_urgency():
    session = _new_session()
    session.frustration_signal = FrustrationSignal.HIGH
    prompt = agent._build_system_prompt(session)
    assert "default to inferring `High` urgency" in prompt


# ── Language dispatch ─────────────────────────────────────────────────────────

async def test_extract_language_spanish_sets_session_field():
    session = _new_session()
    responses = [
        _response(_tool_block("extract_field", "t1", {"field_name": "language", "field_value": "es"})),
        _response(_text_block("¡Hola! ¿En qué puedo ayudarte?")),
    ]

    with patch.object(agent._client.messages, "create", side_effect=responses):
        await agent.process_message(session, "Hola, tengo una pregunta")

    assert session.language == Language.ES


async def test_extract_language_invalid_code_is_ignored():
    session = _new_session()
    responses = [
        _response(_tool_block("extract_field", "t1", {"field_name": "language", "field_value": "klingon"})),
        _response(_text_block("Hello!")),
    ]

    with patch.object(agent._client.messages, "create", side_effect=responses):
        await agent.process_message(session, "hi")

    assert session.language == Language.EN


async def test_language_locked_once_non_english_detected():
    session = _new_session()
    session.language = Language.ES
    responses = [
        _response(_tool_block("extract_field", "t1", {"field_name": "language", "field_value": "fr"})),
        _response(_text_block("Hola.")),
    ]

    with patch.object(agent._client.messages, "create", side_effect=responses):
        await agent.process_message(session, "whatever")

    assert session.language == Language.ES


# ── Language directive in system prompt ───────────────────────────────────────

def test_system_prompt_contains_no_language_directive_for_english():
    session = _new_session()
    prompt = agent._build_system_prompt(session)
    assert "Respond in" not in prompt
    assert "## Language" not in prompt


def test_system_prompt_contains_spanish_directive():
    session = _new_session()
    session.language = Language.ES
    prompt = agent._build_system_prompt(session)
    assert "Spanish" in prompt
    assert "extract_field" in prompt


def test_system_prompt_contains_french_directive():
    session = _new_session()
    session.language = Language.FR
    prompt = agent._build_system_prompt(session)
    assert "French" in prompt


def test_system_prompt_contains_italian_directive():
    session = _new_session()
    session.language = Language.IT
    prompt = agent._build_system_prompt(session)
    assert "Italian" in prompt


# ── frustration_signal absent from HTTP message response ──────────────────────

async def test_process_message_result_does_not_expose_frustration_signal():
    """process_message returns (agent_text, confirmed) — frustration_signal is not in the tuple."""
    session = _new_session()
    responses = [
        _response(_tool_block("extract_field", "t1", {"field_name": "frustration_signal", "field_value": "High"})),
        _response(_text_block("Let me help you quickly.")),
    ]

    with patch.object(agent._client.messages, "create", side_effect=responses):
        result = await agent.process_message(session, "JUST ANSWER ME")

    # result is a 2-tuple; frustration_signal must not leak into it
    assert len(result) == 2
    agent_text, confirmed = result
    assert "frustration_signal" not in agent_text
    assert isinstance(confirmed, bool)
