import pytest
from routers.tasks import _top_cache

@pytest.fixture(autouse=True)
def clear_top_cache():
    """Перед каждым тестом  чистим кэш"""

    _top_cache.clear()
    yield
    _top_cache.clear()