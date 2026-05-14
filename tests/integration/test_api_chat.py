import pytest

import twilio_phone_server


@pytest.fixture
def client():
    twilio_phone_server.app.config["TESTING"] = True
    twilio_phone_server.sessions.clear()

    with twilio_phone_server.app.test_client() as test_client:
        yield test_client

    twilio_phone_server.sessions.clear()


@pytest.mark.integration
def test_api_chat_add_pizza_and_total(client):
    """
    Given the Flask API is running
    When a tester sends order messages through /api/chat
    Then the API preserves session state and returns order responses
    """
    response1 = client.post(
        "/api/chat",
        json={
            "session_id": "api-test-1",
            "text": "I want a large pepperoni pizza",
        },
    )

    assert response1.status_code == 200
    data1 = response1.get_json()

    assert "Added 1 large pepperoni pizza" in data1["reply"]
    assert len(data1["order"]) == 1
    assert data1["order"][0]["base"] == "pepperoni"

    response2 = client.post(
        "/api/chat",
        json={
            "session_id": "api-test-1",
            "text": "what is my total",
        },
    )

    assert response2.status_code == 200
    data2 = response2.get_json()

    assert "Your total is" in data2["reply"]
    assert "$" in data2["reply"]
    assert len(data2["order"]) == 1


@pytest.mark.integration
def test_api_chat_separate_sessions_do_not_share_orders(client):
    """
    Given two different API sessions
    When each session sends messages
    Then orders remain isolated by session_id
    """
    client.post(
        "/api/chat",
        json={
            "session_id": "session-a",
            "text": "I want a large pepperoni pizza",
        },
    )

    response = client.post(
        "/api/chat",
        json={
            "session_id": "session-b",
            "text": "what is my total",
        },
    )

    assert response.status_code == 200
    data = response.get_json()

    assert data["order"] == []
    assert "Your total is" in data["reply"]