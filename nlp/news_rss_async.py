
import aiohttp
import async_timeout
import asyncio
import gzip
import os
import time
import datetime as dt
import functools

RSS_FEEDS = {
    "moex_issuer": "https://www.moex.com/export/news.aspx?news=issuer&lang=ru",
    "interfax"   : "https://www.finmarket.ru/xml/news.xml",
    "tass"       : "https://tass.ru/rss/v2.xml",
    "rbc"        : "https://rssexport.rbc.ru/rbcnews/news/finance.rss",
    "kommersant" : "https://www.kommersant.ru/RSS/main.xml",
    "lenta"      : "https://lenta.ru/rss/finances",
}

BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/125.0 Safari/537.36")

def _timeout_for(url: str) -> int:
    if "moex.com/export/news" in url:
        return 15          # тяжёлый XML
    return int(os.getenv("RSS_TIMEOUT", "6"))

async def _single_try(url: str, timeout: int):
    hdrs = {"User-Agent": BROWSER_UA,
            "Accept-Encoding": "gzip, deflate"}
    async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=timeout)) as sess:
        async with async_timeout.timeout(timeout + 2):
            async with sess.get(url, headers=hdrs, ssl=False) as r:
                raw = await r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
                return raw.decode(r.charset or "utf-8", "ignore")

async def _fetch(url: str):
    timeout = _timeout_for(url)
    url_variant = url
    for attempt in (1, 2, 3):
        try:
            return await _single_try(url_variant, timeout)
        except Exception:
            # first fail on Interfax https → retry http
            if attempt == 1 and "finmarket.ru" in url_variant and url_variant.startswith("https"):
                url_variant = url_variant.replace("https://", "http://")
            else:
                await asyncio.sleep(2 ** attempt)   # 2s, 4s
    return None

async def async_fetch_all(hours: int = 24):
    cutoff = dt.datetime.utcnow() - dt.timedelta(hours=hours)
    tasks  = [_fetch(u) for u in RSS_FEEDS.values()]
    return await asyncio.gather(*tasks, return_exceptions=True)
