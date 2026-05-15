import os
import anthropic
from models.interview import (
    GameSystem, UrgencyLevel, InterviewFields,
    InterviewStatus, Session, TranscriptMessage,
)

_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

_TOOLS = [
    {
        "name": "extract_field",
        "description": (
            "Call this whenever you successfully extract a valid value for an interview field "
            "from the customer's response. Only call it with values that pass validation "
            "(correct enum values for game_system and urgency_level)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "field_name": {
                    "type": "string",
                    "enum": ["game_system", "problem_category", "problem_description", "urgency_level"],
                },
                "field_value": {"type": "string"},
            },
            "required": ["field_name", "field_value"],
        },
    },
    {
        "name": "confirm_intake",
        "description": "Call this when the customer has confirmed that all their information is correct and the intake should be saved.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]


def _build_system_prompt(fields: InterviewFields, status: InterviewStatus) -> str:
    def _val(v) -> str:
        return v.value if v is not None else "NOT YET COLLECTED"

    state = (
        f"- Game System: {_val(fields.game_system)}\n"
        f"- Problem Category: {fields.problem_category or 'NOT YET COLLECTED'}\n"
        f"- Problem Description: {fields.problem_description or 'NOT YET COLLECTED'}\n"
        f"- Urgency Level: {_val(fields.urgency_level)}"
    )
    interview_status = (
        "All fields collected — awaiting customer confirmation."
        if status == InterviewStatus.AWAITING_CONFIRMATION
        else "Interview in progress."
    )

    return f"""You are an AD&DHelp support agent for a fictional business that helps customers with Advanced Dungeons & Dragons (AD&D) RPG questions. You are friendly, knowledgeable, and professional.

Your primary task is to conduct a structured interview to collect exactly four fields from the customer:

1. **Game System** — must be one of: "AD&D 1e", "AD&D 2e", "D&D 3/3.5", "D&D 4e", "D&D 5e", "Other"
2. **Problem Category** — free text (e.g. "rules clarification", "combat mechanics", "character creation")
3. **Problem Description** — a detailed description of their issue (free text)
4. **Urgency Level** — must be exactly "Low", "Medium", or "High"

## Current Interview State
Status: {interview_status}
{state}

## Rules
- Collect missing fields one at a time, in order.
- **Game System**: if the customer says something close (e.g. "second edition"), map it to the correct enum value and call extract_field. If genuinely ambiguous, present the list and re-ask.
- **Urgency Level**: if the customer says something like "very urgent", map it to "High" and call extract_field. If unclear, present the three options.
- Call extract_field immediately whenever you collect a valid value — do not wait.
- When all four fields are collected, present a clear numbered summary and ask the customer to confirm.
- If the customer confirms, call confirm_intake.
- If the customer rejects, ask which field they want to correct, collect the new value (call extract_field), then re-present the full summary.
- If the customer asks an AD&D knowledge question mid-interview, answer it fully and accurately, then explicitly re-ask the pending interview question.
- Be conversational and natural. Do not sound like you are filling out a form."""


def _apply_field(fields: InterviewFields, field_name: str, field_value: str) -> None:
    if field_name == "game_system":
        try:
            fields.game_system = GameSystem(field_value)
        except ValueError:
            pass  # Claude should only call this with a valid enum value
    elif field_name == "urgency_level":
        try:
            fields.urgency_level = UrgencyLevel(field_value)
        except ValueError:
            pass
    elif field_name == "problem_category":
        fields.problem_category = field_value
    elif field_name == "problem_description":
        fields.problem_description = field_value


async def get_opening_message(session: Session) -> str:
    system = _build_system_prompt(session.fields, session.status)
    init = [{"role": "user", "content": "[BEGIN INTERVIEW]"}]

    response = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=system + "\n\nThe customer has just arrived. Generate a warm opening greeting, introduce yourself briefly, and ask for their game system.",
        messages=init,
    )

    greeting = next((b.text for b in response.content if b.type == "text"), "Hello! Welcome to AD&DHelp.")

    # Seed claude_messages so the opening is part of conversation history
    session.claude_messages.extend([
        {"role": "user", "content": "[BEGIN INTERVIEW]"},
        {"role": "assistant", "content": [b.model_dump() for b in response.content]},
    ])
    session.transcript.append(TranscriptMessage(role="agent", content=greeting))
    return greeting


async def process_message(session: Session, user_message: str) -> tuple[str, bool]:
    """Send a customer message, run the agentic tool loop, return (agent_text, intake_confirmed)."""
    session.claude_messages.append({"role": "user", "content": user_message})
    session.transcript.append(TranscriptMessage(role="customer", content=user_message))

    intake_confirmed = False
    agent_text = ""

    while True:
        system = _build_system_prompt(session.fields, session.status)
        response = _client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system,
            tools=_TOOLS,
            messages=session.claude_messages,
        )

        session.claude_messages.append({
            "role": "assistant",
            "content": [b.model_dump() for b in response.content],
        })

        tool_results = []
        for block in response.content:
            if block.type == "text":
                agent_text = block.text
            elif block.type == "tool_use":
                if block.name == "extract_field":
                    _apply_field(session.fields, block.input["field_name"], block.input["field_value"])
                    if session.fields.is_complete():
                        session.status = InterviewStatus.AWAITING_CONFIRMATION
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": "Field updated.",
                    })
                elif block.name == "confirm_intake":
                    intake_confirmed = True
                    session.status = InterviewStatus.COMPLETED
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": "Intake confirmed.",
                    })

        if tool_results:
            session.claude_messages.append({"role": "user", "content": tool_results})
        else:
            break

    if agent_text:
        session.transcript.append(TranscriptMessage(role="agent", content=agent_text))

    return agent_text, intake_confirmed
