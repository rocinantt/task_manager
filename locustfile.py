from uuid import uuid4
from random import randint, choice

from locust import HttpUser, task, between


class TaskManagerUser(HttpUser):
    """
    Сценарий пользователя:
    - Регистрируется
    - Логинится
    - Создает задачи
    - Читает список задач
    -  повторные запросы к /tasks/top?n=5 для проверки кэша
    """

    wait_time = between(0.1, 0.5)

    def on_start(self):
        "Создает пользователя и получает токен"

        self.username = f'user_{uuid4().hex}'
        self.password = 'test_password'

        register_response = self.client.post(
            "/users/register",
            json={
                "username": self.username,
                "password": self.password
            },
            name="POST /users/register"
        )

        # Проверка на успешность регистрации
        if register_response.status_code not in (200, 201):
            register_response.failure(
                f"register failed: {register_response.status_code} {register_response.text}"
            )
            return
        
        login_response = self.client.post(
            "/users/login",
            data={
                "username": self.username,
                "password": self.password,
            },
            name="POST /users/login",
        )

        # Проверка на успешность авторизации
        if login_response.status_code not in (200, 201):
            login_response.failure(
                f"register failed: {login_response.status_code} {login_response.text}"
            )
            return
        
        token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {token}"}

        # Создаем стартовые задачи
        for i in range(5):
            self.client.post(
                "/tasks/",
                json={
                    "title": f"Initial task {i}",
                    "description": "Initial description",
                    "status": "в ожидании",
                    "priority": randint(1, 5),
                },
                headers=self.headers,
                name="POST /tasks/ setup",
            )

        
    @task(3)
    def create_task(self):
        "Массовое создание задач"
        task_id = uuid4().hex[:8]

        response = self.client.post(
            "/tasks/",
            json={
                "title": f"Load task {task_id}",
                "description": "Created by Locust test",
                "status": choice(["в ожидании", "в работе", "завершено"]),
                "priority": randint(1, 5),
            },
            headers=self.headers,
            name="POST /tasks/",
        )


    @task(2)
    def list_tasks(self):
        "Получение списка задач"
        response = self.client.get(
            "/tasks/",
            headers=self.headers,
            name="GET /tasks/",
        )

        if response.status_code != 200:
            response.failure(
                f"list tasks failed: {response.status_code} {response.text}"
            )


    @task(8)
    def get_top_tasks_cached(self):
        """
        Один и тот же пользователь много раз вызывает /tasks/top?n=5.
        После первого запроса результат должен браться из _top_cache
        """
        response = self.client.get(
            "/tasks/top?n=5",
            headers=self.headers,
            name="GET /tasks/top cached n=5",
        )

        if response.status_code != 200:
            response.failure(
                f"top cached failed: {response.status_code} {response.text}"
            )

    

