
#!/usr/bin/env python
"""
Улучшенный тест анализа настроения с отладкой
"""

def test_sentiment_debug():
    """Тестирует анализ настроения с подробной отладкой"""
    print("🔍 ОТЛАДОЧНЫЙ ТЕСТ АНАЛИЗА НАСТРОЕНИЯ")
    print("=" * 60)
    
    # Импортируем функции
    try:
        from nlp.sentiment import classify_ru, classify_en, classify_multi
        print("✅ Импорт функций успешен")
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    
    # Тестовые тексты с ожидаемыми результатами
    test_cases = [
        # Русские тексты - более явные примеры
        ("Сбербанк показал рекордную прибыль и рост доходов", "ru", "positive"),
        ("Отличные новости! Компания увеличила выручку на 50%", "ru", "positive"),
        ("Акции компании упали на 15%, убытки растут", "ru", "negative"),
        ("Курс акций остался стабильным без изменений", "ru", "neutral"),
        
        # Английские тексты
        ("NVIDIA stock is performing exceptionally well", "en", "positive"),
        ("Great news for NVIDIA stock", "en", "positive"),
        ("Stock market crashed today", "en", "negative"),
        ("The price remained stable", "en", "neutral")
    ]
    
    print(f"\n📊 ПОДРОБНЫЙ АНАЛИЗ:")
    print("-" * 60)
    
    correct = 0
    total = len(test_cases)
    
    for i, (text, lang, expected) in enumerate(test_cases, 1):
        print(f"\n🧪 ТЕСТ {i}/{total}")
        print(f"📝 Текст: '{text}'")
        print(f"🌍 Язык: {lang}")
        print(f"🎯 Ожидаемый результат: {expected}")
        print("-" * 40)
        
        try:
            if lang == "ru":
                result = classify_ru(text)
            else:
                result = classify_en(text)
            
            # Проверяем результат
            is_correct = result == expected
            status = "✅ ПРАВИЛЬНО" if is_correct else "❌ НЕПРАВИЛЬНО"
            
            print(f"🏁 Получен результат: {result}")
            print(f"📋 Статус: {status}")
            
            if is_correct:
                correct += 1
                
        except Exception as e:
            print(f"❌ Ошибка анализа: {e}")
            continue
        
        print("=" * 60)
    
    # Итоговая статистика
    accuracy = (correct / total) * 100
    print(f"\n📈 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"✅ Правильных ответов: {correct}/{total}")
    print(f"📊 Точность: {accuracy:.1f}%")
    
    if accuracy >= 75:
        print("🎉 ОТЛИЧНЫЙ РЕЗУЛЬТАТ!")
    elif accuracy >= 50:
        print("⚠️  УДОВЛЕТВОРИТЕЛЬНО: Можно улучшить")
    else:
        print("❌ НИЗКАЯ ТОЧНОСТЬ: Требуется доработка")
    
    print(f"\n✅ Тест завершен!")
    return accuracy >= 50

if __name__ == "__main__":
    test_sentiment_debug()
