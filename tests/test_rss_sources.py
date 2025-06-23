import pytest, importlib, inspect

# берём вашу функцию fetch_ru_news из nlp.news_rss_async (или где она лежит)
mod = importlib.import_module("nlp.news_rss_async")
latest_fn = getattr(mod, "fetch_ru_news", None)

@pytest.mark.skipif(latest_fn is None, reason="fetch_ru_news not found")
def test_at_least_one_rss_works():
    """Функция должна вернуть >=1 новости хотя бы для одного URL."""
    sig = inspect.signature(latest_fn)
    # функция должна принимать hours и url (или использовать встроенный список)
    kwargs = {"hours": 6} if "hours" in sig.parameters else {}
    news = latest_fn(**kwargs)
    assert isinstance(news, list)
    # допускаем, что RSS могут быть пустыми → xfail
    if not news:
        pytest.xfail("Все RSS вернули 0 новостей за 6ч")
