
from functools import lru_cache
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch, requests, datetime as dt
from news_feed import fetch_news
from langdetect import detect

# Русская модель
RU_MODEL_NAME = "sismetanin/rubert-rusentiment"
RU_LABELS = ["negative", "neutral", "positive"]

# Английская модель (FinBERT для финансовых новостей)
EN_MODEL_NAME = "ProsusAI/finbert"
EN_LABELS = ["negative", "neutral", "positive"]

@lru_cache(maxsize=2)
def _load_models():
    # Русская модель
    ru_tok = AutoTokenizer.from_pretrained(RU_MODEL_NAME)
    ru_mdl = AutoModelForSequenceClassification.from_pretrained(RU_MODEL_NAME)
    ru_mdl.eval()
    
    # Английская модель
    en_tok = AutoTokenizer.from_pretrained(EN_MODEL_NAME)
    en_mdl = AutoModelForSequenceClassification.from_pretrained(EN_MODEL_NAME)
    en_mdl.eval()
    
    return ru_tok, ru_mdl, en_tok, en_mdl

def classify_ru(text: str) -> str:
    """Анализ настроения русского текста"""
    ru_tok, ru_mdl, _, _ = _load_models()
    inputs = ru_tok(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = ru_mdl(**inputs).logits
    return RU_LABELS[logits.argmax().item()]

def classify_en(text: str) -> str:
    """Анализ настроения английского текста"""
    _, _, en_tok, en_mdl = _load_models()
    inputs = en_tok(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = en_mdl(**inputs).logits
    return EN_LABELS[logits.argmax().item()]

def classify_multi(text: str) -> str:
    """Мультиязычный анализ настроения"""
    try:
        lang = detect(text[:200])
        if lang == "ru":
            return classify_ru(text)
        else:
            return classify_en(text)
    except Exception:
        # Если язык не определился, пробуем английский
        return classify_en(text)

# Старая функция для совместимости
def classify(text: str) -> str:
    """Обратная совместимость - анализ русского текста"""
    return classify_ru(text)

# --- RSS-граббер с несколькими источниками ---
RSS_FEEDS = [
    "https://tass.ru/rss/v2.xml",
    "https://rssexport.rbc.ru/rbcnews/news/30/full.rss",
]

def latest_news_ru(ticker: str, hours: int = 24) -> list[str]:
    """Получение русских новостей из RSS"""
    cutoff = dt.datetime.utcnow() - dt.timedelta(hours=hours)
    found = []
    for url in RSS_FEEDS:
        try:
            xml = requests.get(url, timeout=5).text
            for it in xml.split("<item>")[1:]:
                title = it.split("<title>")[1].split("</title>")[0]
                pub   = it.split("<pubDate>")[1].split("</pubDate>")[0]
                dt_pub = dt.datetime.strptime(pub[:-6], "%a, %d %b %Y %H:%M:%S")
                if dt_pub > cutoff and ticker.lower() in title.lower():
                    found.append(title)
        except Exception as e:
            print(f"⚠️ Ошибка обработки RSS {url}: {e}")
            continue
    return found

# Для обратной совместимости
def latest_news(ticker: str, hours: int = 24) -> list[str]:
    """Обратная совместимость - русские новости"""
    return latest_news_ru(ticker, hours)
