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
