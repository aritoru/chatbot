from unittest.mock import MagicMock, patch

import pytest

from models.interview import (
    GameSystem,
    InterviewStatus,
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
