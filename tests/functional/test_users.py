import pytest


# --- register ---

def test_register_creates_user(client):
    "Валидные данные -> 201  + отсутствие пароля/хэша  в данных" 
    response = client.post("/users/register", json={"username": "borat", "password": "borat"})

    assert response.status_code == 201
    data  = response.json()

    assert  data["username"] == "borat"
    assert "id"  in data
    assert "password" not in data
    assert "hashed_password" not in data


def  test_register_duplicate_username_return_400(client):
    "Регистрация  занятого юзернейма -> 400"
    client.post("/users/register", json={"username": "borat", "password": "borat"})
    response = client.post("/users/register", json={"username": "borat", "password": "borat"})

    assert response.status_code == 400


def test_register_missing_password_return_422(client):
    "Нет обязательного  поля  -> 422"
    response = client.post("/users/register", json={"username": "borat"})

    assert  response.status_code == 422


# --- login ---

def test_login_returns_token(client):
    "Правильные креды -> 200 + токен"
    client.post("/users/register", json={"username": "borat", "password": "borat"})
    response = client.post("/users/login", data={"username": "borat", "password": "borat"})

    assert response.status_code == 200
    data  = response.json()
    
    assert "access_token" in data
    assert "access_token" != ""


def test_login_wrong_password_returns_401(client):
    "Существующий юзер + неверный пароль -> 401"
    client.post("/users/register", json={"username": "borat", "password": "borat"})
    response = client.post("/users/login", data={"username": "borat", "password": "azamat"})

    assert response.status_code == 401


def test_login_unknown_user_return_401(client):
    "Несуществующий юзер -> 401"
    response = client.post("/users/login", data={"username": "borat", "password": "borat"})

    assert response.status_code == 401


def test_protected_endpoint_with_invalid_token_returtns_401(client):
    "Битый токен -> 401"

    response = client.get("/tasks/", headers={"Authorization": "Bearer ........"})
    assert response.status_code == 401


