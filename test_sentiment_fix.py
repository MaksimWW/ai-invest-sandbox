
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
    
    # Расширенные тестовые тексты
    test_cases = [
        # Русские тексты - более явные примеры
        ("Сбербанк показал отличные результаты и увеличил прибыль", "ru", "positive"),
        ("Акции упали из-за плохих новостей о компании", "ru", "negative"),
        ("Цена акций осталась без изменений", "ru", "neutral"),
        ("Курс остался стабильным на уровне предыдущего дня", "ru", "neutral"),
        ("Компания сохранила позиции в рамках ожиданий", "ru", "neutral"),
        ("Рекордный рост выручки на 25%", "ru", "positive"),
        ("Катастрофическое падение акций", "ru", "negative"),
        
        # Английские тексты
        ("Apple stock surged to new highs on strong earnings", "en", "positive"),
        ("Tesla shares plummeted after disappointing results", "en", "negative"),
        ("Microsoft stock remained flat during trading", "en", "neutral"),
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
        
        print("=" * 40)
    
    # Итоговая статистика
    accuracy = (correct / total) * 100
    print(f"\n📈 ИТОГИ:")
    print(f"✅ Правильных: {correct}/{total}")
    print(f"📊 Точность: {accuracy:.1f}%")
    
    if accuracy >= 80:
        print("🎉 Отличный результат!")
    elif accuracy >= 60:
        print("⚠️ Удовлетворительно, но есть место для улучшений")
    else:
        print("❌ Требуются серьезные улучшения")
    
    return accuracy >= 60

def test_models_loading():
    """Проверяет загрузку моделей"""
    print("🔧 ПРОВЕРКА ЗАГРУЗКИ МОДЕЛЕЙ")
    print("=" * 40)
    
    try:
        from nlp.sentiment import _load_models
        ru_tok, ru_mdl, ru_labels, en_tok, en_mdl = _load_models()
        
        print(f"📊 СТАТУС МОДЕЛЕЙ:")
        print(f"  • Русский токенизатор: {'✅ OK' if ru_tok else '❌ Ошибка'}")
        print(f"  • Русская модель: {'✅ OK' if ru_mdl else '❌ Ошибка'}")
        print(f"  • Английский токенизатор: {'✅ OK' if en_tok else '❌ Ошибка'}")
        print(f"  • Английская модель: {'✅ OK' if en_mdl else '❌ Ошибка'}")
        
        if ru_labels:
            print(f"  • Русские метки: {ru_labels}")
        
        return all([ru_tok, ru_mdl, en_tok, en_mdl])
        
    except Exception as e:
        print(f"❌ Ошибка проверки моделей: {e}")
        return False

def test_news_integration():
    """Тестирует интеграцию с новостями"""
    print("📋 ТЕСТ ПОЛУЧЕНИЯ НОВОСТЕЙ:")
    print("=" * 40)
    
    try:
        from news_feed import fetch_news
        from nlp.sentiment import latest_news_ru
        
        # Тест английских новостей
        print("📰 Запрашиваем NewsAPI для AAPL...")
        en_news = fetch_news("AAPL", hours=24)
        print(f"✅ NewsAPI: найдено {len(en_news)} новостей")
        
        # Тест русских новостей
        print("📰 Запрашиваем RSS для YNDX...")
        ru_news = latest_news_ru("YNDX", hours=48)  # Увеличиваем период
        print(f"✅ RSS: найдено {len(ru_news)} новостей")
        
        for ticker in ["AAPL"]:
            total_news = len(fetch_news(ticker, hours=24))
            print(f"📊 Итого для {ticker}: {total_news} новостей (NewsAPI: {len(en_news)}, GDELT: 0)")
            print(f"  • Найдено {total_news} новостей для {ticker}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования новостей: {e}")
        return False

def run_full_test():
    """Запускает полный тест системы"""
    print("🔬 АВТОМАТИЧЕСКИЙ ТЕСТ СИСТЕМЫ")
    print("=" * 50)
    
    # Тест загрузки моделей
    models_ok = test_models_loading()
    print()
    
    # Тест анализа настроения
    sentiment_ok = test_sentiment_debug()
    print()
    
    # Тест новостей
    news_ok = test_news_integration()
    print()
    
    print("✅ Автоматический тест завершен")
    
    return models_ok and sentiment_ok and news_ok

if __name__ == "__main__":
    run_full_test()
