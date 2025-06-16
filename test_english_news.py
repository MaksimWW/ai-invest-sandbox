
#!/usr/bin/env python
"""
Тест англоязычного агрегатора новостей
"""

import os
import sys
sys.path.append('.')
from news_feed import fetch_news

def test_english_news():
    """Тестирует работу англоязычного агрегатора новостей"""
    
    print("📰 ТЕСТ АНГЛОЯЗЫЧНОГО АГРЕГАТОРА НОВОСТЕЙ")
    print("=" * 60)
    
    # Проверяем настройку API ключа
    newsapi_key = os.getenv("NEWSAPI_KEY")
    if newsapi_key:
        masked_key = newsapi_key[:8] + "..." if len(newsapi_key) > 8 else "***"
        print(f"🔑 NewsAPI Key: {masked_key}")
    else:
        print("⚠️ NewsAPI Key: НЕ НАСТРОЕН (будет использоваться только GDELT)")
    
    print(f"🌐 Источники:")
    print(f"   • NewsAPI.org {'✅' if newsapi_key else '❌'}")
    print(f"   • GDELT Project ✅")
    
    # Тестируем популярные тикеры
    test_tickers = ["AAPL", "TSLA", "GOOGL", "MSFT", "NVDA", "META"]
    
    print(f"\n🔍 Ищем англоязычные новости за последние 48 часов...")
    print("-" * 60)
    
    total_news = 0
    
    for ticker in test_tickers:
        print(f"\n📊 {ticker}:")
        
        try:
            news_list = fetch_news(ticker, hours=48)
            
            if news_list:
                print(f"   ✅ Найдено {len(news_list)} новостей")
                total_news += len(news_list)
                
                # Показываем первые 3 новости
                for i, title in enumerate(news_list[:3], 1):
                    print(f"   {i}. {title[:100]}...")
                
                if len(news_list) > 3:
                    print(f"   ... и ещё {len(news_list) - 3} новостей")
            else:
                print(f"   ❌ Новостей не найдено")
                
        except Exception as e:
            print(f"   ⚠️ Ошибка: {e}")
    
    print(f"\n📈 ИТОГО:")
    print(f"   • Всего найдено новостей: {total_news}")
    print(f"   • NewsAPI статус: {'Активен' if newsapi_key else 'Не настроен'}")
    print(f"   • GDELT статус: Активен")
    
    if total_news > 0:
        print("   ✅ Англоязычный агрегатор работает корректно!")
    else:
        print("   ⚠️ Новости не найдены - возможно, тикеры не популярны в англоязычных СМИ")

def test_gdelt_specifically():
    """Тестирует конкретно GDELT API"""
    
    print(f"\n🌐 ДЕТАЛЬНЫЙ ТЕСТ GDELT API")
    print("-" * 50)
    
    import requests
    import datetime as dt
    
    # Тестируем прямой запрос к GDELT
    test_query = "AAPL"
    since = int((dt.datetime.utcnow() - dt.timedelta(hours=24)).timestamp())
    
    url = (f"https://api.gdeltproject.org/api/v2/doc/docsearch"
           f"?query={test_query}&filter=SourceCommonName:english&maxrecords=10"
           f"&format=json&mode=ArtList&filter=PublishDate>{since}")
    
    print(f"🔗 Тестовый запрос: {test_query}")
    print(f"📅 За последние 24 часа")
    
    try:
        print("📤 Запрашиваем GDELT API...")
        response = requests.get(url, timeout=10)
        
        print(f"📊 HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                articles = data.get("artList", [])
                print(f"📰 Найдено статей: {len(articles)}")
                
                if articles:
                    print(f"📝 Примеры заголовков:")
                    for i, article in enumerate(articles[:3], 1):
                        title = article.get("title", "Без заголовка")
                        print(f"   {i}. {title[:80]}...")
                    print("   ✅ GDELT API работает корректно")
                else:
                    print("   ℹ️ Новости не найдены (нормально для некоторых тикеров)")
                    
            except Exception as e:
                print(f"   ⚠️ Ошибка парсинга JSON: {e}")
        else:
            print(f"   ❌ Ошибка HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Ошибка подключения: {e}")

def show_setup_instructions():
    """Показывает инструкции по настройке NewsAPI"""
    
    print(f"\n🛠️ НАСТРОЙКА NEWSAPI (ОПЦИОНАЛЬНО)")
    print("-" * 50)
    
    print("📋 Для получения большего количества новостей:")
    print("   1. Зарегистрируйтесь на https://newsapi.org/")
    print("   2. Получите бесплатный API ключ")
    print("   3. Добавьте в .env файл:")
    print("      NEWSAPI_KEY=ваш_ключ_здесь")
    print("   4. Перезапустите тест")
    
    print(f"\n💡 БЕЗ NEWSAPI:")
    print("   • Используется только GDELT Project")
    print("   • Бесплатно и без ограничений")
    print("   • Может быть достаточно для многих случаев")

if __name__ == "__main__":
    test_english_news()
    test_gdelt_specifically()
    show_setup_instructions()
