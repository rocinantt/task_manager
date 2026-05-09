import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db
from routers.tasks import _top_cache


# --- Тестовая БД --- 
TEST_DATABASE_URL = "sqlite:///:memory:"

# Тестовая бд в памяти, отдельный  engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool, # все сесии видят одни и те же таблицйы
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture
def db_session():
    "Новая бд  на каждый  тест"
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db_session):
    "TestClient с подменой get_db на тестовую сессию."

    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # сессию закроет фикстура db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    # Убираем override после теста  чтобы не перетекло в другие тесты
    app.dependency_overrides.clear()


@pytest.fixture
def auth_client(client):
    "Зарегистрированный и авторизованный тестовый юзер"
    client.post(
        "/users/register",
        json={"username" : "test_user", "password" : "test_password"}
    )

    response = client.post(
        "/users/login",
        data={"username": "test_user", "password": "test_password"},
    )

    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture
def auth_client_2(client):
    """Второй аЗарегистрированный и авторизованный тестовый юзер для тестов изоляции данных между юзерами."""
    client.post(
        "/users/register",
        json={"username": "test_user_2", "password": "test_password_2"},
    )
    response = client.post(
        "/users/login",
        data={"username": "test_user_2", "password": "test_password_2"},
    )
    token = response.json()["access_token"]
    # новый клиент — отдельный TestClient с тем же app.
    from fastapi.testclient import TestClient
    from main import app
    c2 = TestClient(app)
    c2.headers.update({"Authorization": f"Bearer {token}"})
    return c2


@pytest.fixture(autouse=True)
def clear_top_cache():
    """Перед каждым тестом автоматическая чистка кэша"""

    _top_cache.clear()
    yield
    _top_cache.clear()
