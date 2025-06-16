
#!/usr/bin/env python
"""
Тест исправленного анализа настроения
"""

def test_sentiment_fix():
    """Тестирует исправленный анализ настроения"""
    print("🔍 ТЕСТ ИСПРАВЛЕННОГО АНАЛИЗА НАСТРОЕНИЯ")
    print("=" * 50)
    
    # Импортируем функции
    try:
        from nlp.sentiment import classify_ru, classify_en, classify_multi
        print("✅ Импорт функций успешен")
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    
    # Тестовые тексты
    test_texts = [
        ("Отличные новости для инвесторов!", "ru"),
        ("Акции компании упали на 10%", "ru"),
        ("Great news for NVIDIA stock", "en"),
        ("Stock market crashed today", "en")
    ]
    
    print("\n📊 ТЕСТИРУЕМ АНАЛИЗ НАСТРОЕНИЯ:")
    print("-" * 40)
    
    for text, lang in test_texts:
        print(f"\n📝 Текст: {text}")
        print(f"🌍 Язык: {lang}")
        
        try:
            if lang == "ru":
                sentiment = classify_ru(text)
            else:
                sentiment = classify_en(text)
            
            emoji = {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}[sentiment]
            print(f"📈 Настроение: {emoji} {sentiment.upper()}")
            
        except Exception as e:
            print(f"❌ Ошибка анализа: {e}")
            continue
    
    # Тест мультиязычной функции
    print(f"\n🌍 ТЕСТ МУЛЬТИЯЗЫЧНОЙ ФУНКЦИИ:")
    print("-" * 40)
    
    multi_texts = [
        "Яндекс показал отличные результаты",
        "NVIDIA stock is performing well"
    ]
    
    for text in multi_texts:
        try:
            sentiment = classify_multi(text)
            emoji = {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}[sentiment]
            print(f"📝 {text} → {emoji} {sentiment.upper()}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    print(f"\n✅ Тест завершен!")
    return True

if __name__ == "__main__":
    test_sentiment_fix()
