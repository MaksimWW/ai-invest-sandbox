
#!/usr/bin/env python
import os
import pandas as pd
from datetime import datetime, timedelta
from tinkoff.invest import Client, CandleInterval

# Переменные окружения
TINKOFF_SANDBOX_TOKEN = os.getenv("TINKOFF_SANDBOX_TOKEN")

def get_candles(figi, interval='hour', count=200):
    """Получает исторические свечи для анализа"""
    if not TINKOFF_SANDBOX_TOKEN:
        raise RuntimeError("❌ Переменная TINKOFF_SANDBOX_TOKEN не найдена!")
    
    # Определяем интервал для API
    interval_map = {
        'minute': CandleInterval.CANDLE_INTERVAL_1_MIN,
        'hour': CandleInterval.CANDLE_INTERVAL_HOUR,
        'day': CandleInterval.CANDLE_INTERVAL_DAY
    }
    
    api_interval = interval_map.get(interval, CandleInterval.CANDLE_INTERVAL_HOUR)
    
    # Рассчитываем временной диапазон
    end_time = datetime.now()
    if interval == 'minute':
        start_time = end_time - timedelta(minutes=count)
    elif interval == 'hour':
        start_time = end_time - timedelta(hours=count)
    else:  # day
        start_time = end_time - timedelta(days=count)
    
    with Client(TINKOFF_SANDBOX_TOKEN, app_name="sma-signal") as client:
        try:
            response = client.market_data.get_candles(
                figi=figi,
                from_=start_time,
                to=end_time,
                interval=api_interval
            )
            
            # Преобразуем в DataFrame
            candles_data = []
            for candle in response.candles:
                close_price = candle.close.units + candle.close.nano / 1_000_000_000
                candles_data.append({
                    'time': candle.time.replace(tzinfo=None),
                    'close': close_price
                })
            
            df = pd.DataFrame(candles_data)
            if len(df) > 0:
                df = df.sort_values('time').reset_index(drop=True)
            
            return df
            
        except Exception as e:
            print(f"❌ Ошибка получения свечей для {figi}: {e}")
            return pd.DataFrame()

def calculate_sma(df, period):
    """Вычисляет простую скользящую среднюю"""
    if len(df) < period:
        return pd.Series([None] * len(df))
    return df['close'].rolling(window=period).mean()

def generate_signal(figi, interval='hour'):
    """
    Генерирует сигнал на основе пересечения SMA20 и SMA50
    
    Returns:
        str: 'BUY' если SMA20 пересекла SMA50 снизу вверх на последней свече
             'SELL' если SMA20 пересекла SMA50 сверху вниз на последней свече
             'HOLD' в остальных случаях
    """
    try:
        # Получаем свечи
        df = get_candles(figi, interval, 200)
        
        if len(df) < 50:
            return "HOLD"  # Недостаточно данных
        
        # Вычисляем SMA
        df['sma20'] = calculate_sma(df, 20)
        df['sma50'] = calculate_sma(df, 50)
        
        # Удаляем строки с NaN значениями
        df = df.dropna()
        
        if len(df) < 2:
            return "HOLD"  # Недостаточно данных после очистки
        
        # Проверяем пересечение на последней свече
        last_idx = len(df) - 1
        prev_idx = last_idx - 1
        
        # Текущие значения SMA
        current_sma20 = df.iloc[last_idx]['sma20']
        current_sma50 = df.iloc[last_idx]['sma50']
        
        # Предыдущие значения SMA
        prev_sma20 = df.iloc[prev_idx]['sma20']
        prev_sma50 = df.iloc[prev_idx]['sma50']
        
        # Проверяем пересечение
        # BUY: SMA20 была ниже SMA50, теперь выше
        if prev_sma20 <= prev_sma50 and current_sma20 > current_sma50:
            return "BUY"
        
        # SELL: SMA20 была выше SMA50, теперь ниже
        elif prev_sma20 >= prev_sma50 and current_sma20 < current_sma50:
            return "SELL"
        
        else:
            return "HOLD"
            
    except Exception as e:
        print(f"❌ Ошибка генерации сигнала для {figi}: {e}")
        return "HOLD"
