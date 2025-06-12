
#!/usr/bin/env python
import os
from tinkoff.invest import Client, MoneyValue

TOKEN = os.getenv("TINKOFF_SANDBOX_TOKEN")
START_CAPITAL = 100_000  # ₽

def to_money(amount: int) -> MoneyValue:
    return MoneyValue(units=amount, nano=0, currency="rub")

def main():
    if not TOKEN:
        raise RuntimeError("❌ Переменная TINKOFF_SANDBOX_TOKEN не найдена!")
    
    with Client(TOKEN, app_name="ai-trader") as client:
        # Открываем песочный аккаунт
        acc = client.sandbox.open_sandbox_account().account_id
        print("Sandbox account:", acc)

        # Пополняем счёт
        client.sandbox.sandbox_pay_in(
            account_id=acc,
            amount=to_money(START_CAPITAL),
        )
        
        # Получаем баланс через sandbox service
        portfolio = client.sandbox.get_sandbox_portfolio(account_id=acc)
        bal = portfolio.total_amount_portfolio
        print(f"Balance after pay-in: {bal.units} {bal.currency}")

if __name__ == "__main__":
    main()
