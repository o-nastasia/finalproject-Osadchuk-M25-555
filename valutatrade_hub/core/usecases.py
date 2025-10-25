#!/usr/bin/env python3
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import json
from .models import User, Wallet, Portfolio
from .utils import (
    get_user_by_id, get_user_by_username, save_user,
    get_portfolio_by_user_id, save_portfolio, get_rates,
    is_rate_fresh
)

class UseCases:
    @staticmethod
    def register(username: str, password: str) -> str:
        """Регистрация нового пользователя."""
        if not username.strip():
            return "Имя пользователя не может быть пустым"
        if len(password) < 4:
            return "Пароль должен быть не короче 4 символов"

        # Проверка уникальности username
        if get_user_by_username(username):
            return f"Имя пользователя '{username}' уже занято"

        # Генерация user_id
        try:
            with open('data/users.json', 'r') as f:
                users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            users = []
        user_id = max([u['user_id'] for u in users], default=0) + 1

        # Создание пользователя
        user = User(user_id, username, password)
        save_user(user.to_json())

        # Создание пустого портфеля
        portfolio = Portfolio(user_id)
        save_portfolio(portfolio.to_json())

        return f"Пользователь '{username}' зарегистрирован (id={user_id}). Войдите: login --username {username} --password ****"

    @staticmethod
    def login(username: str, password: str) -> tuple[Optional[User], str]:
        """Вход пользователя в систему."""
        user_data = get_user_by_username(username)
        if not user_data:
            return None, f"Пользователь '{username}' не найден"

        user = User(
            user_data['user_id'],
            user_data['username'],
            user_data['hashed_password']  # Передаем хеш, чтобы не пересоздавать
        )
        user._salt = user_data['salt']  # Устанавливаем соль
        user._hashed_password = user_data['hashed_password']  # Устанавливаем хеш
        user._registration_date = datetime.fromisoformat(user_data['registration_date'])

        if not user.verify_password(password):
            return None, "Неверный пароль"

        return user, f"Вы вошли как '{username}'"

    @staticmethod
    def show_portfolio(user_id: int, base_currency: str = 'USD') -> str:
        """Отображение портфеля пользователя."""
        portfolio_data = get_portfolio_by_user_id(user_id)
        if not portfolio_data:
            return "Портфель не найден"

        portfolio = Portfolio(user_id)
        for currency_code, wallet_data in portfolio_data['wallets'].items():
            portfolio.add_currency(currency_code)
            wallet = portfolio.get_wallet(currency_code)
            if wallet:
                wallet.balance = wallet_data['balance']

        if not portfolio.wallets:
            return "У вас нет кошельков"

        rates = get_rates()
        if base_currency not in rates and base_currency != 'USD':
            return f"Неизвестная базовая валюта '{base_currency}'"

        result = [f"Портфель пользователя '{portfolio.user.username}' (база: {base_currency}):"]
        total_value = 0.0
        for currency, wallet in portfolio.wallets.items():
            balance = wallet.balance
            rate = rates.get(f"{currency}_{base_currency}", {}).get('rate', None)
            if rate is None and currency != base_currency:
                return f"Не удалось получить курс для {currency}→{base_currency}"
            value = balance if currency == base_currency else balance * rate
            total_value += value
            result.append(f"- {currency}: {balance:.2f} → {value:.2f} {base_currency}")
        result.append("-" * 35)
        result.append(f"ИТОГО: {total_value:.2f} {base_currency}")

        return "\n".join(result)

    @staticmethod
    def buy(user_id: int, currency: str, amount: float) -> str:
        """Покупка валюты."""
        if not isinstance(amount, (int, float)) or amount <= 0:
            return "'amount' должен быть положительным числом"

        portfolio_data = get_portfolio_by_user_id(user_id)
        if not portfolio_data:
            return "Портфель не найден"

        portfolio = Portfolio(user_id)
        for currency_code, wallet_data in portfolio_data['wallets'].items():
            portfolio.add_currency(currency_code)
            wallet = portfolio.get_wallet(currency_code)
            if wallet:
                wallet.balance = wallet_data['balance']

        # Получаем курс
        rates = get_rates()
        rate_key = f"{currency}_USD"
        rate = rates.get(rate_key, {}).get('rate', None)
        if rate is None:
            return f"Не удалось получить курс для {currency}→USD"

        # Проверяем USD-кошелёк
        usd_wallet = portfolio.get_wallet('USD')
        if not usd_wallet:
            portfolio.add_currency('USD')
            usd_wallet = portfolio.get_wallet('USD')
        cost = amount * rate
        if usd_wallet.balance < cost:
            return f"Недостаточно средств: доступно {usd_wallet.balance:.2f} USD, требуется {cost:.2f} USD"

        # Создаем кошелек для валюты, если его нет
        portfolio.add_currency(currency)
        wallet = portfolio.get_wallet(currency)
        if not wallet:
            return f"Не удалось создать кошелек для валюты '{currency}'"

        # Выполняем списание с USD и пополнение целевой валюты
        if usd_wallet.withdraw(cost) and wallet.deposit(amount):
            save_portfolio(portfolio.to_json())
            return (f"Покупка выполнена: {amount:.4f} {currency} по курсу {rate:.2f} USD/{currency}\n"
                    f"Изменения в портфеле:\n"
                    f"- USD: было {usd_wallet.balance + cost:.4f} → стало {usd_wallet.balance:.4f}\n"
                    f"- {currency}: было {wallet.balance - amount:.4f} → стало {wallet.balance:.4f}\n"
                    f"Оценочная стоимость покупки: {cost:.2f} USD")
        return "Не удалось выполнить покупку"
    @staticmethod
    def sell(user_id: int, currency: str, amount: float) -> str:
        """Продажа валюты."""
        if not isinstance(amount, (int, float)) or amount <= 0:
            return "'amount' должен быть положительным числом"

        portfolio_data = get_portfolio_by_user_id(user_id)
        if not portfolio_data:
            return "Портфель не найден"

        portfolio = Portfolio(user_id)
        for currency_code, wallet_data in portfolio_data['wallets'].items():
            portfolio.add_currency(currency_code)
            wallet = portfolio.get_wallet(currency_code)
            if wallet:
                wallet.balance = wallet_data['balance']

        wallet = portfolio.get_wallet(currency)
        if not wallet:
            return f"У вас нет кошелька '{currency}'. Добавьте валюту: она создаётся автоматически при первой покупке."

        if wallet.balance < amount:
            return f"Недостаточно средств: доступно {wallet.balance:.4f} {currency}, требуется {amount:.4f} {currency}"

        # Получаем курс
        rates = get_rates()
        rate_key = f"{currency}_USD"
        rate = rates.get(rate_key, {}).get('rate', None)
        if rate is None:
            return f"Не удалось получить курс для {currency}→USD"

        # Снимаем средства
        if wallet.withdraw(amount):
            # Начисляем USD, если есть кошелек
            usd_wallet = portfolio.get_wallet('USD')
            if not usd_wallet:
                portfolio.add_currency('USD')
                usd_wallet = portfolio.get_wallet('USD')
            usd_wallet.deposit(amount * rate)

            save_portfolio(portfolio.to_json())
            revenue = amount * rate
            return (f"Продажа выполнена: {amount:.4f} {currency} по курсу {rate:.2f} USD/{currency}\n"
                    f"Изменения в портфеле:\n"
                    f"- {currency}: было {wallet.balance + amount:.4f} → стало {wallet.balance:.4f}\n"
                    f"Оценочная выручка: {revenue:.2f} USD")
        return "Не удалось выполнить продажу"

    @staticmethod
    def get_rate(from_currency: str, to_currency: str) -> str:
        """Получение курса валют."""
        if not from_currency.strip() or not to_currency.strip():
            return "Коды валют должны быть непустыми строками"

        from .utils import get_rates, update_rates_cache, is_rate_fresh  # Добавлен импорт update_rates_cache

        rates = get_rates()
        rate_key = f"{from_currency}_{to_currency}"
        rate_data = rates.get(rate_key, {})
        rate = rate_data.get('rate', None)
        updated_at = rate_data.get('updated_at', None)

        # Проверяем обратный курс, если прямой недоступен
        if rate is None:
            reverse_key = f"{to_currency}_{from_currency}"
            reverse_rate_data = rates.get(reverse_key, {})
            reverse_rate = reverse_rate_data.get('rate', None)
            reverse_updated_at = reverse_rate_data.get('updated_at', None)
            if reverse_rate is not None:
                rate = 1 / reverse_rate
                updated_at = reverse_updated_at

        # Если курс отсутствует или устарел, обновляем кеш
        if rate is None or not is_rate_fresh(updated_at):
            rates = update_rates_cache()
            rate_data = rates.get(rate_key, {})
            rate = rate_data.get('rate', None)
            updated_at = rate_data.get('updated_at', None)
            # Проверяем обратный курс после обновления кеша
            if rate is None:
                reverse_key = f"{to_currency}_{from_currency}"
                reverse_rate_data = rates.get(reverse_key, {})
                reverse_rate = reverse_rate_data.get('rate', None)
                reverse_updated_at = reverse_rate_data.get('updated_at', None)
                if reverse_rate is not None:
                    rate = 1 / reverse_rate
                    updated_at = reverse_updated_at

        if rate is None:
            return f"Курс {from_currency}→{to_currency} недоступен. Повторите попытку позже."

        return (f"Курс {from_currency}→{to_currency}: {rate:.8f} "
                f"(обновлено: {updated_at})\n"
                f"Обратный курс {to_currency}→{from_currency}: {1/rate:.8f}")
    
    @staticmethod
    def deposit(user_id: int, currency: str, amount: float) -> str:
        """Пополнение баланса кошелька."""
        if not isinstance(amount, (int, float)) or amount <= 0:
            return "'amount' должен быть положительным числом"

        portfolio_data = get_portfolio_by_user_id(user_id)
        if not portfolio_data:
            return "Портфель не найден"

        portfolio = Portfolio(user_id)
        for currency_code, wallet_data in portfolio_data['wallets'].items():
            portfolio.add_currency(currency_code)
            wallet = portfolio.get_wallet(currency_code)
            if wallet:
                wallet.balance = wallet_data['balance']

        portfolio.add_currency(currency)
        wallet = portfolio.get_wallet(currency)
        if not wallet:
            return f"Не удалось создать кошелек для валюты '{currency}'"

        if wallet.deposit(amount):
            save_portfolio(portfolio.to_json())
            return f"Пополнение выполнено: {amount:.2f} {currency} добавлено к кошельку"
        return "Не удалось выполнить пополнение"