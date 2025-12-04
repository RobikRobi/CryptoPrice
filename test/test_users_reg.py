import datetime
import pytest

# @pytest.mark.asyncio
# async def test_reg_user_ok(async_client):
#     resp = await async_client.post(
#         "/users/reg",
#         json={
#             "login": "testuser",
#             "email": "test@mail.com",
#             "password": "123456"
#         }
#     )

#     assert resp.status_code == 200
#     data = resp.json()
#     assert data["login"] == "testuser"
#     assert "token" in data

# Тест на создание пользователя
@pytest.mark.asyncio
async def test_reg(async_client):
    payload = {
        "login": "john",
        "email": "john@example.com",
        "password": "12345",
        "dob": str(datetime.date(2000, 12, 1))
    }

    response = await async_client.post("/users/reg", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["login"] == payload["login"]
    assert data["email"] == payload["email"]
    assert "token" in data
    assert "id" not in data

# Тест на добавление уже существующего пользователя
@pytest.mark.asyncio
async def test_reg_user_exists(async_client):
    payload = {
        "login": "john",
        "email": "john@example.com",
        "password": "12345",
        "dob": "2000-12-01"
    }

    # Первый запрос — создаём
    await async_client.post("/users/reg", json=payload)

    # Второй — должны получить ошибку
    response = await async_client.post("/users/reg", json=payload)

    assert response.status_code == 411
    assert response.json()["detail"]["data"] == "user is exists"
