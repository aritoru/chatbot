import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models.interview import Session, InterviewStatus
from services.agent import get_opening_message, process_message
from services.storage import save_intake

router = APIRouter(prefix="/sessions", tags=["chat"])

_sessions: dict[str, Session] = {}


class SendMessageRequest(BaseModel):
    message: str


@router.post("")
async def create_session():
    session_id = str(uuid.uuid4())
    session = Session(session_id)
    _sessions[session_id] = session
    opening = await get_opening_message(session)
    return {"session_id": session_id, "message": opening}


@router.post("/{session_id}/messages")
async def send_message(session_id: str, body: SendMessageRequest):
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status == InterviewStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Interview already completed")

    agent_text, intake_confirmed = await process_message(session, body.message)

    intake = None
    if intake_confirmed:
        intake = save_intake(session)
        del _sessions[session_id]

    return {
        "message": agent_text,
        "status": InterviewStatus.COMPLETED if intake_confirmed else session.status,
        "intake": intake,
    }


@router.delete("/{session_id}")
async def close_session(session_id: str):
    _sessions.pop(session_id, None)
    return {"message": "Session closed"}
