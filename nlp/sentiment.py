
from functools import lru_cache
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch, requests, datetime as dt, re
from news_feed import fetch_news
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

def classify_ru_ensemble(text: str) -> str:
    """Ensemble анализ русского текста с несколькими моделями"""
    print(f"🧠 ENSEMBLE АНАЛИЗ RU: '{text[:50]}...'")
    print("=" * 60)
    
    try:
        # 1. ML Ensemble
        ml_result = _ensemble_analyzer._ensemble_predict(
            text, MODEL_CONFIG["ru_models"], "ru"
        )
        print(f"🤖 ML Ensemble: {ml_result['sentiment']} (conf: {ml_result['confidence']:.3f})")
        
        # 2. Финансовые термины
        financial_signals = _ensemble_analyzer._extract_financial_signals(text, "ru")
        print(f"💰 Финансовые сигналы: {financial_signals}")
        
        # 3. Числовой контекст
        numeric_context = _ensemble_analyzer._extract_numeric_context(text)
        print(f"🔢 Числовой контекст: {numeric_context}")
        
        # 4. Комбинируем результаты
        final_score = 0
        
        # ML вклад
        ml_score = {'positive': 1, 'negative': -1, 'neutral': 0}.get(ml_result['sentiment'], 0)
        final_score += ml_score * _ensemble_analyzer.weights['ml_ensemble'] * ml_result['confidence']
        
        # Финансовые термины
        if financial_signals['positive'] > financial_signals['negative']:
            term_score = min(1.0, financial_signals['positive'] / 3.0)
        elif financial_signals['negative'] > financial_signals['positive']:
            term_score = -min(1.0, financial_signals['negative'] / 3.0)
        else:
            term_score = 0
        
        final_score += term_score * _ensemble_analyzer.weights['financial_terms']
        
        # Числовой контекст
        if numeric_context['magnitude'] > 0:
            magnitude_weight = min(1.0, numeric_context['magnitude'] / 10.0)  # нормализуем к 1.0
            numeric_score = numeric_context['direction'] * magnitude_weight
            final_score += numeric_score * _ensemble_analyzer.weights['numeric_context']
            print(f"📊 Числовой вклад: {numeric_score:.3f} (направление: {numeric_context['direction']}, величина: {numeric_context['magnitude']}%)")
        
        # Определяем финальный результат
        if final_score > 0.3:
            result = 'positive'
        elif final_score < -0.3:
            result = 'negative'
        else:
            result = 'neutral'
        
        print(f"🎯 Финальный скор: {final_score:.3f} → {result}")
        print("=" * 60)
        
        return result
        
    except Exception as e:
        print(f"⚠️ Ошибка ensemble анализа: {e}")
        return "neutral"

def classify_en_ensemble(text: str) -> str:
    """Ensemble анализ английского текста с FinBERT и RoBERTa"""
    print(f"🧠 ENSEMBLE АНАЛИЗ EN: '{text[:50]}...'")
    print("=" * 60)
    
    try:
        # ML Ensemble для английского
        ml_result = _ensemble_analyzer._ensemble_predict(
            text, MODEL_CONFIG["en_models"], "en"
        )
        print(f"🤖 ML Ensemble: {ml_result['sentiment']} (conf: {ml_result['confidence']:.3f})")
        
        # Финансовые термины
        financial_signals = _ensemble_analyzer._extract_financial_signals(text, "en")
        print(f"💰 Финансовые сигналы: {financial_signals}")
        
        # Числовой контекст
        numeric_context = _ensemble_analyzer._extract_numeric_context(text)
        print(f"🔢 Числовой контекст: {numeric_context}")
        
        # Для английского больше доверяем ML (особенно FinBERT)
        weights_en = {'ml_ensemble': 0.7, 'financial_terms': 0.2, 'numeric_context': 0.1}
        
        final_score = 0
        
        # ML вклад (больший вес для английского)
        ml_score = {'positive': 1, 'negative': -1, 'neutral': 0}.get(ml_result['sentiment'], 0)
        final_score += ml_score * weights_en['ml_ensemble'] * ml_result['confidence']
        
        # Остальная логика аналогична русскому
        if financial_signals['positive'] > financial_signals['negative']:
            term_score = min(1.0, financial_signals['positive'] / 3.0)
        elif financial_signals['negative'] > financial_signals['positive']:
            term_score = -min(1.0, financial_signals['negative'] / 3.0)
        else:
            term_score = 0
        
        final_score += term_score * weights_en['financial_terms']
        
        if numeric_context['magnitude'] > 0:
            magnitude_weight = min(1.0, numeric_context['magnitude'] / 10.0)
            numeric_score = numeric_context['direction'] * magnitude_weight
            final_score += numeric_score * weights_en['numeric_context']
        
        # Определяем результат
        if final_score > 0.2:  # Меньший порог для английского
            result = 'positive'
        elif final_score < -0.2:
            result = 'negative'
        else:
            result = 'neutral'
        
        print(f"🎯 Финальный скор: {final_score:.3f} → {result}")
        print("=" * 60)
        
        return result
        
    except Exception as e:
        print(f"⚠️ Ошибка ensemble анализа: {e}")
        return "neutral"

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

# RSS-граббер (без изменений)
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

def latest_news(ticker: str, hours: int = 24) -> list[str]:
    return latest_news_ru(ticker, hours)
