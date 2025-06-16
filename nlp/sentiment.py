
from functools import lru_cache
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch, requests, datetime as dt
from news_feed import fetch_news
from langdetect import detect

# Используем рабочие модели
RU_MODEL_NAME = "blanchefort/rubert-base-cased-sentiment"
RU_LABELS = ["NEUTRAL", "POSITIVE", "NEGATIVE"]

# Английская модель для финансовых новостей
EN_MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
EN_LABELS = ["LABEL_0", "LABEL_1", "LABEL_2"]  # negative, neutral, positive

@lru_cache(maxsize=2)
def _load_models():
    """Загружает модели с обработкой ошибок"""
    try:
        # Русская модель
        print("🔄 Загружаем русскую модель...")
        ru_tok = AutoTokenizer.from_pretrained(RU_MODEL_NAME)
        ru_mdl = AutoModelForSequenceClassification.from_pretrained(RU_MODEL_NAME)
        ru_mdl.eval()
        print("✅ Русская модель загружена")
    except Exception as e:
        print(f"❌ Ошибка загрузки русской модели: {e}")
        ru_tok, ru_mdl = None, None

    try:
        # Английская модель
        print("🔄 Загружаем английскую модель...")
        en_tok = AutoTokenizer.from_pretrained(EN_MODEL_NAME)
        en_mdl = AutoModelForSequenceClassification.from_pretrained(EN_MODEL_NAME)
        en_mdl.eval()
        print("✅ Английская модель загружена")
    except Exception as e:
        print(f"❌ Ошибка загрузки английской модели: {e}")
        en_tok, en_mdl = None, None

    return ru_tok, ru_mdl, en_tok, en_mdl

def _normalize_sentiment(label: str, model_type: str = "ru") -> str:
    """Нормализует метки настроения к единому формату"""
    if model_type == "ru":
        # Для русской модели
        mapping = {
            "NEGATIVE": "negative",
            "NEUTRAL": "neutral", 
            "POSITIVE": "positive"
        }
        return mapping.get(label, "neutral")
    else:
        # Для английской модели (Twitter RoBERTa)
        mapping = {
            "LABEL_0": "negative",  # negative
            "LABEL_1": "neutral",   # neutral
            "LABEL_2": "positive"   # positive
        }
        return mapping.get(label, "neutral")

def classify_ru(text: str) -> str:
    """Анализ настроения русского текста"""
    try:
        ru_tok, ru_mdl, _, _ = _load_models()
        if ru_tok is None or ru_mdl is None:
            return "neutral"
        
        inputs = ru_tok(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            logits = ru_mdl(**inputs).logits
        
        predicted_label = RU_LABELS[logits.argmax().item()]
        return _normalize_sentiment(predicted_label, "ru")
    except Exception as e:
        print(f"⚠️ Ошибка анализа русского текста: {e}")
        return "neutral"

def classify_en(text: str) -> str:
    """Анализ настроения английского текста"""
    try:
        _, _, en_tok, en_mdl = _load_models()
        if en_tok is None or en_mdl is None:
            return "neutral"
        
        inputs = en_tok(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            logits = en_mdl(**inputs).logits
        
        predicted_label = EN_LABELS[logits.argmax().item()]
        return _normalize_sentiment(predicted_label, "en")
    except Exception as e:
        print(f"⚠️ Ошибка анализа английского текста: {e}")
        return "neutral"

def classify_multi(text: str) -> str:
    """Мультиязычный анализ настроения"""
    try:
        # Определяем язык
        lang = detect(text[:200])
        if lang == "ru":
            return classify_ru(text)
        else:
            return classify_en(text)
    except Exception as e:
        print(f"⚠️ Ошибка определения языка: {e}")
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
