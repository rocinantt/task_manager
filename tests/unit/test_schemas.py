import pytest
from pydantic import ValidationError

from schemas import TaskCreate, TaskUpdate, TaskStatus


def test_task_create_with_minimal_fields():
    # Создание задачи только с передачей только  обязательного  поля
    task =  TaskCreate(title="test")
    assert task.priority  == 1
    assert task.status == TaskStatus.pending
    assert task.description == ""


@pytest.mark.parametrize("priority", [1, 2, 3, 4, 5])
def test_task_create_accepts_valid_priority(priority):
    # Проверка корректности создания задачи с валидным уровнем приоритета (1-5)
    task = TaskCreate(title="test", priority=priority)

    assert task.priority ==  priority


@pytest.mark.parametrize("priority", [0, -1, 6, 100])
def test_task_create_rejects_invalid_priority(priority):
    # Проверка некорректности создания задачи с невалидным уровнем приоритета 
    with pytest.raises(ValidationError):
        TaskCreate(title="test", priority=priority)


def test_task_create_rejects_invalid_status():
    # Проверка некорректности создания с невалидными статусом
    with pytest.raises(ValidationError):
        TaskCreate(title="test", status="wrong")


def test_task_update_partial():
    # Если  пользователь передал только 1  поле - обновится только оно
    update = TaskUpdate(title="new_title")
    dumped = update.model_dump(exclude_unset=True)

    assert dumped == {"title": "new_title"}

def test_task_update_empty():
    # Если  пользователь ничего не передал - ничего не обновится
    update =   TaskUpdate()
    dumped = update.model_dump(exclude_unset=True)

    assert dumped == {}