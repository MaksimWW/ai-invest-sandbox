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
        '1min': CandleInterval.CANDLE_INTERVAL_1_MIN,
        '5min': CandleInterval.CANDLE_INTERVAL_5_MIN,
        '15min': CandleInterval.CANDLE_INTERVAL_15_MIN,
        '30min': CandleInterval.CANDLE_INTERVAL_30_MIN,
        'hour': CandleInterval.CANDLE_INTERVAL_HOUR,
        'day': CandleInterval.CANDLE_INTERVAL_DAY
    }

    api_interval = interval_map.get(interval)
    if api_interval is None:
        raise ValueError(f"Неподдерживаемый интервал: {interval}. Доступные: {list(interval_map.keys())}")

    # Рассчитываем временной диапазон
    end_time = datetime.now()
    if interval in ['minute', '1min']:
        start_time = end_time - timedelta(minutes=count)
    elif interval == '5min':
        start_time = end_time - timedelta(minutes=count * 5)
    elif interval == '15min':
        start_time = end_time - timedelta(minutes=count * 15)
    elif interval == '30min':
        start_time = end_time - timedelta(minutes=count * 30)
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
            error_msg = str(e)
            if "30014" in error_msg and "maximum request period" in error_msg:
                # Уменьшаем период запроса для данного интервала
                if interval == '15min' and count > 50:
                    print(f"Слишком большой период для {interval}. Повторяем с меньшим количеством свечей...")
                    return get_candles(figi, interval, 50)
                elif interval in ['5min', '1min'] and count > 100:
                    print(f"Слишком большой период для {interval}. Повторяем с меньшим количеством свечей...")
                    return get_candles(figi, interval, 100)
                else:
                    print(f"Ошибка периода запроса для {figi} ({interval}): API не поддерживает запрос такого количества свечей")
            else:
                print(f"Ошибка получения свечей для {figi}: {e}")
            return pd.DataFrame()

def calculate_sma(df, period):
    """Вычисляет простую скользящую среднюю"""
    if len(df) < period:
        return pd.Series([None] * len(df))
    return df['close'].rolling(window=period).mean()

def calculate_atr(df, period=14):
    """Вычисляет Average True Range (ATR)"""
    if len(df) < 2:
        return pd.Series([None] * len(df))

    # Для ATR нужны high, low, close. Используем close как приближение
    # В реальной реализации нужны данные OHLC
    df['prev_close'] = df['close'].shift(1)
    df['tr'] = df['close'] - df['prev_close']  # Упрощенная версия TR
    df['tr'] = df['tr'].abs()  # Берем абсолютное значение

    # Вычисляем ATR как SMA от True Range
    atr = df['tr'].rolling(window=period).mean()
    return atr

def generate_signal(figi, interval='hour', fast=20, slow=50, atr_ratio=1.0):
    """
    Генерирует сигнал на основе пересечения SMA и фильтра волатильности ATR

    Args:
        figi: FIGI инструмента
        interval: Интервал свечей ('hour', 'day', 'minute')
        fast: Период быстрой SMA (по умолчанию 20)
        slow: Период медленной SMA (по умолчанию 50)
        atr_ratio: Минимальный коэффициент ATR для срабатывания сигнала

    Returns:
        str: 'BUY' если SMA_fast пересекла SMA_slow снизу вверх + ATR фильтр
             'SELL' если SMA_fast пересекла SMA_slow сверху вниз + ATR фильтр
             'HOLD' в остальных случаях
    """
    try:
        # Получаем свечи
        df = get_candles(figi, interval, 200)

        if len(df) < slow:
            return "HOLD"  # Недостаточно данных

        # Вычисляем SMA
        df[f'sma{fast}'] = calculate_sma(df, fast)
        df[f'sma{slow}'] = calculate_sma(df, slow)

        # Вычисляем ATR
        df['atr'] = calculate_atr(df, slow)
        df['avg_atr'] = df['atr'].rolling(window=slow).mean()

        # Удаляем строки с NaN значениями
        df = df.dropna()

        if len(df) < 2:
            return "HOLD"  # Недостаточно данных после очистки

        # Проверяем пересечение на последней свече
        last_idx = len(df) - 1
        prev_idx = last_idx - 1

        # Текущие значения SMA
        current_sma_fast = df.iloc[last_idx][f'sma{fast}']
        current_sma_slow = df.iloc[last_idx][f'sma{slow}']

        # Предыдущие значения SMA
        prev_sma_fast = df.iloc[prev_idx][f'sma{fast}']
        prev_sma_slow = df.iloc[prev_idx][f'sma{slow}']

        # Проверяем ATR фильтр
        current_atr = df.iloc[last_idx]['atr']
        avg_atr = df.iloc[last_idx]['avg_atr']

        # ATR фильтр: текущая волатильность должна быть достаточной
        atr_filter_passed = (current_atr >= atr_ratio * avg_atr) if avg_atr > 0 else True

        # Проверяем пересечения с учетом ATR фильтра
        if (prev_sma_fast <= prev_sma_slow and 
            current_sma_fast > current_sma_slow and 
            atr_filter_passed):
            return "BUY"  # Пересечение снизу вверх + достаточная волатильность
        elif (prev_sma_fast >= prev_sma_slow and 
              current_sma_fast < current_sma_slow and 
              atr_filter_passed):
            return "SELL"  # Пересечение сверху вниз + достаточная волатильность
        else:
            return "HOLD"  # Нет пересечения или недостаточная волатильность

    except Exception as e:
        print(f"Ошибка генерации сигнала для {figi}: {e}")
        return "HOLD"

def _debug_last_values(figi, interval="hour", fast=20, slow=50):
    """
    Только для отладки. Возвращает два последних набора:
    (close, sma_fast, sma_slow)
    """
    df = get_candles(figi, interval, slow * 3)        # большой запас свечей
    sma_fast = df['close'].rolling(fast).mean()
    sma_slow = df['close'].rolling(slow).mean()
    # не трогаем основную логику generate_signal!
    sma_fast = sma_fast.dropna()
    sma_slow = sma_slow.dropna()
    tail_len = min(len(sma_fast), len(sma_slow), 2)
    return list(zip(df['close'].tail(tail_len),
                    sma_fast.tail(tail_len),
                    sma_slow.tail(tail_len)))