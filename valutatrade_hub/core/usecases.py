#!/usr/bin/env python3
from datetime import datetime
from typing import Optional

from ..decorators import log_action
from .exceptions import ApiRequestError, CurrencyNotFoundError, InsufficientFundsError
from .models import Portfolio, User
from .utils import (
    get_portfolio_by_user_id,
    get_rates,
    get_user_by_username,
    save_portfolio,
    save_user,
    validate_currency_code,
)


class UseCases:
    @staticmethod
    @log_action(verbose=True)
    def register(username: str, password: str) -> str:
        """Регистрирует нового пользователя."""
        if not username.strip():
            return "Имя пользователя не может быть пустым"
        if len(password) < 4:
            return "Пароль должен быть не короче 4 символов"
        if get_user_by_username(username):
            return f"Имя пользователя '{username}' уже занято"

        from ..infra.database import DatabaseManager
        db = DatabaseManager()
        users = db._read_json('users.json')
        user_id = max([u['user_id'] for u in users], default=0) + 1

        user = User(user_id, username, password)
        save_user(user.to_json())

        portfolio = Portfolio(user_id)
        save_portfolio(portfolio.to_json())

        return f"Пользователь '{username}' зарегистрирован (id={user_id}). Войдите: login --username {username} --password ****"#noqa: E501

    @staticmethod
    @log_action()
    def login(username: str, password: str) -> tuple[Optional[User], str]:
        """Авторизует пользователя."""
        user_data = get_user_by_username(username)
        if not user_data:
            return None, f"Пользователь '{username}' не найден."

        user = User(
            user_data['user_id'],
            user_data['username'],
            user_data['hashed_password']
        )
        user._salt = user_data['salt']
        user._hashed_password = user_data['hashed_password']
        user._registration_date = datetime.fromisoformat(user_data['registration_date'])

        if not user.verify_password(password):
            return None, "Неверный пароль."

        return user, f"Вы вошли как '{username}'"

    @staticmethod
    def show_portfolio(user_id: int, base_currency: str = 'USD') -> str:
        """Показывает портфель пользователя."""
        try:
            validate_currency_code(base_currency)
        except CurrencyNotFoundError as e:
            return f"Ошибка: {e.message}."

        portfolio_data = get_portfolio_by_user_id(user_id)
        if not portfolio_data:
            return "Портфель не найден."

        portfolio = Portfolio(user_id)
        for currency_code, wallet_data in portfolio_data['wallets'].items():
            portfolio.add_currency(currency_code)
            wallet = portfolio.get_wallet(currency_code)
            if wallet:
                wallet.balance = wallet_data['balance']

        if not portfolio.wallets:
            return "У вас нет кошельков."

        rates = get_rates()
        if base_currency not in rates and base_currency != 'USD':
            return f"Неизвестная базовая валюта '{base_currency}'"

        result = [f"Портфель пользователя '{portfolio.user.username}' (база: {base_currency}):"]#noqa: E501
        total_value = 0.0
        for currency, wallet in portfolio.wallets.items():
            balance = wallet.balance
            rate = rates.get(f"{currency}_{base_currency}", {}).get('rate', None)
            if rate is None and currency != base_currency:
                return f"Не удалось получить курс для {currency}→{base_currency}. Повторите позже."#noqa: E501
            value = balance if currency == base_currency else balance * rate
            total_value += value
            result.append(f"- {currency}: {balance:.2f} → {value:.2f} {base_currency}")
        result.append("-" * 35)
        result.append(f"ИТОГО: {total_value:.2f} {base_currency}")

        return "\n".join(result)

    @staticmethod
    @log_action(verbose=True)
    def buy(user_id: int, currency: str, amount: float) -> str:
        """Покупает валюту для пользователя."""
        if not isinstance(amount, (int, float)) or amount <= 0:
            return "Сумма должна быть положительным числом."
        try:
            validate_currency_code(currency)
        except CurrencyNotFoundError as e:
            return f"Ошибка: {e.message}."

        portfolio_data = get_portfolio_by_user_id(user_id)
        if not portfolio_data:
            return "Портфель не найден"

        portfolio = Portfolio(user_id)
        for currency_code, wallet_data in portfolio_data['wallets'].items():
            portfolio.add_currency(currency_code)
            wallet = portfolio.get_wallet(currency_code)
            if wallet:
                wallet.balance = wallet_data['balance']

        rates = get_rates()
        rate_key = f"{currency}_USD"
        rate = rates.get(rate_key, {}).get('rate', None)
        if rate is None:
            return f"Не удалось получить курс для {currency}→USD. Повторите позже."

        usd_wallet = portfolio.get_wallet('USD')
        if not usd_wallet:
            portfolio.add_currency('USD')
            usd_wallet = portfolio.get_wallet('USD')
        cost = amount * rate
        try:
            usd_wallet.withdraw(cost)
        except InsufficientFundsError as e:
            return f"Ошибка: {e.message}"

        portfolio.add_currency(currency)
        wallet = portfolio.get_wallet(currency)
        if not wallet:
            return f"Не удалось создать кошелек для валюты '{currency}.'"

        if wallet.deposit(amount):
            save_portfolio(portfolio.to_json())
            return (f"Покупка выполнена: {amount:.4f} {currency} по курсу {rate:.2f} USD/{currency}\n"#noqa: E501
                    f"Изменения в портфеле:\n"
                    f"- USD: было {usd_wallet.balance + cost:.2f} → стало {usd_wallet.balance:.2f}\n"#noqa: E501
                    f"- {currency}: было {wallet.balance - amount:.4f} → стало {wallet.balance:.4f}\n"#noqa: E501
                    f"Оценочная стоимость покупки: {cost:.2f} USD")
        return "Не удалось выполнить покупку."

    @staticmethod
    @log_action(verbose=True)
    def sell(user_id: int, currency: str, amount: float) -> str:
        """Продаёт валюту пользователя."""
        if not isinstance(amount, (int, float)) or amount <= 0:
            return "Сумма должна быть положительным числом"
        try:
            validate_currency_code(currency)
        except CurrencyNotFoundError as e:
            return f"Ошибка: {e.message}."

        portfolio_data = get_portfolio_by_user_id(user_id)
        if not portfolio_data:
            return "Портфель не найден."

        portfolio = Portfolio(user_id)
        for currency_code, wallet_data in portfolio_data['wallets'].items():
            portfolio.add_currency(currency_code)
            wallet = portfolio.get_wallet(currency_code)
            if wallet:
                wallet.balance = wallet_data['balance']

        wallet = portfolio.get_wallet(currency)
        if not wallet:
            return f"У вас нет кошелька '{currency}'. Добавьте валюту: она создаётся автоматически при первой покупке."#noqa: E501

        try:
            wallet.withdraw(amount)
        except InsufficientFundsError as e:
            return f"Ошибка: {e.message}"

        rates = get_rates()
        rate_key = f"{currency}_USD"
        rate = rates.get(rate_key, {}).get('rate', None)
        if rate is None:
            return f"Не удалось получить курс для {currency}→USD. Повторите позже."

        usd_wallet = portfolio.get_wallet('USD')
        if not usd_wallet:
            portfolio.add_currency('USD')
            usd_wallet = portfolio.get_wallet('USD')
        usd_wallet.deposit(amount * rate)

        save_portfolio(portfolio.to_json())
        revenue = amount * rate
        return (f"Продажа выполнена: {amount:.4f} {currency} по курсу {rate:.2f} USD/{currency}\n"#noqa: E501
                f"Изменения в портфеле:\n"
                f"- {currency}: было {wallet.balance + amount:.4f} → стало {wallet.balance:.4f}\n"#noqa: E501
                f"- USD: было {usd_wallet.balance - revenue:.4f} → стало {usd_wallet.balance:.2f}\n"#noqa: E501
                f"Оценочная выручка: {revenue:.2f} USD")

    @staticmethod
    @log_action()
    def get_rate(from_currency: str, to_currency: str) -> str:
        """Получает курс обмена между валютами."""
        try:
            validate_currency_code(from_currency)
            validate_currency_code(to_currency)
        except CurrencyNotFoundError as e:
            return f"Ошибка: {e.message}."

        from ..infra.database import DatabaseManager
        db = DatabaseManager()
        rates = db.get_rates()
        rate_key = f"{from_currency}_{to_currency}"
        rate_data = rates.get(rate_key, {})
        rate = rate_data.get('rate', None)
        updated_at = rate_data.get('updated_at', None)

        if rate is None:
            reverse_key = f"{to_currency}_{from_currency}"
            reverse_rate_data = rates.get(reverse_key, {})
            reverse_rate = reverse_rate_data.get('rate', None)
            reverse_updated_at = reverse_rate_data.get('updated_at', None)
            if reverse_rate is not None:
                rate = 1 / reverse_rate
                updated_at = reverse_updated_at

        if rate is None:
            raise ApiRequestError("Курс недоступен.")

        return (f"Курс {from_currency}→{to_currency}: {rate:.8f} "
                f"(обновлено: {updated_at})\n"
                f"Обратный курс {to_currency}→{from_currency}: {1/rate:.8f}")

    @staticmethod
    @log_action(verbose=True)
    def deposit(user_id: int, currency: str, amount: float) -> str:
        """Пополняет кошелёк пользователя."""
        if not isinstance(amount, (int, float)) or amount <= 0:
            return "Сумма должна быть положительным числом."
        try:
            validate_currency_code(currency)
        except CurrencyNotFoundError as e:
            return f"Ошибка: {e.message}."

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
            return f"Не удалось создать кошелек для валюты '{currency}'."

        if wallet.deposit(amount):
            save_portfolio(portfolio.to_json())
            return f"Пополнение выполнено: {amount:.2f} {currency} добавлено к кошельку."#noqa: E501
        return "Не удалось выполнить пополнение."