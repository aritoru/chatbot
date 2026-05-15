def test_list_intakes_passes_through_storage_result(client, stub_list_intakes):
    stub_list_intakes["return_value"] = [
        {
            "issue_reference_number": "IRN-ABCDEF12",
            "created_at": "2026-05-15T10:00:00+00:00",
            "game_system": "D&D 5e",
            "problem_category": "rules clarification",
            "urgency_level": "Medium",
        },
        {
            "issue_reference_number": "IRN-99887766",
            "created_at": "2026-05-14T09:00:00+00:00",
            "game_system": "AD&D 2e",
            "problem_category": "combat mechanics",
            "urgency_level": "High",
        },
    ]

    response = client.get("/intakes")

    assert response.status_code == 200
    assert response.json() == stub_list_intakes["return_value"]
    assert stub_list_intakes["calls"] == 1


def test_list_intakes_returns_empty_list(client, stub_list_intakes):
    response = client.get("/intakes")

    assert response.status_code == 200
    assert response.json() == []


def test_get_intake_returns_full_intake_when_found(client, stub_get_intake):
    full_intake = {
        "issue_reference_number": "IRN-ABCDEF12",
        "created_at": "2026-05-15T10:00:00+00:00",
        "game_system": "D&D 5e",
        "problem_category": "rules clarification",
        "problem_description": "How does flanking work?",
        "urgency_level": "Medium",
        "summary": "Medium urgency D&D 5e issue (rules clarification): How does flanking work?",
        "conversation_transcript": [
            {"role": "agent", "content": "Hello!"},
            {"role": "customer", "content": "Hi."},
        ],
    }
    stub_get_intake["return_value"] = full_intake

    response = client.get("/intakes/IRN-ABCDEF12")

    assert response.status_code == 200
    assert response.json() == full_intake
    assert stub_get_intake["calls"] == ["IRN-ABCDEF12"]


def test_get_intake_returns_404_when_missing(client, stub_get_intake):
    stub_get_intake["return_value"] = None

    response = client.get("/intakes/IRN-NOTFOUND")

    assert response.status_code == 404
    assert response.json()["detail"] == "Intake not found"
    assert stub_get_intake["calls"] == ["IRN-NOTFOUND"]
