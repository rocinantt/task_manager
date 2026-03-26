from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Task, User
from schemas import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# кэш для топ-N запросов: ключ (user_id, n) -> список задач
_top_cache: dict[tuple[int, int], list] = {}


def _clear_cache(user_id: int):
    """Сбрасывает кэш при изменении задач пользователя."""
    keys_to_delete = [key for key in _top_cache if key[0] == user_id]
    for key in keys_to_delete:
        del _top_cache[key]


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Создать новую задачу."""
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        owner_id=current_user.id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    _clear_cache(current_user.id)
    return new_task


@router.get("/", response_model=list[TaskResponse])
def get_tasks(
    sort_by: str = Query("created_at", description="Поле для сортировки: title, status, priority, created_at"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить все задачи текущего пользователя с сортировкой."""

    # проверяем, что поле для сортировки допустимо
    allowed_fields = {"title", "status", "priority", "created_at"}
    if sort_by not in allowed_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Сортировка по '{sort_by}' не поддерживается. Допустимые поля: {allowed_fields}",
        )

    # получаем колонку модели по имени
    sort_column = getattr(Task, sort_by)

    tasks = (
        db.query(Task)
        .filter(Task.owner_id == current_user.id)
        .order_by(sort_column)
        .all()
    )
    return tasks


@router.get("/search", response_model=list[TaskResponse])
def search_tasks(
    query: str = Query(..., description="Строка для поиска в заголовке и описании"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Поиск задач по вхождению подстроки в заголовок или описание."""
    query_lower = query.lower()

    # получаем все задачи пользователя и фильтруем в Python 
    all_tasks = db.query(Task).filter(Task.owner_id == current_user.id).all()

    results = []
    for task in all_tasks:
        if query_lower in task.title.lower() or query_lower in task.description.lower():
            results.append(task)

    return results


@router.get("/top", response_model=list[TaskResponse])
def get_top_tasks(
    n: int = Query(5, ge=1, description="Количество самых приоритетных задач"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить топ-N задач с наивысшим приоритетом"""

    cache_key = (current_user.id, n)

    # если есть в кэше - возвращаем сразу
    if cache_key in _top_cache:
        return _top_cache[cache_key]

    # иначе - запрос к БД
    tasks = (
        db.query(Task)
        .filter(Task.owner_id == current_user.id)
        .order_by(Task.priority.desc())
        .limit(n)
        .all()
    )

    _top_cache[cache_key] = tasks
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить одну задачу по ID."""
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Обновить задачу (частично или полностью)."""
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

    # обновляем только те поля, которые переданы
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    _clear_cache(current_user.id)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Удалить задачу."""
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

    db.delete(task)
    db.commit()
    _clear_cache(current_user.id)
