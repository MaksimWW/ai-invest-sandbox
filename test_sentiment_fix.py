
#!/usr/bin/env python
"""
Тест нового ensemble анализатора настроения
"""

def test_ensemble_sentiment():
    """Тестирует новый ensemble анализатор"""
    print("🎭 ТЕСТ ENSEMBLE АНАЛИЗАТОРА НАСТРОЕНИЙ")
    print("=" * 70)

    try:
        from nlp.sentiment import classify_ru_ensemble, classify_en_ensemble, classify_multi
        print("✅ Импорт ensemble функций успешен")
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

    # Специальные тесты для финансовых новостей
    financial_tests = [
        # Позитивные с сильными сигналами
        ("Акции Сбербанка показали рекордный рост на 15% после превосходных результатов", "positive"),
        ("Компания продемонстрировала прорыв в технологиях, акции взлетели на 12%", "positive"),
        ("Apple stock surged 18% after breakthrough earnings beat", "positive"),
        ("Tesla shares soared 20% on record delivery numbers", "positive"),
        
        # Позитивные умеренные
        ("Прибыль компании выросла на 8% по сравнению с прошлым годом", "positive"),
        ("Доходы увеличились на 6.5% благодаря улучшению продаж", "positive"),
        ("Microsoft shares gained 7% on improved revenue guidance", "positive"),
        ("Netflix stock rose 5% after subscriber growth", "positive"),
        
        # Негативные с сильными сигналами
        ("Произошел обвал акций на 20% после кризиса в компании", "negative"),
        ("Котировки рухнули на 15% из-за катастрофических убытков", "negative"),
        ("GameStop shares plummeted 25% after massive losses", "negative"),
        ("Crypto market crashed 30% following regulatory concerns", "negative"),
        
        # Негативные умеренные
        ("Стоимость акций снизилась на 7% после слабых результатов", "negative"),
        ("Цена упала на 5% из-за снижения прогнозов", "negative"),
        ("Amazon stock declined 6% on disappointing guidance", "negative"),
        ("Ford shares dropped 4% after production cuts", "negative"),
        
        # Нейтральные (важные для финансов)
        ("Торги завершились без существенных изменений", "neutral"),
        ("Цена осталась стабильной на уровне 150 рублей", "neutral"),
        ("Google stock remained flat with 0.2% change", "neutral"),
        ("Boeing shares traded sideways with minimal movement", "neutral"),
        
        # Смешанные сигналы (тест устойчивости)
        ("Акции выросли на 3%, но аналитики снизили рейтинг", "neutral"),
        ("Несмотря на убытки, компания повысила дивиденды на 2%", "neutral"),
        ("Mixed earnings results led to 1% gain in volatile trading", "neutral"),
        
        # Малые изменения (должны быть нейтральными)
        ("Незначительный рост на 0.8% при низких объемах", "neutral"),
        ("Минимальное снижение на 1.2% в спокойных торгах", "neutral"),
    ]

    print(f"\n🧪 Тестируем {len(financial_tests)} финансовых случаев:")
    print("-" * 70)

    correct = 0
    total = len(financial_tests)
    results_by_category = {
        'positive': {'correct': 0, 'total': 0},
        'negative': {'correct': 0, 'total': 0},
        'neutral': {'correct': 0, 'total': 0}
    }

    for i, (text, expected) in enumerate(financial_tests, 1):
        print(f"\n📝 Тест {i}: {text}")
        print(f"🎯 Ожидаем: {expected}")

        # Определяем язык и вызываем соответствующую функцию
        if any(russian_char in text.lower() for russian_char in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"):
            result = classify_ru_ensemble(text)
        else:
            result = classify_en_ensemble(text)

        print(f"✅ Получили: {result}")

        # Обновляем статистику
        results_by_category[expected]['total'] += 1
        if result == expected:
            print("✅ ПРОЙДЕН")
            correct += 1
            results_by_category[expected]['correct'] += 1
        else:
            print("❌ ПРОВАЛЕН")

        print("-" * 50)

    # Подробная статистика
    accuracy = (correct / total) * 100
    print(f"\n📊 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ ENSEMBLE АНАЛИЗА:")
    print(f"✅ Общая точность: {correct}/{total} = {accuracy:.1f}%")
    
    for category, stats in results_by_category.items():
        if stats['total'] > 0:
            cat_accuracy = (stats['correct'] / stats['total']) * 100
            print(f"📈 {category.upper()}: {stats['correct']}/{stats['total']} = {cat_accuracy:.1f}%")

    return accuracy

def test_model_ensemble_details():
    """Тестирует детали работы ensemble"""
    print("\n🔬 ТЕСТ ДЕТАЛЕЙ ENSEMBLE МОДЕЛИ")
    print("=" * 50)
    
    from nlp.sentiment import _ensemble_analyzer
    
    test_texts = [
        "Акции выросли на 15% после рекордных результатов",
        "Apple stock surged 12% on strong earnings",
        "Цена осталась без изменений"
    ]
    
    for text in test_texts:
        print(f"\n📰 Анализируем: '{text}'")
        
        # Тестируем извлечение финансовых сигналов
        lang = "ru" if any(c in text.lower() for c in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя") else "en"
        financial_signals = _ensemble_analyzer._extract_financial_signals(text, lang)
        print(f"💰 Финансовые сигналы: {financial_signals}")
        
        # Тестируем числовой контекст
        numeric_context = _ensemble_analyzer._extract_numeric_context(text)
        print(f"🔢 Числовой контекст: {numeric_context}")

def test_performance_comparison():
    """Сравнивает производительность старого и нового подходов"""
    print("\n⚡ СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ")
    print("=" * 50)
    
    # Набор тестовых случаев для сравнения
    comparison_tests = [
        ("Акции Сбербанка выросли на 5%", "positive"),
        ("Компания показала убытки", "negative"),
        ("Цена осталась без изменений", "neutral"),
        ("Apple stock surged after earnings", "positive"),
        ("Tesla shares plummeted", "negative"),
        ("Microsoft remained flat", "neutral")
    ]
    
    try:
        # Импортируем старые и новые функции
        from nlp.sentiment import classify_ru_ensemble, classify_en_ensemble
        # Можно было бы импортировать старые, но они теперь указывают на новые
        
        print("🔄 Тестируем новый ensemble подход...")
        
        ensemble_correct = 0
        for text, expected in comparison_tests:
            if any(c in text.lower() for c in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"):
                result = classify_ru_ensemble(text)
            else:
                result = classify_en_ensemble(text)
            
            if result == expected:
                ensemble_correct += 1
            
            print(f"📝 '{text[:30]}...' → {result} ({'✅' if result == expected else '❌'})")
        
        ensemble_accuracy = (ensemble_correct / len(comparison_tests)) * 100
        print(f"\n🎯 Ensemble точность: {ensemble_accuracy:.1f}%")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")

if __name__ == "__main__":
    print("🚀 ЗАПУСК ТЕСТИРОВАНИЯ ENSEMBLE АНАЛИЗАТОРА")
    print("=" * 70)
    
    # Основной тест
    accuracy = test_ensemble_sentiment()
    
    # Дополнительные тесты
    test_model_ensemble_details()
    test_performance_comparison()
    
    print(f"\n🏆 ФИНАЛЬНАЯ ОЦЕНКА ENSEMBLE СИСТЕМЫ:")
    if accuracy >= 85:
        print("🥇 Превосходный результат! Ensemble система работает отлично")
    elif accuracy >= 75:
        print("🥈 Отличный результат! Значительное улучшение достигнуто")
    elif accuracy >= 65:
        print("🥉 Хороший прогресс! Ensemble подход показывает потенциал")
    else:
        print("⚠️ Требуется дальнейшая настройка ensemble системы")
        
    print("\n💡 КЛЮЧЕВЫЕ ОСОБЕННОСТИ НОВОГО ПОДХОДА:")
    print("• 🤖 Мультимодельный ensemble (RuBERT + Multilingual + FinBERT)")
    print("• 💰 Специализированные финансовые словари") 
    print("• 🔢 Интеллектуальный анализ числовых показателей")
    print("• ⚖️ Взвешенное комбинирование разных источников сигналов")
    print("• 🌍 Отдельная оптимизация для русского и английского")
