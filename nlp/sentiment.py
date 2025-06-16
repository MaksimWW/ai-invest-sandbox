
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
    """Улучшенный rule-based анализ с весами"""
    text_lower = text.lower()
    
    # Сильные позитивные индикаторы (вес 2)
    strong_positive = ["выросли", "рост", "прибыль", "рекорд", "breakthrough", "скачок", "взлет", "бум"]
    # Обычные позитивные (вес 1)
    positive_words = [
        "успех", "хорошо", "отлично", "выигр", "плюс", "повыш", "увелич", 
        "улучш", "позитив", "выгод", "доход", "превосход", "достиж"
    ]
    
    # Сильные негативные индикаторы (вес 2)
    strong_negative = ["упали", "падение", "убыток", "кризис", "обвал", "крах", "коллапс"]
    # Обычные негативные (вес 1)
    negative_words = [
        "плохо", "ужасно", "провал", "проигр", "минус", "снизил", "уменьш", 
        "ухудш", "негатив", "потер", "долг", "катастроф", "спад", "рецесс"
    ]
    
    # Нейтральные индикаторы (вес 1)
    neutral_words = [
        "остал", "стабильн", "без изменен", "сохран", "поддерж", "удержал",
        "на уровне", "в рамках", "соответств", "планов", "ожидан", "прежн", 
        "неизменн", "статично", "постоянн", "обычн", "средн", "типичн"
    ]
    
    # Подсчитываем взвешенные очки
    pos_score = (
        sum(2 for word in strong_positive if word in text_lower) +
        sum(1 for word in positive_words if word in text_lower)
    )
    
    neg_score = (
        sum(2 for word in strong_negative if word in text_lower) +
        sum(1 for word in negative_words if word in text_lower)
    )
    
    neutral_score = sum(1 for word in neutral_words if word in text_lower)
    
    # Логика принятия решения
    if neutral_score > 0 and abs(pos_score - neg_score) <= 1:
        return "neutral"
    elif pos_score > neg_score:
        return "positive"
    elif neg_score > pos_score:
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
            
            # Всегда получаем rule-based результат для сравнения
            rule_result = _rule_based_sentiment_ru(text)
            print(f"⚡ Rule-based результат: {rule_result}")
            
            # Улучшенная логика комбинирования:
            # 1. Если ML очень уверен (>0.7), используем ML
            # 2. Если есть согласие между ML и rule-based, используем его
            # 3. При низкой уверенности ML (<0.55), предпочитаем rule-based
            # 4. При конфликте в средней зоне (0.55-0.7), используем взвешенный подход
            
            if confidence > 0.7:
                print(f"🎯 Высокая уверенность ML ({confidence:.3f}), используем: {result}")
            elif rule_result == result:
                print(f"🤝 ML и rule-based согласны: {result}")
            elif confidence < 0.55:
                print(f"🔄 Низкая уверенность ML ({confidence:.3f}), используем rule-based: {rule_result}")
                result = rule_result
            else:
                # Взвешенный подход: учитываем силу rule-based сигналов
                if rule_result != "neutral" and result == "neutral":
                    # Если rule-based видит сильный сигнал, а ML нейтральный - доверяем rule-based
                    print(f"🎯 Rule-based видит сильный сигнал ({rule_result}), ML нейтральный - используем rule-based")
                    result = rule_result
                elif rule_result == "neutral" and result != "neutral":
                    # Если ML видит сигнал при средней уверенности, а rule-based нейтральный - используем ML
                    print(f"🎯 ML видит сигнал ({result}) при средней уверенности - используем ML")
                else:
                    # При полном конфликте используем более консервативный вариант
                    print(f"⚖️ Полный конфликт: ML={result}, rule={rule_result}, выбираем neutral")
                    result = "neutral"
            
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
