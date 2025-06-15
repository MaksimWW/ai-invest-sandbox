
#!/usr/bin/env python
"""
Тест RSS-источников новостей
"""

import sys
sys.path.append('.')
from nlp.ru_sentiment import latest_news, classify, RSS_FEEDS

def test_rss_sources():
    """Тестирует работу RSS-источников"""
    
    print("📰 ТЕСТ RSS-ИСТОЧНИКОВ НОВОСТЕЙ")
    print("=" * 50)
    
    print(f"🔗 Настроенные источники:")
    for i, url in enumerate(RSS_FEEDS, 1):
        print(f"   {i}. {url}")
    
    # Тестируем популярные тикеры
    test_tickers = ["YNDX", "SBER", "GAZP", "LKOH", "NVTK", "FXIT"]
    
    print(f"\n🔍 Ищем новости за последние 48 часов...")
    print("-" * 50)
    
    total_news = 0
    
    for ticker in test_tickers:
        print(f"\n📊 {ticker}:")
        
        try:
            news_list = latest_news(ticker, hours=48)
            
            if news_list:
                print(f"   ✅ Найдено {len(news_list)} новостей")
                total_news += len(news_list)
                
                # Показываем первые 3 новости
                for i, title in enumerate(news_list[:3], 1):
                    # Анализируем настроение
                    sentiment = classify(title)
                    emoji = {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}[sentiment]
                    
                    print(f"   {i}. {emoji} {sentiment.upper()}: {title[:100]}...")
                
                if len(news_list) > 3:
                    print(f"   ... и ещё {len(news_list) - 3} новостей")
            else:
                print(f"   ❌ Новостей не найдено")
                
        except Exception as e:
            print(f"   ⚠️ Ошибка: {e}")
    
    print(f"\n📈 ИТОГО:")
    print(f"   • Всего найдено новостей: {total_news}")
    print(f"   • Источников RSS: {len(RSS_FEEDS)}")
    
    if total_news > 0:
        print("   ✅ RSS-источники работают корректно!")
    else:
        print("   ⚠️ Новости не найдены - возможно, проблемы с источниками")

def test_individual_sources():
    """Тестирует каждый источник отдельно"""
    
    print(f"\n🔍 ДЕТАЛЬНЫЙ ТЕСТ ИСТОЧНИКОВ")
    print("-" * 50)
    
    import requests
    
    for i, url in enumerate(RSS_FEEDS, 1):
        print(f"\n📡 Источник {i}: {url}")
        
        try:
            print("   📤 Запрашиваем RSS...")
            response = requests.get(url, timeout=10)
            
            print(f"   📊 HTTP Status: {response.status_code}")
            
            if response.status_code == 200:
                xml_content = response.text
                items_count = len(xml_content.split("<item>")) - 1
                print(f"   📰 Найдено новостных элементов: {items_count}")
                
                # Показываем первый заголовок как пример
                if items_count > 0:
                    first_item = xml_content.split("<item>")[1]
                    if "<title>" in first_item and "</title>" in first_item:
                        title = first_item.split("<title>")[1].split("</title>")[0]
                        print(f"   📝 Пример заголовка: {title[:100]}...")
                        print("   ✅ Источник работает корректно")
                    else:
                        print("   ⚠️ Проблема с парсингом заголовков")
                else:
                    print("   ⚠️ Новостных элементов не найдено")
            else:
                print(f"   ❌ Ошибка HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Ошибка подключения: {e}")

if __name__ == "__main__":
    test_rss_sources()
    test_individual_sources()
