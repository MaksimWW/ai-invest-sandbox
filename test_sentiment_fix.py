#!/usr/bin/env python
"""
Улучшенный тест анализа настроения с детальной проверкой
"""

def test_sentiment_improvements():
    """Тестирует улучшения анализа настроения"""
    print("🔍 ТЕСТ УЛУЧШЕНИЙ АНАЛИЗА НАСТРОЕНИЯ")
    print("=" * 60)

    # Импортируем функции
    try:
        from nlp.sentiment import classify_ru, classify_en, _rule_based_sentiment_ru
        print("✅ Импорт функций успешен")
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

    # Тестовые случаи с ожидаемыми результатами
    test_cases = [
        # Явно позитивные
        ("Акции Сбербанка выросли на 10% после отличных результатов", "positive"),
        ("Компания показала рекордную прибыль и превзошла ожидания", "positive"),
        ("Apple stock surged 15% after breakthrough earnings", "positive"),

        # Явно негативные  
        ("Акции упали на 8% из-за убытков компании", "negative"),
        ("Tesla shares plummeted after disappointing results", "negative"),
        ("Компания объявила о кризисе и массовых увольнениях", "negative"),

        # Нейтральные
        ("Цена осталась стабильной на уровне предыдущего дня", "neutral"),
        ("Торги прошли без существенных изменений", "neutral"),
        ("Microsoft remained flat with minimal trading volume", "neutral"),
    ]

    print(f"\n🧪 Тестируем {len(test_cases)} случаев:")
    print("-" * 60)

    correct = 0
    total = len(test_cases)

    for i, (text, expected) in enumerate(test_cases, 1):
        print(f"\n📝 Тест {i}: {text[:50]}...")
        print(f"🎯 Ожидаем: {expected}")

        # Определяем язык и вызываем соответствующую функцию
        if any(russian_char in text for russian_char in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"):
            result = classify_ru(text)
            # Также тестируем rule-based
            rule_result = _rule_based_sentiment_ru(text)
            print(f"🔧 Rule-based: {rule_result}")
        else:
            result = classify_en(text)

        print(f"✅ Получили: {result}")

        if result == expected:
            print("✅ ПРОЙДЕН")
            correct += 1
        else:
            print("❌ ПРОВАЛЕН")

        print("-" * 40)

    # Результаты
    accuracy = (correct / total) * 100
    print(f"\n📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    print(f"✅ Пройдено: {correct}/{total}")
    print(f"📈 Точность: {accuracy:.1f}%")

    if accuracy >= 80:
        print("🎉 Отличный результат!")
    elif accuracy >= 60:
        print("👍 Хороший результат, есть место для улучшений")
    else:
        print("⚠️ Требуются дополнительные улучшения")

    return accuracy >= 60

def test_rule_based_weights():
    """Тестирует новую систему весов в rule-based анализе"""
    print("\n🔧 ТЕСТ СИСТЕМЫ ВЕСОВ RULE-BASED")
    print("=" * 50)

    from nlp.sentiment import _rule_based_sentiment_ru

    weight_tests = [
        ("Акции выросли на 5%", "positive"),  # сильное позитивное слово
        ("Цены упали резко", "negative"),     # сильное негативное слово
        ("Хорошие новости", "positive"),      # обычное позитивное
        ("Плохая ситуация", "negative"),      # обычное негативное
        ("Остались стабильными", "neutral"),  # нейтральное
    ]

    for text, expected in weight_tests:
        result = _rule_based_sentiment_ru(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text}' → {result} (ожидали {expected})")

if __name__ == "__main__":
    success = test_sentiment_improvements()
    test_rule_based_weights()

    if success:
        print("\n🎉 Тесты пройдены успешно!")
    else:
        print("\n⚠️ Некоторые тесты провалены, требуются доработки")