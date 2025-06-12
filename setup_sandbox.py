
<old_str>import os
from dotenv import load_dotenv
from tinkoff.invest import Client, AccountType, MoneyValue

def to_money(amount: int) -> MoneyValue:
    return MoneyValue(units=amount, nano=0, currency="rub")

def main():
    # Загружаем переменные окружения из .env файла
    load_dotenv()

    # Получаем токен из переменной окружения
    token = os.getenv('TINKOFF_SANDBOX_TOKEN')

    if not token:
        print("Ошибка: переменная окружения TINKOFF_SANDBOX_TOKEN не найдена!")
        print("Создайте файл .env и добавьте в него:")
        print("TINKOFF_SANDBOX_TOKEN=ваш_токен_здесь")
        return

    try:
        # Создаем клиент для песочницы
        with Client(token, sandbox_token=token) as client:
            # Получаем список аккаунтов
            accounts = client.users.get_accounts()

            # Ищем песочный аккаунт
            sandbox_account_id = None
            for account in accounts.accounts:
                if account.type == AccountType.ACCOUNT_TYPE_TINKOFF_IIS_SANDBOX:
                    sandbox_account_id = account.id
                    break

            if not sandbox_account_id:
                # Если песочного аккаунта нет, открываем новый
                account = client.sandbox.open_sandbox_account()
                sandbox_account_id = account.account_id

            # Пополняем счёт на 100 000 рублей
            client.sandbox.sandbox_pay_in(
                account_id=sandbox_account_id,
                amount=to_money(100000)
            )

            # Выводим результат
            print(f"Sandbox account: {sandbox_account_id}")
            print("Balance after pay-in: 100000 RUB")

    except Exception as e:
        print(f"Ошибка при работе с API: {e}")

if __name__ == "__main__":
    main()</old_str>
<new_str>#!/usr/bin/env python
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
    main()</new_str>
