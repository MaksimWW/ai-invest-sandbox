
#!/usr/bin/env python
"""
Расширенный тест нового композитного анализатора настроения
"""

def test_contextual_sentiment():
    """Тестирует новый контекстный анализатор"""
    print("🧠 ТЕСТ КОНТЕКСТНОГО АНАЛИЗАТОРА НАСТРОЕНИЙ")
    print("=" * 70)

    # Импортируем функции
    try:
        from nlp.sentiment import classify_ru, classify_en, analyze_sentiment_trend, ContextualSentimentAnalyzer
        print("✅ Импорт новых функций успешен")
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

    # Тесты с учетом величины изменений
    magnitude_tests = [
        # Позитивные с числами
        ("Акции выросли на 15% после отличных результатов", "positive"),
        ("Цена поднялась на 8.5% благодаря хорошим новостям", "positive"),
        ("Apple stock surged 12% on strong earnings", "positive"),
        
        # Позитивные без чисел, но с сильными словами
        ("Компания показала рекордную прибыль", "positive"),
        ("Акции взлетели после breakthrough", "positive"),
        
        # Негативные с числами
        ("Стоимость упала на 10% из-за плохих новостей", "negative"),
        ("Tesla shares plummeted 7% after announcement", "negative"),
        
        # Негативные с сильными словами
        ("Произошел обвал котировок компании", "negative"),
        ("Акции обрушились после кризиса", "negative"),
        
        # Нейтральные (даже если ML видит негатив)
        ("Торги завершились без существенных изменений", "neutral"),
        ("Цена осталась стабильной на уровне 100 рублей", "neutral"),
        ("Microsoft remained flat with 0.1% change", "neutral"),
        
        # Малые изменения (должны быть нейтральными)
        ("Акции выросли на 0.5%", "neutral"),
        ("Цена снизилась на 1%", "neutral"),
    ]

    print(f"\n🧪 Тестируем {len(magnitude_tests)} случаев с учетом контекста:")
    print("-" * 70)

    correct = 0
    total = len(magnitude_tests)

    for i, (text, expected) in enumerate(magnitude_tests, 1):
        print(f"\n📝 Тест {i}: {text}")
        print(f"🎯 Ожидаем: {expected}")

        # Определяем язык и вызываем соответствующую функцию
        if any(russian_char in text for russian_char in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"):
            result = classify_ru(text)
        else:
            result = classify_en(text)

        print(f"✅ Получили: {result}")

        if result == expected:
            print("✅ ПРОЙДЕН")
            correct += 1
        else:
            print("❌ ПРОВАЛЕН")

        print("-" * 50)

    # Результаты
    accuracy = (correct / total) * 100
    print(f"\n📊 РЕЗУЛЬТАТЫ КОНТЕКСТНОГО АНАЛИЗА:")
    print(f"✅ Пройдено: {correct}/{total}")
    print(f"📈 Точность: {accuracy:.1f}%")

    return accuracy

def test_trend_analysis():
    """Тестирует анализ трендов"""
    print("\n📈 ТЕСТ АНАЛИЗА ТРЕНДОВ")
    print("=" * 50)
    
    from nlp.sentiment import analyze_sentiment_trend
    
    # Позитивный тренд
    positive_news = [
        "Акции выросли на 5%",
        "Компания показала отличные результаты", 
        "Прибыль превзошла ожидания"
    ]
    
    # Негативный тренд
    negative_news = [
        "Акции упали на 8%",
        "Компания понесла убытки",
        "Произошел обвал котировок"
    ]
    
    # Смешанный тренд
    mixed_news = [
        "Акции выросли на 3%",
        "Цена упала на 2%",
        "Торги прошли стабильно"
    ]
    
    test_cases = [
        (positive_news, "позитивный"),
        (negative_news, "негативный"), 
        (mixed_news, "смешанный")
    ]
    
    for news_list, expected_type in test_cases:
        result = analyze_sentiment_trend(news_list)
        print(f"\n📰 {expected_type.title()} тренд:")
        print(f"   Среднее настроение: {result['trend']:.2f}")
        print(f"   Уверенность: {result['confidence']:.2f}")
        print(f"   Распределение: {result['distribution']}")

def test_magnitude_extraction():
    """Тестирует извлечение величины изменений"""
    print("\n🔢 ТЕСТ ИЗВЛЕЧЕНИЯ ВЕЛИЧИНЫ ИЗМЕНЕНИЙ")
    print("=" * 50)
    
    from nlp.sentiment import ContextualSentimentAnalyzer
    analyzer = ContextualSentimentAnalyzer()
    
    test_texts = [
        "Акции выросли на 15.5%",
        "Цена упала на 8,2% за день",
        "Apple stock surged 12% after earnings",
        "Произошел рекордный рост без цифр",
        "Стабильная цена без изменений"
    ]
    
    for text in test_texts:
        magnitude = analyzer.extract_magnitude(text)
        print(f"\n📝 '{text}'")
        print(f"   Числовое значение: {magnitude['numeric_value']}")
        print(f"   Сильные сигналы: {magnitude['has_strong_signals']}")
        print(f"   Паттерны: {magnitude['magnitude_scores']}")

if __name__ == "__main__":
    print("🚀 ЗАПУСК РАСШИРЕННОГО ТЕСТИРОВАНИЯ")
    print("=" * 70)
    
    # Основной тест
    accuracy = test_contextual_sentiment()
    
    # Дополнительные тесты
    test_trend_analysis()
    test_magnitude_extraction()
    
    print(f"\n🎯 ФИНАЛЬНАЯ ОЦЕНКА:")
    if accuracy >= 85:
        print("🏆 Превосходный результат! Система готова к продакшену")
    elif accuracy >= 75:
        print("🎉 Отличный результат! Значительное улучшение")
    elif accuracy >= 65:
        print("👍 Хороший прогресс, но есть место для доработок")
    else:
        print("⚠️ Требуются дополнительные улучшения")
