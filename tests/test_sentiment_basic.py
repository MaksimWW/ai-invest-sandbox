
from nlp.sentiment import fetch_ru_news

def test_fetch_ru_nonerror():
    """fetch_ru_news должен всегда возвращать list (возможно пустой)."""
    headlines = fetch_ru_news(1)
    assert isinstance(headlines, list)
