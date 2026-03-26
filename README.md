# Task Manager API

Управление списком задач на FastAPI + SQLAlchemy + SQLite.

## Запуск

```bash
uv sync
uv run uvicorn main:app --reload
```

Swagger: http://127.0.0.1:8000/docs

Чтобы авторизоваться в Swagger - нажать кнопку "Authorize" вверху, ввести username и password.

## Эндпоинты

### Пользователи

- `POST /users/register` - регистрация (JSON: username, password)
- `POST /users/login` - логин через OAuth2-форму, возвращает JWT-токен

### Задачи (все требуют токен)

- `POST /tasks/` - создать задачу
- `GET /tasks/?sort_by=priority` - список задач с сортировкой (title, status, priority, created_at)
- `GET /tasks/search?query=python` - поиск по подстроке в заголовке/описании
- `GET /tasks/top?n=5` - топ-N по приоритету
- `GET /tasks/{id}` - одна задача
- `PUT /tasks/{id}` - обновить (можно передать только нужные поля)
- `DELETE /tasks/{id}` - удалить

## Валидация

- Статус задачи: только "в ожидании", "в работе", "завершено" (enum)
- Приоритет: целое число от 1 до 5
- Каждый пользователь видит и редактирует только свои задачи

## Кэширование

Кэшируется `GET /tasks/top` - этот запрос включает сортировку + LIMIT,
вызывается часто с одними и теми же параметрами, а данные меняются реже чем читаются.

Реализация: словарь в памяти, ключ `(user_id, n)`.
Сбрасывается при создании, обновлении или удалении задачи.

Ограничения: не переживает рестарт, не разделяется между процессами.

## Структура

```
main.py       - точка входа, lifespan
database.py   - подключение к SQLite через SQLAlchemy
models.py     - модели User и Task
schemas.py    - Pydantic-схемы с валидацией
auth.py       - JWT-токены, хеширование паролей
routers/
  users.py    - регистрация и логин
  tasks.py    - CRUD, сортировка, поиск, топ-N
```