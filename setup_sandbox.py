
import os
from dotenv import load_dotenv
from tinkoff.invest import Client, SandboxService
from tinkoff.invest.sandbox.client import SandboxClient

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
        with SandboxClient(token) as client:
            # Получаем список аккаунтов
            accounts = client.users.get_accounts()
            
            if not accounts.accounts:
                # Если аккаунтов нет, открываем новый
                print("Открываем новый песочный счёт...")
                account = client.sandbox.open_sandbox_account()
                account_id = account.account_id
                print(f"Создан новый аккаунт: {account_id}")
            else:
                # Используем первый доступный аккаунт
                account_id = accounts.accounts[0].id
                print(f"Используем существующий аккаунт: {account_id}")
            
            # Пополняем счёт на 100 000 рублей
            print("Пополняем счёт на 100 000 ₽...")
            client.sandbox.sandbox_pay_in(
                account_id=account_id,
                amount={
                    'currency': 'rub',
                    'units': 100000,
                    'nano': 0
                }
            )
            
            # Получаем и выводим баланс портфеля
            portfolio = client.operations.get_portfolio(account_id=account_id)
            
            print("\n=== Баланс портфеля ===")
            
            # Общая стоимость портфеля
            total_amount = portfolio.total_amount_portfolio
            print(f"Общая стоимость портфеля: {total_amount.units}.{total_amount.nano:09d} {total_amount.currency.upper()}")
            
            # Позиции по валютам
            if portfolio.positions:
                print("\nПозиции:")
                for position in portfolio.positions:
                    if position.instrument_type == 'currency':
                        balance = position.quantity
                        print(f"  {position.figi}: {balance.units}.{balance.nano:09d}")
            
            print("\nСкрипт успешно выполнен!")
            
    except Exception as e:
        print(f"Ошибка при работе с API: {e}")

if __name__ == "__main__":
    main()
