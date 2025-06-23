import pytest
from importlib import import_module

try:
    latest_fn = getattr(import_module("nlp.sentiment"), "fetch_ru_news")
except Exception:
    latest_fn = None

# --- если функции нет → пропускаем весь файл
if latest_fn is None or not callable(latest_fn):
    pytest.skip("fetch_ru_news not available", allow_module_level=True)

def test_fetch_ru_news_returns_list():
    """Функция должна вернуть список строк (может быть пустым)."""
    headlines = latest_fn(hours=1)          # ≤ 1 ч, чтобы быстро
    assert isinstance(headlines, list)
    assert all(isinstance(h, str) for h in headlines), "все элементы – строки"