import requests
import time
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import feedparser
import logging

if os.getenv("GDELT_OFF", "0") != "1":
    def _gdelt_query(query: str, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Запрашивает GDELT API для получения статей по запросу.

        Args:
            query (str): Поисковый запрос.
            hours (int, optional): Количество часов для поиска. Defaults to 24.

        Returns:
            List[Dict[str, Any]]: Список статей, полученных из GDELT API.
        """
        endpoint_name = "GDELT"
        try:
            # GDELT API URL
            url = "https://api.gdeltproject.org/api/v2/doc/doc"

            # Формируем параметры запроса
            params = {
                "query": query,
                "mode": "timelinevol",
                "format": "json",
                "timespan": hours,
                "maxrecords": 250,
            }

            # Выполняем запрос к API
            response = requests.get(url, params=params)
            response.raise_for_status()  # Проверка на ошибки HTTP

            data = response.json()

            articles = []
            if 'timeline' in data:
                for entry in data['timeline']:
                    if 'date' in entry and 'volume' in entry:
                        date = datetime.strptime(entry['date'], '%Y%m%d%H%M%S')
                        volume = entry['volume']
                        articles.append({
                            "title": f"Volume: {volume}",
                            "link": f"https://gdeltproject.org/",
                            "summary": f"Volume of articles on {date.isoformat()}: {volume}",
                            "published": date.isoformat(),
                            "source": "GDELT"
                        })

            return articles

        except Exception as e:
            print(f"❌ {endpoint_name} ошибка: {type(e).__name__}: {e}")
            return []
else:
    def _gdelt_query(*args, **kwargs):
        return []

def fetch_news(query: str, hours: int = 24) -> List[Dict[str, Any]]:
    """
    Получает новости из разных источников.

    Args:
        query (str): Поисковый запрос.
        hours (int, optional): Количество часов для поиска. Defaults to 24.

    Returns:
        List[Dict[str, Any]]: Список новостей.
    """
    news: List[Dict[str, Any]] = []

    # 1. NewsAPI
    try:
        newsapi_articles = _newsapi_query(query, hours)
        print(f"   📰 NewsAPI: {len(newsapi_articles)} статей")
        news.extend(newsapi_articles)
    except Exception as e:
        print(f"   ❌ NewsAPI ошибка: {e}")

    # 2. RSS Feeds
    try:
        rss_articles = _rss_query(query)
        print(f"   🔗 RSS: {len(rss_articles)} статей")
        news.extend(rss_articles)
    except Exception as e:
        print(f"   ❌ RSS ошибка: {e}")

    # 3. GDELT API (глобальные новости с анализом тональности)
    # NOTE: GDELT отключён, включить → убрать ENV GDELT_OFF
    if os.getenv("GDELT_OFF", "0") == "1":
        print("   🔧 GDELT отключён (GDELT_OFF=1)")
    else:
        try:
            gdelt_articles = _gdelt_query(query, hours)
            print(f"   📡 GDELT: {len(gdelt_articles)} статей")
            news.extend(gdelt_articles)
        except Exception as e:
            print(f"   ❌ GDELT ошибка: {e}")

    return news

def _newsapi_query(query: str, hours: int = 24) -> List[Dict[str, Any]]:
    """
    Выполняет запрос к NewsAPI для получения статей.

    Args:
        query (str): Поисковый запрос.
        hours (int): Количество часов для поиска.

    Returns:
        List[Dict[str, Any]]: Список статей, полученных из NewsAPI.
    """
    endpoint_name = "NewsAPI"
    try:
        NEWSAPI_API_KEY = os.getenv("NEWSAPI_API_KEY")
        if not NEWSAPI_API_KEY:
            raise ValueError("NewsAPI API key is not set in environment variables.")

        url = "https://newsapi.org/v2/everything"
        now = datetime.utcnow()
        time_threshold = now - timedelta(hours=hours)
        formatted_time = time_threshold.isoformat()[:-3] + 'Z'

        params = {
            "q": query,
            "from": formatted_time,
            "sortBy": "relevancy",
            "apiKey": NEWSAPI_API_KEY,
            "language": "ru",
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        articles = []
        if data["status"] == "ok":
            for article in data["articles"]:
                articles.append({
                    "title": article["title"],
                    "link": article["url"],
                    "summary": article["description"],
                    "published": article["publishedAt"],
                    "source": article["source"]["name"],
                })
        return articles

    except Exception as e:
        print(f"❌ {endpoint_name} ошибка: {type(e).__name__}: {e}")
        return []


def _rss_query(query: str) -> List[Dict[str, Any]]:
    """
    Выполняет запросы к RSS-лентам для получения статей.

    Args:
        query (str): Поисковый запрос.

    Returns:
        List[Dict[str, Any]]: Список статей, полученных из RSS-лент.
    """
    endpoint_name = "RSS"
    try:
        RSS_FEED_URLS = [
            "https://lenta.ru/rss/news",
            "https://www.vesti.ru/vesti.rss",
            "https://www.interfax.ru/rss.asp",
        ]

        articles = []
        for url in RSS_FEED_URLS:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if query.lower() in entry.title.lower() or query.lower() in entry.summary.lower():
                    articles.append({
                        "title": entry.title,
                        "link": entry.link,
                        "summary": entry.summary,
                        "published": entry.published,
                        "source": url,
                    })
        return articles

    except Exception as e:
        print(f"❌ {endpoint_name} ошибка: {type(e).__name__}: {e}")
        return []