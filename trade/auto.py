
#!/usr/bin/env python
"""
Автоматическая торговля при composite-score ≥ 3
"""
import os
import datetime as dt
import traceback
from tinkoff.invest import Client, LimitOrderRequest, OrderType, Quotation
from signals.composite import get_composite_score
from utils.sheets_logger import log_trade

# Конфигурация
ACCOUNT = os.getenv("TKS_SANDBOX_ACC")
TOKEN = os.getenv("TINKOFF_SANDBOX_TOKEN")
AUTO_ON = os.getenv("AUTO_TRADE", "0") == "1"
FIX_QTY = int(os.getenv("AUTO_QTY", "1"))

def auto_trade(figi: str, price_rub: float, ticker: str):
    """
    Автоматическая торговля на основе композитного скора
    
    Args:
        figi: FIGI код инструмента
        price_rub: Текущая цена в рублях
        ticker: Тикер инструмента
        
    Returns:
        tuple: (success: bool, message: str)
    """
    if not AUTO_ON:
        return False, "auto-off"
    
    if not ACCOUNT or not TOKEN:
        return False, "no-sandbox-account"
    
    score = get_composite_score(figi)
    if abs(score) < 3:
        return False, f"score={score}<3"
    
    # Определяем направление
    if score > 0:
        direction = LimitOrderRequest.LimitOrderDirection.LIMIT_ORDER_DIRECTION_BUY
        side_str = "BUY"
    else:
        direction = LimitOrderRequest.LimitOrderDirection.LIMIT_ORDER_DIRECTION_SELL
        side_str = "SELL"
    
    try:
        with Client(TOKEN, app_name="auto-trade") as c:
            # Размещаем лимитный ордер
            resp = c.sandbox.post_sandbox_order(
                account_id=ACCOUNT,
                figi=figi,
                price=Quotation(units=int(price_rub), nano=0),
                quantity=FIX_QTY,
                direction=direction,
                order_type=OrderType.ORDER_TYPE_LIMIT,
                order_id=f"auto-{dt.datetime.utcnow().timestamp():.0f}"
            )
            
        # Логируем в Google Sheets
        log_trade(
            date=dt.date.today(),
            ticker=ticker,
            figi=figi,
            side=side_str,
            price=price_rub,
            qty=FIX_QTY,
            fees=0.0
        )
        
        return True, f"orderId {resp.order_id}"
        
    except Exception as e:
        traceback.print_exc()
        return False, str(e)
