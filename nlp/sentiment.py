
from functools import lru_cache
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch, requests, datetime as dt
from news_feed import fetch_news
from langdetect import detect
import warnings

# Подавляем предупреждения о неиспользуемых весах модели
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")

# Модели для русского языка (в порядке предпочтения)
RU_MODELS = [
    {
        "name": "seara/rubert-base-cased-russian-sentiment",
        "labels": ["NEGATIVE", "NEUTRAL", "POSITIVE"]
    },
    {
        "name": "sismetanin/rubert-ru-sentiment-rusentiment",
        "labels": ["NEGATIVE", "NEUTRAL", "POSITIVE"]
    },
    {
        "name": "blanchefort/rubert-base-cased-sentiment",
        "labels": ["NEUTRAL", "POSITIVE", "NEGATIVE"]
    }
]

# Английская модель для финансовых новостей
EN_MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
EN_LABELS = ["LABEL_0", "LABEL_1", "LABEL_2"]  # negative, neutral, positive

@lru_cache(maxsize=2)
def _load_models():
    """Загружает модели с обработкой ошибок и резервными вариантами"""
    ru_tok, ru_mdl, ru_labels = None, None, None
    
    # Пробуем русские модели по очереди
    for model_info in RU_MODELS:
        try:
            print(f"🔄 Пробуем русскую модель: {model_info['name']}")
            ru_tok = AutoTokenizer.from_pretrained(model_info["name"])
            ru_mdl = AutoModelForSequenceClassification.from_pretrained(model_info["name"])
            ru_mdl.eval()
            ru_labels = model_info["labels"]
            print(f"✅ Русская модель загружена: {model_info['name']}")
            break
        except Exception as e:
            print(f"⚠️ Ошибка загрузки {model_info['name']}: {e}")
            continue
    
    if ru_tok is None:
        print("❌ Не удалось загрузить ни одну русскую модель")

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

    return ru_tok, ru_mdl, ru_labels, en_tok, en_mdl

def _normalize_sentiment(label: str, model_type: str = "ru") -> str:
    """Нормализует метки настроения к единому формату"""
    if model_type == "ru":
        # Для русских моделей
        label_upper = label.upper()
        if "NEGATIVE" in label_upper or "NEG" in label_upper:
            return "negative"
        elif "POSITIVE" in label_upper or "POS" in label_upper:
            return "positive"
        else:
            return "neutral"
    else:
        # Для английской модели (Twitter RoBERTa)
        mapping = {
            "LABEL_0": "negative",  # negative
            "LABEL_1": "neutral",   # neutral
            "LABEL_2": "positive"   # positive
        }
        return mapping.get(label, "neutral")

def _rule_based_sentiment_ru(text: str) -> str:
    """Простой rule-based анализ как резервный вариант"""
    text_lower = text.lower()
    
    positive_words = [
        "рост", "прибыль", "успех", "хорошо", "отлично", "рекорд", "выигр", 
        "плюс", "повыш", "увелич", "улучш", "позитив", "выгод", "доход"
    ]
    
    negative_words = [
        "падение", "убыток", "кризис", "плохо", "ужасно", "провал", "проигр",
        "минус", "снизил", "уменьш", "ухудш", "негатив", "потер", "долг"
    ]
    
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    else:
        return "neutral"

def classify_ru(text: str) -> str:
    """Анализ настроения русского текста с резервными методами"""
    try:
        ru_tok, ru_mdl, ru_labels, _, _ = _load_models()
        
        # Если модель загружена, используем её
        if ru_tok is not None and ru_mdl is not None:
            inputs = ru_tok(text, return_tensors="pt", truncation=True, max_length=512)
            with torch.no_grad():
                logits = ru_mdl(**inputs).logits
            
            probabilities = torch.softmax(logits, dim=-1)
            predicted_idx = logits.argmax().item()
            predicted_label = ru_labels[predicted_idx]
            confidence = probabilities[0][predicted_idx].item()
            
            print(f"🔍 RU MODEL: '{text[:50]}...'")
            print(f"📊 Вероятности: {[f'{ru_labels[i]}={probabilities[0][i]:.3f}' for i in range(len(ru_labels))]}")
            print(f"🎯 Предсказание: {predicted_label} (уверенность: {confidence:.3f})")
            
            result = _normalize_sentiment(predicted_label, "ru")
            
            # Если уверенность низкая, используем rule-based
            if confidence < 0.7:
                rule_result = _rule_based_sentiment_ru(text)
                print(f"⚡ Rule-based результат: {rule_result}")
                if rule_result != "neutral":
                    result = rule_result
                    print(f"🔄 Используем rule-based результат")
            
            print(f"✅ Финальный результат: {result}")
            return result
        
        # Если модель не загружена, используем rule-based
        else:
            print(f"🔄 Используем rule-based анализ для: '{text[:50]}...'")
            result = _rule_based_sentiment_ru(text)
            print(f"✅ Rule-based результат: {result}")
            return result
            
    except Exception as e:
        print(f"⚠️ Ошибка анализа русского текста: {e}")
        # Резервный rule-based анализ
        return _rule_based_sentiment_ru(text)

def classify_en(text: str) -> str:
    """Анализ настроения английского текста"""
    try:
        _, _, _, en_tok, en_mdl = _load_models()
        if en_tok is None or en_mdl is None:
            return "neutral"
        
        inputs = en_tok(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            logits = en_mdl(**inputs).logits
        
        probabilities = torch.softmax(logits, dim=-1)
        predicted_idx = logits.argmax().item()
        predicted_label = EN_LABELS[predicted_idx]
        confidence = probabilities[0][predicted_idx].item()
        
        print(f"🔍 EN DEBUG: '{text[:50]}...'")
        print(f"📊 Вероятности: {[f'{EN_LABELS[i]}={probabilities[0][i]:.3f}' for i in range(len(EN_LABELS))]}")
        print(f"🎯 Предсказание: {predicted_label} (уверенность: {confidence:.3f})")
        
        result = _normalize_sentiment(predicted_label, "en")
        print(f"✅ Финальный результат: {result}")
        return result
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
