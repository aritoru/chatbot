import re

from models.interview import FrustrationSignal, Language
from services import storage

IRN_RE = re.compile(r"^IRN-[0-9A-F]{8}$")


def test_irn_has_prefix_and_eight_uppercase_hex():
    irn = storage._irn()
    assert IRN_RE.match(irn), f"unexpected IRN format: {irn!r}"


def test_irn_is_unique_across_many_calls():
    irns = {storage._irn() for _ in range(1000)}
    assert len(irns) == 1000


def test_save_intake_returns_full_intake_dict(isolated_intakes_dir, completed_session):
    intake = storage.save_intake(completed_session)

    assert IRN_RE.match(intake["issue_reference_number"])
    # created_at is ISO 8601 with timezone
    assert "T" in intake["created_at"]
    assert intake["created_at"].endswith("+00:00")
    assert intake["game_system"] == "D&D 5e"
    assert intake["problem_category"] == "rules clarification"
    assert intake["problem_description"] == "How does flanking work in 5e?"
    assert intake["urgency_level"] == "Medium"
    assert intake["summary"] == (
        "Medium urgency D&D 5e issue (rules clarification): "
        "How does flanking work in 5e?"
    )
    assert intake["conversation_transcript"] == [
        {"role": "agent", "content": "Hello!"},
        {"role": "customer", "content": "Hi, I have a question."},
    ]


def test_save_intake_round_trips_through_get_intake(isolated_intakes_dir, completed_session):
    saved = storage.save_intake(completed_session)

    fetched = storage.get_intake(saved["issue_reference_number"])

    assert fetched == saved


def test_get_intake_returns_none_for_unknown_irn(isolated_intakes_dir):
    isolated_intakes_dir.mkdir(parents=True, exist_ok=True)

    assert storage.get_intake("IRN-DEADBEEF") is None


def test_list_intakes_returns_empty_when_dir_missing(isolated_intakes_dir):
    assert not isolated_intakes_dir.exists()

    assert storage.list_intakes() == []


def test_list_intakes_projects_only_summary_fields(isolated_intakes_dir, completed_session):
    storage.save_intake(completed_session)

    entries = storage.list_intakes()

    assert len(entries) == 1
    assert set(entries[0].keys()) == {
        "issue_reference_number",
        "created_at",
        "game_system",
        "problem_category",
        "urgency_level",
    }


def _write_fake_intake(dir_path, irn):
    dir_path.mkdir(parents=True, exist_ok=True)
    (dir_path / f"{irn}.json").write_text(
        '{"issue_reference_number": "' + irn + '",'
        ' "created_at": "2026-05-15T10:00:00+00:00",'
        ' "game_system": "D&D 5e",'
        ' "problem_category": "x",'
        ' "urgency_level": "Low"}'
    )


def test_save_intake_includes_frustration_signal(isolated_intakes_dir, completed_session):
    completed_session.frustration_signal = FrustrationSignal.HIGH
    intake = storage.save_intake(completed_session)
    assert intake["frustration_signal"] == "High"


def test_save_intake_frustration_signal_defaults_to_none(isolated_intakes_dir, completed_session):
    # completed_session fixture does not set frustration_signal — defaults to NONE
    intake = storage.save_intake(completed_session)
    assert intake["frustration_signal"] == "None"


def test_save_intake_includes_language(isolated_intakes_dir, completed_session):
    completed_session.language = Language.ES
    intake = storage.save_intake(completed_session)
    assert intake["language"] == "es"


def test_save_intake_language_defaults_to_en(isolated_intakes_dir, completed_session):
    intake = storage.save_intake(completed_session)
    assert intake["language"] == "en"


def test_list_intakes_orders_by_irn_descending(isolated_intakes_dir):
    # Deliberately written out of order to prove sort is by IRN, not insertion order.
    for irn in ["IRN-11111111", "IRN-FFFFFFFF", "IRN-88888888"]:
        _write_fake_intake(isolated_intakes_dir, irn)

    entries = storage.list_intakes()
    irns = [e["issue_reference_number"] for e in entries]

    assert irns == ["IRN-FFFFFFFF", "IRN-88888888", "IRN-11111111"]
