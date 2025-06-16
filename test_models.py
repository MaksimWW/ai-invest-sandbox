
#!/usr/bin/env python
"""
Тест доступности моделей Hugging Face
"""

def test_model_availability():
    """Проверяет доступность моделей"""
    print("🔍 ПРОВЕРКА ДОСТУПНОСТИ МОДЕЛЕЙ")
    print("=" * 50)
    
    models_to_test = [
        "sismetanin/rubert-rusentiment",
        "cardiffnlp/twitter-roberta-base-sentiment-latest", 
        "ProsusAI/finbert",
        "blanchefort/rubert-base-cased-sentiment"
    ]
    
    for model_name in models_to_test:
        print(f"\n📦 Тестируем модель: {model_name}")
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            
            # Попробуем загрузить токенизатор
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            print(f"✅ Токенизатор загружен успешно")
            
            # Попробуем загрузить модель
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            print(f"✅ Модель загружена успешно")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            continue

if __name__ == "__main__":
    test_model_availability()
