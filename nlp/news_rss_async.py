
import aiohttp
import asyncio
import async_timeout
import datetime as dt
import functools
import os

RSS_FEEDS = {
    "moex_issuer": "https://www.moex.com/export/news.aspx?news=issuer&lang=ru",
    "interfax"   : "https://www.finmarket.ru/xml/news.xml",
    "tass"       : "https://tass.ru/rss/v2.xml",
    "rbc"        : "https://rssexport.rbc.ru/rbcnews/news/finance.rss",
    "kommersant" : "https://www.kommersant.ru/RSS/main.xml",
    "lenta"      : "https://lenta.ru/rss/finances",
}

_TIMEOUT = int(os.getenv("RSS_TIMEOUT", "6"))

async def _fetch(url):
    try:
        async with aiohttp.ClientSession() as sess:
            async with async_timeout.timeout(_TIMEOUT):
                async with sess.get(url) as r:
                    return await r.text()
    except Exception:
        return None

async def async_fetch_all(hours: int = 24):
    cutoff = dt.datetime.utcnow() - dt.timedelta(hours=hours)
    tasks  = [_fetch(u) for u in RSS_FEEDS.values()]
    return await asyncio.gather(*tasks, return_exceptions=True)
