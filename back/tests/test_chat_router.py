import re
import uuid

UUID_RE = re.compile(r"^[0-9a-f-]{36}$")


def test_create_session_returns_id_and_opening_greeting(client, stub_opening):
    stub_opening["return_value"] = "Welcome — what game system are you playing?"

    response = client.post("/sessions")

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Welcome — what game system are you playing?"
    assert UUID_RE.match(body["session_id"])
    # sanity: the id is parseable as a real UUID
    uuid.UUID(body["session_id"])
    assert len(stub_opening["calls"]) == 1


def test_send_message_to_unknown_session_returns_404(client):
    response = client.post(
        "/sessions/nonexistent-id/messages",
        json={"message": "hello"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_in_progress_message_returns_reply_and_status(client, stub_opening, stub_process):
    stub_process["return_value"] = ("Got it — what's the urgency?", False)
    session_id = client.post("/sessions").json()["session_id"]

    response = client.post(
        f"/sessions/{session_id}/messages",
        json={"message": "D&D 5e"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Got it — what's the urgency?"
    assert body["status"] == "in_progress"
    assert body["intake"] is None
    # process_message was called with the customer's text
    assert stub_process["calls"][0][1] == "D&D 5e"


def test_confirmation_saves_intake_and_returns_it(
    client, stub_opening, stub_process, stub_save_intake
):
    stub_process["return_value"] = ("Saved!", True)
    stub_save_intake["return_value"] = {
        "irn": "IRN-ABCDEF12",
        "game_system": "D&D 5e",
    }
    session_id = client.post("/sessions").json()["session_id"]

    response = client.post(
        f"/sessions/{session_id}/messages",
        json={"message": "yes, confirm"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["intake"] == {"irn": "IRN-ABCDEF12", "game_system": "D&D 5e"}
    assert body["message"] == "Saved!"
    assert len(stub_save_intake["calls"]) == 1


def test_message_after_confirmation_returns_404(
    client, stub_opening, stub_process, stub_save_intake
):
    stub_process["return_value"] = ("Saved!", True)
    session_id = client.post("/sessions").json()["session_id"]
    client.post(f"/sessions/{session_id}/messages", json={"message": "confirm"})

    followup = client.post(
        f"/sessions/{session_id}/messages",
        json={"message": "wait, one more thing"},
    )

    assert followup.status_code == 404
    assert followup.json()["detail"] == "Session not found"


def test_delete_removes_live_session(client, stub_opening):
    session_id = client.post("/sessions").json()["session_id"]

    delete_response = client.delete(f"/sessions/{session_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Session closed"}

    followup = client.post(
        f"/sessions/{session_id}/messages",
        json={"message": "hi"},
    )
    assert followup.status_code == 404


def test_delete_unknown_session_is_idempotent(client):
    response = client.delete("/sessions/never-existed")
    assert response.status_code == 200
    assert response.json() == {"message": "Session closed"}


def test_message_response_includes_language(client, stub_opening, stub_process):
    stub_process["return_value"] = ("¡Hola!", False)
    session_id = client.post("/sessions").json()["session_id"]

    response = client.post(
        f"/sessions/{session_id}/messages",
        json={"message": "Hola"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "language" in body
    assert body["language"] == "en"  # default — no extract_field call in stub
