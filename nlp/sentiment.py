
from functools import lru_cache
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch, requests, datetime as dt, re
from news_feed import fetch_news
from langdetect import detect
import warnings
from typing import Dict, List, Tuple

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

class ContextualSentimentAnalyzer:
    """Композитный анализатор с пониманием контекста"""
    
    def __init__(self):
        self.magnitude_patterns = {
            'high_positive': r'(рекорд|взлет|скачок|бум|превзош|breakthrough|surge)',
            'moderate_positive': r'(выросли|рост|увелич|повыш|улучш|improved|gained)',
            'high_negative': r'(обвал|крах|кризис|коллапс|plummet|crash|collapse)',
            'moderate_negative': r'(упали|снизил|падение|уменьш|declined|dropped)',
            'neutral_stable': r'(стабильн|без изменен|остал|remained|stable|flat)'
        }
        
        # Извлечение числовых значений
        self.number_pattern = r'(\d+(?:,\d+)?(?:\.\d+)?)\s*%'
        
    def extract_magnitude(self, text: str) -> Dict[str, float]:
        """Извлекает информацию о величине изменений"""
        text_lower = text.lower()
        
        # Находим числовые значения
        numbers = re.findall(self.number_pattern, text_lower)
        max_number = 0
        if numbers:
            try:
                max_number = max(float(num.replace(',', '.')) for num in numbers)
            except:
                max_number = 0
        
        # Определяем тип изменения по ключевым словам
        magnitude_scores = {}
        for mag_type, pattern in self.magnitude_patterns.items():
            matches = len(re.findall(pattern, text_lower))
            magnitude_scores[mag_type] = matches
            
        return {
            'numeric_value': max_number,
            'magnitude_scores': magnitude_scores,
            'has_strong_signals': any(score > 0 for key, score in magnitude_scores.items() 
                                    if 'high_' in key)
        }
    
    def calculate_contextual_score(self, text: str, ml_result: str, ml_confidence: float) -> Tuple[str, float]:
        """Рассчитывает итоговый скор с учетом контекста"""
        magnitude_info = self.extract_magnitude(text)
        
        # Базовые очки от ML
        ml_score = {
            'positive': 1,
            'negative': -1, 
            'neutral': 0
        }.get(ml_result, 0)
        
        # Корректировка на основе величины изменений
        numeric_bonus = 0
        if magnitude_info['numeric_value'] > 0:
            if magnitude_info['numeric_value'] >= 10:  # Большие изменения
                numeric_bonus = 0.5 if ml_score > 0 else -0.5
            elif magnitude_info['numeric_value'] >= 5:  # Средние изменения
                numeric_bonus = 0.3 if ml_score > 0 else -0.3
        
        # Корректировка на сильные сигналы
        strong_signal_bonus = 0
        if magnitude_info['has_strong_signals']:
            if magnitude_info['magnitude_scores'].get('high_positive', 0) > 0:
                strong_signal_bonus = 0.7
            elif magnitude_info['magnitude_scores'].get('high_negative', 0) > 0:
                strong_signal_bonus = -0.7
        
        # Коррекция смещения русской модели к негативу
        bias_correction = 0
        if ml_result == 'negative' and ml_confidence < 0.7:
            # Если ML слабо уверен в негативе, проверяем нейтральные сигналы
            if magnitude_info['magnitude_scores'].get('neutral_stable', 0) > 0:
                bias_correction = 0.5  # Сдвигаем к нейтральному
        
        # Итоговый скор
        final_score = ml_score + numeric_bonus + strong_signal_bonus + bias_correction
        final_confidence = min(1.0, ml_confidence + abs(numeric_bonus) + abs(strong_signal_bonus))
        
        # Определяем финальный результат
        if final_score > 0.3:
            result = 'positive'
        elif final_score < -0.3:
            result = 'negative'
        else:
            result = 'neutral'
            
        return result, final_confidence

# Глобальный экземпляр анализатора
_context_analyzer = ContextualSentimentAnalyzer()

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

def classify_ru(text: str) -> str:
    """Продвинутый анализ настроения русского текста с контекстным пониманием"""
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
            
            print(f"🔍 АНАЛИЗ: '{text[:50]}...'")
            print(f"📊 ML Вероятности: {[f'{ru_labels[i]}={probabilities[0][i]:.3f}' for i in range(len(ru_labels))]}")
            print(f"🎯 ML Предсказание: {predicted_label} (уверенность: {confidence:.3f})")
            
            ml_result = _normalize_sentiment(predicted_label, "ru")
            
            # Применяем контекстный анализ
            final_result, final_confidence = _context_analyzer.calculate_contextual_score(
                text, ml_result, confidence
            )
            
            print(f"🧠 Контекстная коррекция: {ml_result} → {final_result} (финальная уверенность: {final_confidence:.3f})")
            print(f"✅ Финальный результат: {final_result}")
            
            return final_result
        
        # Если модель не загружена, используем базовый анализ
        else:
            print(f"🔄 Используем базовый анализ для: '{text[:50]}...'")
            return "neutral"
            
    except Exception as e:
        print(f"⚠️ Ошибка анализа: {e}")
        return "neutral"

def classify_en(text: str) -> str:
    """Анализ настроения английского текста с контекстным пониманием"""
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
        
        print(f"🔍 EN АНАЛИЗ: '{text[:50]}...'")
        print(f"📊 Вероятности: {[f'{EN_LABELS[i]}={probabilities[0][i]:.3f}' for i in range(len(EN_LABELS))]}")
        print(f"🎯 Предсказание: {predicted_label} (уверенность: {confidence:.3f})")
        
        ml_result = _normalize_sentiment(predicted_label, "en")
        
        # Применяем контекстный анализ
        final_result, final_confidence = _context_analyzer.calculate_contextual_score(
            text, ml_result, confidence
        )
        
        print(f"🧠 Контекстная коррекция: {ml_result} → {final_result}")
        print(f"✅ Финальный результат: {final_result}")
        
        return final_result
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

def analyze_sentiment_trend(texts: List[str]) -> Dict[str, float]:
    """Анализирует тренд настроения по множеству текстов"""
    if not texts:
        return {'trend': 0.0, 'confidence': 0.0, 'count': 0}
    
    sentiments = []
    for text in texts:
        sentiment = classify_multi(text)
        score = {'positive': 1, 'negative': -1, 'neutral': 0}.get(sentiment, 0)
        sentiments.append(score)
    
    avg_sentiment = sum(sentiments) / len(sentiments)
    
    # Рассчитываем уверенность на основе согласованности
    consistency = 1.0 - (len(set(sentiments)) - 1) / 2.0  # от 0 до 1
    
    return {
        'trend': avg_sentiment,
        'confidence': consistency,
        'count': len(texts),
        'distribution': {
            'positive': sentiments.count(1),
            'negative': sentiments.count(-1),
            'neutral': sentiments.count(0)
        }
    }

# Старые функции для совместимости
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
