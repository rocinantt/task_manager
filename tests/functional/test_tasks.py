def _create_task(client, **overrides):
    "Создает задачу с  дефолтными полями + overrides и возвращает JSON ответа"
    payload = {"title": "default", "description": "", "priority": 1}
    payload.update(overrides)
    response = client.post("/tasks/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()



# --- Создание tasks ---

def test_create_task_minimal(auth_client):
    "Создание таски с обязательным полем"
    response = auth_client.post("/tasks/", json={"title": "test"})

    assert response.status_code == 201
    data = response.json()
    assert 'id' in data and 'owner_id' in data and 'created_at' in data
    assert data.get("priority") == 1
    assert data.get("status") == "в ожидании"


def test_create_task_full(auth_client):
    "Создание таски со всеми полями"
    response = auth_client.post("/tasks/", json={
        "title": "test",
        "description": "test_description",
        "priority": 3,
        "status": "в работе"
        })

    assert response.status_code == 201
    data = response.json()

    assert 'id' in data and 'owner_id' in data and 'created_at' in data
    assert data.get("description") == "test_description"
    assert data.get("priority") == 3
    assert data.get("status") == "в работе"


def test_create_task_invalid_priority_returns_422(auth_client):
    # Проверка некорректности создания задачи с невалидным уровнем приоритета 
    response = auth_client.post("/tasks/", json={"title": "test", "priority": 666})
    assert response.status_code == 422


def test_create_task_invalid_status_returns_422(auth_client):
    # Проверка некорректности создания задачи с невалидным статусом
    response = auth_client.post("/tasks/", json={"title": "test", "status": "отложил"})
    assert response.status_code == 422


# --- Список tasks ---

def test_list_tasks_empty(auth_client):
    """У свежего юзера - пустой список"""
    response = auth_client.get("/tasks/")

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_returns_only_own_tasks(auth_client, auth_client_2):
    "Проверка изоляции задач"
    _create_task(auth_client, title='borat_tasks')
    _create_task(auth_client_2, title='azamat_tasks')

    response = auth_client.get("/tasks/")
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "borat_tasks"


def test_list_tasks_sort_by_priority(auth_client):
    "Сортировка по приоритету"
    _create_task(auth_client, title="low", priority=1)
    _create_task(auth_client, title="high", priority=5)
    _create_task(auth_client, title="mid", priority=3)

    response = auth_client.get("/tasks/?sort_by=priority")
    titles = [t['title'] for t in response.json()]

    assert titles == ['low', 'mid', 'high']


# --- task по id ---

def test_get_task_by_id(auth_client):
    "Нахождение таски по id"
    created = _create_task(auth_client, title='test')
    response = auth_client.get(f"/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json()['title'] == 'test'


def test_get_task_not_found(auth_client):
    "Поиск несуществующей таски -> 404"
    response = auth_client.get(f"/tasks/666")
    assert response.status_code == 404


# --- put task ---

def test_update_task(auth_client):
    "Проверка обновления таски"
    created = _create_task(auth_client, title='old', priority=1)
    response = auth_client.put(
        f"/tasks/{created['id']}",
        json={'title': 'new', 'priority': 5}
    )

    assert response.status_code == 200
    data = response.json()

    assert data['title'] == 'new'
    assert data['priority'] == 5


def test_update_task_not_found(auth_client):
    "Обновлении несуществующей таски"
    response = auth_client.put(
        "/tasks/666",
        json={'title': 'new', 'priority': 5}
    )

    assert response.status_code == 404


# --- delete tasks по id ---

def test_delete_task(auth_client):
    "Проверка удаление ветки + 404 после удаления"
    created = _create_task(auth_client, title='old', priority=1)
    response = auth_client.delete(f"/tasks/{created['id']}")
    assert response.status_code == 204

    check = auth_client.get(f"/tasks/{created['id']}")
    assert check.status_code == 404


def test_delet_task_not_found(auth_client):
    "Удаление несуществующей таски -> 404"

    response =  auth_client.delete("/tasks/666")
    assert response.status_code == 404



# --- search task ---

def test_search_in_title_and_descriptions(auth_client):
    _create_task(auth_client, title="купить молочко", description="")
    _create_task(auth_client, title="таска2", description="ойойой")
    _create_task(auth_client, title="таска3", description="пупупу")

    r1 = auth_client.get("/tasks/search?query=МОЛОЧКО")
    assert r1.status_code == 200
    assert len(r1.json()) == 1

    r2 = auth_client.get("/tasks/search?query=ой")
    assert len(r2.json()) == 1


# --- tasks/top ---

def test_top_returns_sorted_and_uses_cache(auth_client):
    _create_task(auth_client, title="p1", priority=1)
    _create_task(auth_client, title="p5", priority=5)
    _create_task(auth_client, title="p3", priority=3)

    r1 = auth_client.get("/tasks/top?n=2")
    assert r1.status_code == 200

    titles = [t['title'] for t in r1.json()]
    assert titles == ["p5", "p3"]

    r2 = auth_client.get("/tasks/top?n=2")
    assert r2.json() == r1.json()


def test_list_tasks_invalid_sort_field_returns_400(auth_client):
    response = auth_client.get("/tasks/?sort_by=password")
    assert response.status_code == 400
