import os

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-not-used")

import pytest
from fastapi.testclient import TestClient

from main import app
from models.interview import (
    GameSystem,
    InterviewFields,
    Session,
    TranscriptMessage,
    UrgencyLevel,
)
from routers import chat as chat_router
from routers import intakes as intakes_router
from services import storage


@pytest.fixture
def client():
    chat_router._sessions.clear()
    return TestClient(app)


@pytest.fixture
def stub_opening(monkeypatch):
    """Replace get_opening_message on the router with a configurable async stub."""
    state = {"return_value": "Welcome to AD&DHelp!", "calls": []}

    async def _stub(session):
        state["calls"].append(session)
        return state["return_value"]

    monkeypatch.setattr(chat_router, "get_opening_message", _stub)
    return state


@pytest.fixture
def stub_process(monkeypatch):
    """Replace process_message on the router. Default: ('ok', False) — in-progress."""
    state = {"return_value": ("ok", False), "calls": []}

    async def _stub(session, user_message):
        state["calls"].append((session, user_message))
        return state["return_value"]

    monkeypatch.setattr(chat_router, "process_message", _stub)
    return state


@pytest.fixture
def stub_save_intake(monkeypatch):
    """Replace save_intake on the router with a callable returning a dict."""
    state = {"return_value": {"irn": "IRN-DEADBEEF"}, "calls": []}

    def _stub(session):
        state["calls"].append(session)
        return state["return_value"]

    monkeypatch.setattr(chat_router, "save_intake", _stub)
    return state


@pytest.fixture
def stub_list_intakes(monkeypatch):
    """Replace list_intakes on the intakes router with a configurable stub."""
    state = {"return_value": [], "calls": 0}

    def _stub():
        state["calls"] += 1
        return state["return_value"]

    monkeypatch.setattr(intakes_router, "list_intakes", _stub)
    return state


@pytest.fixture
def stub_get_intake(monkeypatch):
    """Replace get_intake on the intakes router. Default: returns None (not found)."""
    state = {"return_value": None, "calls": []}

    def _stub(irn):
        state["calls"].append(irn)
        return state["return_value"]

    monkeypatch.setattr(intakes_router, "get_intake", _stub)
    return state


@pytest.fixture
def isolated_intakes_dir(tmp_path, monkeypatch):
    """Redirect storage.INTAKES_DIR to a fresh tmp_path subdir. Returns the path."""
    intakes_dir = tmp_path / "intakes"
    monkeypatch.setattr(storage, "INTAKES_DIR", intakes_dir)
    return intakes_dir


@pytest.fixture
def completed_session():
    """A Session with all four fields filled and a small transcript."""
    session = Session("test-session")
    session.fields = InterviewFields(
        game_system=GameSystem.DND_5,
        problem_category="rules clarification",
        problem_description="How does flanking work in 5e?",
        urgency_level=UrgencyLevel.MEDIUM,
    )
    session.transcript = [
        TranscriptMessage(role="agent", content="Hello!"),
        TranscriptMessage(role="customer", content="Hi, I have a question."),
    ]
    return session
