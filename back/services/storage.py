import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

INTAKES_DIR = Path("data/intakes")


def _irn() -> str:
    return f"IRN-{uuid.uuid4().hex[:8].upper()}"


def save_intake(session) -> dict:
    INTAKES_DIR.mkdir(parents=True, exist_ok=True)

    irn = _irn()
    fields = session.fields

    intake = {
        "issue_reference_number": irn,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "game_system": fields.game_system.value,
        "problem_category": fields.problem_category,
        "problem_description": fields.problem_description,
        "urgency_level": fields.urgency_level.value,
        "summary": (
            f"{fields.urgency_level.value} urgency {fields.game_system.value} issue "
            f"({fields.problem_category}): {fields.problem_description}"
        ),
        "conversation_transcript": [
            {"role": m.role, "content": m.content}
            for m in session.transcript
        ],
    }

    (INTAKES_DIR / f"{irn}.json").write_text(json.dumps(intake, indent=2))
    return intake


def list_intakes() -> list[dict]:
    if not INTAKES_DIR.exists():
        return []
    result = []
    for path in sorted(INTAKES_DIR.glob("IRN-*.json"), reverse=True):
        data = json.loads(path.read_text())
        result.append({
            "issue_reference_number": data["issue_reference_number"],
            "created_at": data["created_at"],
            "game_system": data["game_system"],
            "problem_category": data["problem_category"],
            "urgency_level": data["urgency_level"],
        })
    return result


def get_intake(irn: str) -> dict | None:
    path = INTAKES_DIR / f"{irn}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())
