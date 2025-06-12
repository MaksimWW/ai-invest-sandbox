#!/usr/bin/env python
import os
from tinkoff.invest import SandboxClient, MoneyValue, AccountType

TOKEN = os.getenv("TINKOFF_SANDBOX_TOKEN")
START_CAPITAL = 100_000  # ₽

def to_money(amount: int) -> MoneyValue:
    return MoneyValue(units=amount, nano=0, currency="rub")

def main():
    if not TOKEN:
        raise RuntimeError("❌ Переменная TINKOFF_SANDBOX_TOKEN не найдена!")
    with SandboxClient(TOKEN, app_name="ai-trader") as client:
        acc = client.open_sandbox_account(
            account_type=AccountType.ACCOUNT_TYPE_UNSPECIFIED
        ).account_id
        print("Sandbox account:", acc)

        client.sandbox_pay_in(
            account_id=acc,
            amount=to_money(START_CAPITAL),
        )
        bal = client.get_portfolio(account_id=acc).total_amount_portfolio
        print(f"Balance after pay-in: {bal.units} {bal.currency}")

if __name__ == "__main__":
    main()