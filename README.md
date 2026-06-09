# Task Manager - FastAPI + MySQL в Docker

Веб-сервис для управления задачами на FastAPI. Приложение и база данных MySQL
работают в отдельных Docker-контейнерах, связаны через общую сеть, данные базы
сохраняются в Docker volume. Поддерживается режим Docker Swarm с автоперезапуском.

## Требования
- Установленный Docker и Docker Compose
- Свободный порт 8000

## Возможности
- Регистрация и авторизация пользователей (JWT)
- CRUD задач: создание, чтение, обновление, удаление
- Поиск и сортировка задач
- Каждый пользователь работает только со своими задачами

## Структура проекта
- `main.py` - точка входа FastAPI, инициализация БД
- `database.py` - подключение к БД 
- `models.py` - модели таблиц
- `schemas.py` - схемы валидации
- `auth.py` - хеширование паролей и JWT
- `routers/` - эндпоинты
- `Dockerfile` - сборка образа веб-сервиса
- `docker-compose.yml` - запуск web + MySQL
- `docker-stack.yml` - конфигурация для Docker Swarm
- `.env` - переменные окружения

## Настройка

Создайте файл `.env` в корне проекта (или скопируйте `.env.example`):

```
MYSQL_ROOT_PASSWORD=rootpass
MYSQL_DATABASE=task_manager
MYSQL_USER=taskuser
MYSQL_PASSWORD=taskpass
SECRET_KEY=simsimept
```

## Запуск через Docker Compose

```bash
docker compose up --build
```

Команда соберет образ приложения и поднимет два контейнера: `db` (MySQL) и `web`.
Приложение дождтся готовности базы и создаст таблицы.

После старта доступны:
- Веб-интерфейс: http://localhost:8000/
- Документация API (Swagger): http://localhost:8000/docs
- Проверка состояния: http://localhost:8000/health

## Запуск в режиме Docker Swarm

```bash
# 1. Инициализировать Swarm
docker swarm init

# 2. Собрать образ веб-сервиса
docker build -t task-manager-web:latest .

# 3. Развернуть стьек
docker stack deploy -c docker-stack.yml taskmgr

# 4. Проверить сервисы (должно быть 1/1)
docker stack services taskmgr
```

## Хранение данных
Данные MySQL хранятся в Docker volume `db_data`, поэтому сохраняются при
перезапуске и пересоздании контейнера базы. Полностью удалить данные:
`docker compose down -v`.


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
