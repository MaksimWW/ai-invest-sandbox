
#!/usr/bin/env python
"""
Тестирование нового LLM-анализатора настроения
"""
import os
import sys
sys.path.append('.')

def test_fallback_classifier():
    """Тестирует fallback классификатор"""
    print("🧪 ТЕСТ: Fallback классификатор")
    
    from nlp.sentiment_llm import fallback_classify
    
    test_cases = [
        ("Акции выросли на 5%", "positive"),
        ("Компания показала рост прибыли", "positive"),
        ("Stocks declined sharply", "negative"),
        ("Revenue dropped by 10%", "negative"),
        ("Company reported quarterly results", "neutral")
    ]
    
    correct = 0
    for text, expected in test_cases:
        result = fallback_classify(text)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{text[:30]}...' → {result} (ожидалось: {expected})")
        if result == expected:
            correct += 1
    
    print(f"📊 Точность fallback: {correct}/{len(test_cases)} ({correct/len(test_cases)*100:.1f}%)")
    return correct == len(test_cases)

def test_cache_functionality():
    """Тестирует кэширование"""
    print("\n🧪 ТЕСТ: Кэширование")
    
    from nlp.sentiment_llm import smart_classify, get_cache_stats, cache_get, get_text_hash
    
    # Тестируем кэширование
    test_text = "Test news about company growth"
    
    print("  🔄 Первый вызов (должен идти в LLM/fallback)...")
    result1 = smart_classify(test_text, "TEST")
    
    print("  🔄 Второй вызов (должен брать из кэша)...")
    result2 = smart_classify(test_text, "TEST")
    
    # Проверяем, что результаты одинаковые
    cache_works = result1 == result2
    print(f"  {'✅' if cache_works else '❌'} Кэш: {result1} == {result2}")
    
    # Проверяем, что запись действительно в кэше
    text_hash = get_text_hash(test_text.strip())
    cached = cache_get(text_hash)
    has_cached = cached is not None
    print(f"  {'✅' if has_cached else '❌'} Запись в кэше: {has_cached}")
    
    # Статистика кэша
    stats = get_cache_stats()
    print(f"  📊 Статистика кэша: {stats}")
    
    return cache_works and has_cached

def test_sentiment_integration():
    """Тестирует интеграцию с основной системой"""
    print("\n🧪 ТЕСТ: Интеграция с системой")
    
    try:
        from daily_plan_bot import get_sentiment_score
        
        # Тестируем получение score для тикера
        print("  🔄 Тестируем get_sentiment_score для YNDX...")
        score = get_sentiment_score("YNDX", hours=48)
        
        print(f"  📊 Score для YNDX: {score}")
        print(f"  {'✅' if isinstance(score, int) else '❌'} Возвращает int: {type(score)}")
        
        return isinstance(score, int)
        
    except Exception as e:
        print(f"  ❌ Ошибка интеграции: {e}")
        return False

def test_openai_config():
    """Проверяет конфигурацию OpenAI"""
    print("\n🧪 ТЕСТ: Конфигурация OpenAI")
    
    api_key = os.getenv("OPENAI_API_KEY")
    llm_off = os.getenv("LLM_OFF", "0")
    
    print(f"  🔑 OPENAI_API_KEY: {'✅ настроен' if api_key else '❌ не настроен'}")
    print(f"  🔌 LLM_OFF: {llm_off}")
    
    if not api_key:
        print("  💡 Для полного тестирования установите OPENAI_API_KEY")
        print("  💡 Пока что система будет работать в режиме fallback")
    
    return True

def main():
    """Запускает все тесты"""
    print("🧪 ТЕСТИРОВАНИЕ LLM SENTIMENT ANALYZER")
    print("=" * 50)
    
    tests = [
        ("Конфигурация OpenAI", test_openai_config),
        ("Fallback классификатор", test_fallback_classifier),
        ("Кэширование", test_cache_functionality),
        ("Интеграция", test_sentiment_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {name}: PASSED")
            else:
                print(f"❌ {name}: FAILED")
        except Exception as e:
            print(f"💥 {name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 РЕЗУЛЬТАТ: {passed}/{total} тестов прошли успешно")
    
    if passed == total:
        print("🎉 Все тесты пройдены! LLM-анализатор готов к работе.")
    else:
        print("⚠️ Есть проблемы, требующие исправления.")

if __name__ == "__main__":
    main()
