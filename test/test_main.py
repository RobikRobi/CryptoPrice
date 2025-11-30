import pytest


def test_websocket(client):
    with client.websocket_connect("client/ws/crypto") as ws:
       data = ws.receive_json()
       print(data)
       assert data

def test_create_user(client):
    user_data = {
        "login": "newuser",
        "email": "newuser@example.com",
        "password": "12345678",
        "dob": "12.04.1991"
    }
    response = client.post("/users/reg", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["login"] == user_data["login"]
    assert data["email"] == user_data["email"]
    assert data["password"] == user_data["password"]
    assert data["dob"] == user_data["dob"]
    assert "id" in data