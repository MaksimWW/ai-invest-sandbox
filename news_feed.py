
"""Modified news_feed.py to disable GDELT functionality based on user request."""
import requests
import datetime as dt
import os
from health.metrics import record

# Переменная для отключения GDELT (по умолчанию отключен)
GDELT_ENABLED = os.getenv("GDELT_ENABLED", "0") == "1"

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

def _newsapi_query(q, from_dt):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q"      : q,
        "language": "en",
        "sortBy" : "publishedAt",
        "from"   : from_dt.isoformat(timespec="seconds"),
        "apiKey" : NEWSAPI_KEY,
        "pageSize": 100,
    }
    r = requests.get(url, params=params, timeout=6)
    r.raise_for_status()
    resp = r.json()
    retrieved = len(resp.get("articles", []))
    record("newsapi_call", {
        "ticker": q,
        "articles": retrieved
    })
    return [a["title"] for a in resp.get("articles", [])]

def _gdelt_query(q, from_dt):
    """GDELT функция отключена - возвращает пустой список"""
    print("⚠️ GDELT отключен (используйте GDELT_ENABLED=1 для включения)")
    return []

def fetch_news(ticker: str, hours: int = 24) -> list[str]:
    """Получить новости по тикеру из NewsAPI (GDELT отключен)"""
    cutoff = dt.datetime.utcnow() - dt.timedelta(hours=hours)
    news = []

    # NewsAPI
    if NEWSAPI_KEY:
        print(f"📰 Запрашиваем NewsAPI для {ticker}...")
        try:
            newsapi_results = _newsapi_query(ticker, cutoff)
            news += newsapi_results
            print(f"✅ NewsAPI: найдено {len(newsapi_results)} новостей")
        except Exception as e:
            print(f"❌ NewsAPI ошибка: {e}")
            newsapi_results = []
    else:
        print("⚠️ NewsAPI не настроен (нет NEWSAPI_KEY)")
        newsapi_results = []

    # GDELT - отключен
    gdelt_results = []
    if GDELT_ENABLED:
        print(f"🌐 Запрашиваем GDELT для {ticker}...")
        gdelt_results = _gdelt_query(ticker, cutoff)
        news += gdelt_results
        print(f"✅ GDELT: найдено {len(gdelt_results)} новостей")
    else:
        print("⚠️ GDELT отключен (используйте GDELT_ENABLED=1 для включения)")

    print(f"📊 Итого для {ticker}: {len(news)} новостей (NewsAPI: {len(newsapi_results)}, GDELT: {len(gdelt_results)})")
    return news
