
#!/usr/bin/env python
"""
Композитный скор = техническая оценка + настроение новостей
"""
import os
from signals.sma_breakout import generate_signal
from daily_plan_bot import get_sentiment_score, FIGI_MAP

def get_composite_score(figi: str) -> int:
    """
    Возвращает композитный скор для инструмента
    
    Args:
        figi: FIGI код инструмента
        
    Returns:
        int: Композитный скор (-3 до +3)
    """
    # Находим тикер по FIGI
    ticker = None
    for t, f in FIGI_MAP.items():
        if f == figi:
            ticker = t
            break
    
    if not ticker:
        return 0
    
    try:
        # Техническая оценка
        signal = generate_signal(figi, interval='hour', fast=5, slow=15, atr_ratio=0)
        tech_score = 1 if signal == "BUY" else -1 if signal == "SELL" else 0
        
        # Настроение новостей (за 24 часа)
        news_score = get_sentiment_score(ticker, hours=24)
        
        # Ограничиваем диапазон новостного скора
        news_score = max(-2, min(2, news_score))
        
        composite = tech_score + news_score
        return composite
        
    except Exception as e:
        print(f"❌ Ошибка расчета композитного скора для {ticker}: {e}")
        return 0
