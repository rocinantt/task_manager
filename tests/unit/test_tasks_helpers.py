from routers.tasks import _clear_cache, _top_cache


def test_clear_cache_removes_only_target_user():
    # Проверяем что кэш сбрасывается  только у выбранного  пользователя 

    _top_cache[(1, 5)] = ["task_a"]
    _top_cache[(1, 10)] = ["task_b"]
    _top_cache[(2, 5)] = ["task_c"]

    _clear_cache(user_id=1)

    assert (1,  5) not in  _top_cache
    assert (1, 10) not in _top_cache
    assert (2, 5) in _top_cache

def test_clear_cache_on_empty_cache_does_not_raise():
    # Очистка пустого кэша не приводит  к ошибке
    _clear_cache(user_id=999)

    assert _top_cache == {}


def test_clear_cache_when_user_has_no_entries():
    # При сбросе кэша  несуществующего пользователя чужие данные сохраняются
    _top_cache[(1, 5)] = ["test"]

    _clear_cache(user_id=123)

    assert (1, 5) in _top_cache