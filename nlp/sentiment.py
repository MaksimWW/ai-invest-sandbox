from functools import lru_cache
# ⬇ отключено: from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from news_feed import fetch_news
from nlp.news_rss_async import async_fetch_all
import asyncio
from langdetect import detect
import warnings
from typing import Dict, List, Tuple, Optional
import statistics

# Подавляем предупреждения о неиспользуемых весах модели
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")

# Конфигурация моделей для ensemble
MODEL_CONFIG = {
    "ru_models": [
        {
            "name": "seara/rubert-base-cased-russian-sentiment",
            "labels": ["NEGATIVE", "NEUTRAL", "POSITIVE"],
            "weight": 0.3,
            "description": "RuBERT специализированный"
        },
        {
            "name": "blanchefort/rubert-base-cased-sentiment",
            "labels": ["NEUTRAL", "POSITIVE", "NEGATIVE"],
            "weight": 0.25,
            "description": "RuBERT базовый"
        },
        {
            "name": "nlptown/bert-base-multilingual-uncased-sentiment",
            "labels": ["1", "2", "3", "4", "5"],  # 1-2=negative, 3=neutral, 4-5=positive
            "weight": 0.45,
            "description": "Мультиязычная модель (приоритетная)"
        }
    ],
    "en_models": [
        {
            "name": "ProsusAI/finbert",
            "labels": ["positive", "negative", "neutral"],
            "weight": 0.6,
            "description": "FinBERT специально для финансов"
        },
        {
            "name": "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "labels": ["LABEL_0", "LABEL_1", "LABEL_2"],
            "weight": 0.4,
            "description": "Twitter RoBERTa"
        }
    ]
}

class FinancialSentimentEnsemble:
    """Ensemble анализатор с несколькими моделями и финансовой логикой"""

    def __init__(self):
        # Финансовые словари
        self.financial_terms = {
            'strong_positive': {
                'ru': ['рекорд', 'взлет', 'скачок', 'бум', 'превзош', 'прорыв', 'резкий рост'],
                'en': ['breakthrough', 'surge', 'soar', 'rally', 'boom', 'outperform', 'beat']
            },
            'moderate_positive': {
                'ru': ['выросли', 'рост', 'увелич', 'повыш', 'улучш', 'прибыль', 'доход'],
                'en': ['improved', 'gained', 'rise', 'increase', 'profit', 'earnings', 'revenue']
            },
            'strong_negative': {
                'ru': ['обвал', 'крах', 'кризис', 'коллапс', 'катастроф', 'провал'],
                'en': ['plummet', 'crash', 'collapse', 'crisis', 'catastrophe', 'disaster']
            },
            'moderate_negative': {
                'ru': ['упали', 'снизил', 'падение', 'уменьш', 'убыт', 'потер'],
                'en': ['declined', 'dropped', 'fell', 'loss', 'decrease', 'down']
            },
            'neutral_stable': {
                'ru': ['стабильн', 'без изменен', 'остал', 'неизменн'],
                'en': ['remained', 'stable', 'flat', 'unchanged', 'steady']
            }
        }

        # Паттерны для числовых значений
        self.number_pattern = r'(\d+(?:,\d+)?(?:\.\d+)?)\s*%'

        # Весовые коэффициенты для разных источников сигналов
        self.weights = {
            'ml_ensemble': 0.5,      # Вес ML-ансамбля
            'financial_terms': 0.3,   # Вес финансовых терминов
            'numeric_context': 0.2    # Вес числового контекста
        }

    def _normalize_multilingual_sentiment(self, label: str, model_name: str) -> str:
        """Нормализует метки разных моделей к единому формату"""
        if "nlptown" in model_name:
            # Мультиязычная модель: 1-2=negative, 3=neutral, 4-5=positive
            if label in ["1", "2"]:
                return "negative"
            elif label == "3":
                return "neutral"
            elif label in ["4", "5"]:
                return "positive"
        elif "finbert" in model_name.lower():
            # FinBERT уже возвращает правильные метки
            return label.lower()
        elif "twitter" in model_name or "cardiff" in model_name:
            # Twitter RoBERTa
            mapping = {"LABEL_0": "negative", "LABEL_1": "neutral", "LABEL_2": "positive"}
            return mapping.get(label, "neutral")
        else:
            # Стандартные RuBERT модели
            label_upper = label.upper()
            if "NEGATIVE" in label_upper or "NEG" in label_upper:
                return "negative"
            elif "POSITIVE" in label_upper or "POS" in label_upper:
                return "positive"
            else:
                return "neutral"

    def _extract_financial_signals(self, text: str, lang: str) -> Dict[str, float]:
        """Извлекает финансовые сигналы из текста"""
        text_lower = text.lower()
        signals = {'positive': 0, 'negative': 0, 'neutral': 0}

        # Проверяем финансовые термины
        for sentiment_type, terms_dict in self.financial_terms.items():
            if lang in terms_dict:
                for term in terms_dict[lang]:
                    if term in text_lower:
                        if 'positive' in sentiment_type:
                            weight = 2.0 if 'strong' in sentiment_type else 1.0
                            signals['positive'] += weight
                        elif 'negative' in sentiment_type:
                            weight = 2.0 if 'strong' in sentiment_type else 1.0
                            signals['negative'] += weight
                        else:  # neutral
                            signals['neutral'] += 1.0

        return signals

    def _extract_numeric_context(self, text: str) -> Dict[str, float]:
        """Анализирует числовой контекст (проценты, суммы)"""
        context = {'magnitude': 0, 'direction': 0}  # direction: +1=рост, -1=падение

        # Ищем проценты
        numbers = re.findall(self.number_pattern, text.lower())
        if numbers:
            try:
                max_number = max(float(num.replace(',', '.')) for num in numbers)
                context['magnitude'] = max_number

                # Определяем направление по контексту
                growth_words = ['выросли', 'рост', 'увелич', 'повыш', 'gained', 'rise', 'up']
                decline_words = ['упали', 'снизил', 'падение', 'уменьш', 'declined', 'dropped', 'down']

                text_lower = text.lower()
                if any(word in text_lower for word in growth_words):
                    context['direction'] = 1
                elif any(word in text_lower for word in decline_words):
                    context['direction'] = -1

            except ValueError:
                pass

        return context

    def _ensemble_predict(self, text: str, models_config: List[Dict], lang: str = "ru") -> Dict[str, float]:
        """Выполняет ensemble предсказание с несколькими моделями"""
        predictions = []
        total_weight = 0

        for model_info in models_config:
            try:
                # Пробуем загрузить и использовать модель
                tokenizer = AutoTokenizer.from_pretrained(model_info["name"])
                model = AutoModelForSequenceClassification.from_pretrained(model_info["name"])
                model.eval()

                inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
                with torch.no_grad():
                    logits = model(**inputs).logits

                probabilities = torch.softmax(logits, dim=-1)
                predicted_idx = logits.argmax().item()
                predicted_label = model_info["labels"][predicted_idx]
                confidence = probabilities[0][predicted_idx].item()

                # Нормализуем результат
                normalized_sentiment = self._normalize_multilingual_sentiment(predicted_label, model_info["name"])

                predictions.append({
                    'sentiment': normalized_sentiment,
                    'confidence': confidence,
                    'weight': model_info["weight"],
                    'model': model_info["description"]
                })
                total_weight += model_info["weight"]

                print(f"🤖 {model_info['description']}: {normalized_sentiment} (conf: {confidence:.3f})")

            except Exception as e:
                print(f"⚠️ Ошибка модели {model_info['name']}: {e}")
                continue

        # Вычисляем взвешенный результат
        if not predictions:
            return {'sentiment': 'neutral', 'confidence': 0.0, 'details': []}

        # Агрегируем результаты
        weighted_scores = {'positive': 0, 'negative': 0, 'neutral': 0}
        total_confidence = 0

        for pred in predictions:
            weight_norm = pred['weight'] / total_weight
            weighted_scores[pred['sentiment']] += weight_norm * pred['confidence']
            total_confidence += weight_norm * pred['confidence']

        # Определяем финальный результат
        final_sentiment = max(weighted_scores, key=weighted_scores.get)
        final_confidence = total_confidence / len(predictions)

        return {
            'sentiment': final_sentiment,
            'confidence': final_confidence,
            'details': predictions,
            'scores': weighted_scores
        }

# Глобальный экземпляр ensemble анализатора
_ensemble_analyzer = FinancialSentimentEnsemble()

@lru_cache(maxsize=10)
def _load_ensemble_models():
    """Кэшированная загрузка моделей для ensemble"""
    print("🔄 Инициализация ensemble моделей...")
    return True  # Модели загружаются динамически в _ensemble_predict

@lru_cache(maxsize=256)
def classify_ru_ensemble(text: str) -> str:
    """Классифицирует русский текст с помощью ensemble моделей"""
    return _ensemble_classify(text, MODEL_CONFIG["ru_models"])

@lru_cache(maxsize=256)  
def classify_en_ensemble(text: str) -> str:
    """Классифицирует английский текст с помощью ensemble моделей"""
    return _ensemble_classify(text, MODEL_CONFIG["en_models"])

def _extract_financial_signals(text: str) -> Dict[str, float]:
    """Извлекает финансовые сигналы из текста (глобальная функция)"""
    financial_terms = {
        'strong_positive': {
            'ru': ['рекорд', 'взлет', 'скачок', 'бум', 'превзош', 'прорыв', 'резкий рост'],
            'en': ['breakthrough', 'surge', 'soar', 'rally', 'boom', 'outperform', 'beat']
        },
        'moderate_positive': {
            'ru': ['выросли', 'рост', 'увелич', 'повыш', 'улучш', 'прибыль', 'доход'],
            'en': ['improved', 'gained', 'rise', 'increase', 'profit', 'earnings', 'revenue']
        },
        'strong_negative': {
            'ru': ['обвал', 'крах', 'кризис', 'коллапс', 'катастроф', 'провал'],
            'en': ['plummet', 'crash', 'collapse', 'crisis', 'catastrophe', 'disaster']
        },
        'moderate_negative': {
            'ru': ['упали', 'снизил', 'падение', 'уменьш', 'убыт', 'потер'],
            'en': ['declined', 'dropped', 'fell', 'loss', 'decrease', 'down']
        },
        'neutral_stable': {
            'ru': ['стабильн', 'без изменен', 'остал', 'неизменн'],
            'en': ['remained', 'stable', 'flat', 'unchanged', 'steady']
        }
    }

    text_lower = text.lower()
    signals = {'positive': 0, 'negative': 0, 'neutral': 0}

    # Определяем язык (простая эвристика)
    lang = 'ru' if any(char in 'абвгдежзийклмнопрстуфхцчшщъыьэюя' for char in text_lower[:50]) else 'en'

    # Проверяем финансовые термины
    for sentiment_type, terms_dict in financial_terms.items():
        if lang in terms_dict:
            for term in terms_dict[lang]:
                if term in text_lower:
                    if 'positive' in sentiment_type:
                        weight = 2.0 if 'strong' in sentiment_type else 1.0
                        signals['positive'] += weight
                    elif 'negative' in sentiment_type:
                        weight = 2.0 if 'strong' in sentiment_type else 1.0
                        signals['negative'] += weight
                    else:  # neutral
                        signals['neutral'] += 1.0

    return signals

def _ensemble_classify(text: str, models_config: list) -> str:
    """Выполняет ensemble предсказание с несколькими моделями"""
    predictions = []
    total_weight = 0

    # Ограничиваем количество используемых моделей для снижения нагрузки
    active_models = models_config[:2]  # Используем только 2 модели

    for model_info in active_models:
        try:
            # Пробуем загрузить и использовать модель с кэшированием
            tokenizer = AutoTokenizer.from_pretrained(
                model_info["name"], 
                cache_dir=".model_cache",
                local_files_only=False
            )
            model = AutoModelForSequenceClassification.from_pretrained(
                model_info["name"],
                cache_dir=".model_cache", 
                local_files_only=False
            )
            model.eval()

            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            with torch.no_grad():
                logits = model(**inputs).logits

            probabilities = torch.softmax(logits, dim=-1)
            predicted_idx = logits.argmax().item()
            predicted_label = model_info["labels"][predicted_idx]
            confidence = probabilities[0][predicted_idx].item()

            # Конвертируем в стандартный формат
            if predicted_label.upper() in ["POSITIVE", "POS"]:
                sentiment_score = 1.0
            elif predicted_label.upper() in ["NEGATIVE", "NEG"]:
                sentiment_score = -1.0
            else:
                sentiment_score = 0.0

            predictions.append(sentiment_score * confidence * model_info["weight"])
            total_weight += model_info["weight"]

        except Exception as e:
            print(f"⚠️ Модель {model_info['name'][:20]}... недоступна")
            continue

    if not predictions:
        return "neutral"

    # Вычисляем взвешенный результат
    ensemble_score = sum(predictions) / total_weight if total_weight > 0 else 0

    # Добавляем финансовый контекст
    financial_signals = _extract_financial_signals(text)

    # Итоговый скор с учетом финансовых сигналов
    final_score = (
        ensemble_score * 0.8 +
        (financial_signals['positive'] - financial_signals['negative']) * 0.2
    )

    if final_score > 0.1:
        result = "positive"
    elif final_score < -0.1:
        result = "negative"
    else:
        result = "neutral"

    return result

# Основные функции с ensemble подходом
def classify_ru(text: str) -> str:
    """Главная функция для анализа русского текста"""
    return classify_ru_ensemble(text)

def classify_en(text: str) -> str:
    """Главная функция для анализа английского текста"""
    return classify_en_ensemble(text)

def classify_multi(text: str) -> str:
    """Мультиязычный анализ настроения с ensemble"""
    try:
        lang = detect(text[:200])
        if lang == "ru":
            return classify_ru_ensemble(text)
        else:
            return classify_en_ensemble(text)
    except Exception as e:
        print(f"⚠️ Ошибка определения языка: {e}")
        return classify_en_ensemble(text)

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
    consistency = 1.0 - (len(set(sentiments)) - 1) / 2.0

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

# Обратная совместимость
def classify(text: str) -> str:
    return classify_ru(text)

def classify_llm(text: str) -> str:
    """Алиас для LLM классификации через sentiment_llm модуль"""
    from nlp.sentiment_llm import smart_classify
    return smart_classify(text)
# ------------------------------------------------------------------------
# ↓↓↓ MINI-RSS helper: 🇷🇺-заголовки за N часов
# ------------------------------------------------------------------------
from datetime import datetime, timedelta
from nlp.news_feed import _rss_query

# ───────────────────────────────────────────────────────────
#  RSS-Sentiment summary (OpenAI)
# ───────────────────────────────────────────────────────────
import os, json, openai
from collections import Counter
from typing import Dict

def rss_sentiment_summary(hours: int = 24) -> Dict[str, int]:
    """
    Возвращает {'positive': N, 'neutral': M, 'negative': K} для русских RSS-новостей
    за *hours* часов.  Может вернуть пустой dict, если новостей нет.
    Требует переменной окружения OPENAI_API_KEY.
    """
    headlines = fetch_ru_news(hours)
    if not headlines:
        return {}

    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY не установлен")

    prompt = (
        "Классифицируй тональность заголовков (positive / neutral / negative) "
        "и выведи JSON вида {\"positive\":N,\"neutral\":M,\"negative\":K}.\n\n"
        + "\n".join(f"- {h}" for h in headlines[:25])  # ≤25 строк, чтобы уложиться в токены
    )

    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=50,
        temperature=0,
    )
    try:
        counts = json.loads(chat.choices[0].message.content.strip())
        # приводим к int и заполняем отсутствующие ключи нулями
        total = Counter({k: int(counts.get(k, 0)) for k in ("positive", "neutral", "negative")})
        return dict(total)
    except Exception:
        return {}


# ─────────────────────────────────────────────────────────────
# 🚀 robust fetch_ru_news — берёт все RSS-ленты, где бы они ни хранились
# ─────────────────────────────────────────────────────────────
from datetime import datetime, timedelta


# ─────────────────────────────────────────────────────────────
# 🚀 robust fetch_ru_news — собирает 🇷🇺 RSS-заголовки за N часов
# ─────────────────────────────────────────────────────────────
from datetime import datetime, timedelta

    cutoff  = datetime.utcnow() - timedelta(hours=hours)
    titles: list[str] = []

    for url in _FEEDS:
        try:
            for art in _rss_query(url):
                if (
                    art.get("dt") and art["dt"] >= cutoff
                    and art.get("title")
                ):
                    titles.append(art["title"].strip())
        except Exception:
            # падающий источник просто пропускаем
            continue
    return titles


# ─────────────────────────────────────────────────────────────
# 🚀 robust fetch_ru_news — собирает 🇷🇺 RSS-заголовки за N часов
# ─────────────────────────────────────────────────────────────
from datetime import datetime, timedelta
def fetch_ru_news(hours: int = 24) -> list[str]:
    """Возвращает русскоязычные заголовки за *hours* часов."""
    # ➊ пытаемся найти список лент
    try:
        from nlp.news_feed import RSS_FEED_URLS as _FEEDS            # современный вариант
    except ImportError:
        try:
            from nlp.news_rss_async import RSS_FEEDS as _DICT        # старый словарь
            _FEEDS = list(_DICT.values())
        except ImportError:
            _FEEDS = []                                              # ничего не нашли

    # ➋ берём парсер RSS-ленты
    try:
        from nlp.news_feed import _rss_query
    except ImportError:
        return []

    cutoff  = datetime.utcnow() - timedelta(hours=hours)
    titles: list[str] = []

    for url in _FEEDS:
        try:
            for art in _rss_query(url):
                if art.get("dt") and art["dt"] >= cutoff and art.get("title"):
                    titles.append(art["title"].strip())
        except Exception:
            continue    # падающий источник пропускаем
    return titles

