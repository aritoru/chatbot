from enum import Enum
from typing import Optional
from pydantic import BaseModel


class GameSystem(str, Enum):
    ADD_1E = "AD&D 1e"
    ADD_2E = "AD&D 2e"
    DND_3 = "D&D 3/3.5"
    DND_4 = "D&D 4e"
    DND_5 = "D&D 5e"
    OTHER = "Other"


class UrgencyLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class FrustrationSignal(str, Enum):
    NONE = "None"
    MILD = "Mild"
    HIGH = "High"


class Language(str, Enum):
    EN = "en"
    ES = "es"
    FR = "fr"
    IT = "it"


class InterviewStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    COMPLETED = "completed"


class InterviewFields(BaseModel):
    game_system: Optional[GameSystem] = None
    problem_category: Optional[str] = None
    problem_description: Optional[str] = None
    urgency_level: Optional[UrgencyLevel] = None

    def is_complete(self) -> bool:
        return all([
            self.game_system is not None,
            self.problem_category is not None,
            self.problem_description is not None,
            self.urgency_level is not None,
        ])


class TranscriptMessage(BaseModel):
    role: str  # "customer" or "agent"
    content: str


class Session:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.fields = InterviewFields()
        self.status = InterviewStatus.IN_PROGRESS
        self.frustration_signal = FrustrationSignal.NONE
        self.language = Language.EN
        self.transcript: list[TranscriptMessage] = []
        self.claude_messages: list[dict] = []
