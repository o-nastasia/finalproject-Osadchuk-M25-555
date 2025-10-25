#!/usr/bin/env python3
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import os

DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

def get_user_by_id(user_id: int):
    from .models import User
    users_file = os.path.join(DATA_DIR, 'users.json')
    try:
        with open(users_file, 'r') as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(users_file, 'w') as f:
            json.dump([], f, indent=2)
        users = []
    for user_data in users:
        if user_data['user_id'] == user_id:
            user = User(
                user_id=user_data['user_id'],
                username=user_data['username'],
                password=user_data['hashed_password']
            )
            user._salt = user_data['salt']
            user._hashed_password = user_data['hashed_password']
            user._registration_date = datetime.fromisoformat(user_data['registration_date'])
            return user
    return None

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    users_file = os.path.join(DATA_DIR, 'users.json')
    try:
        with open(users_file, 'r') as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(users_file, 'w') as f:
            json.dump([], f, indent=2)
        users = []
    for user_data in users:
        if user_data['username'] == username:
            return user_data
    return None

def save_user(user_data: Dict[str, Any]) -> None:
    users_file = os.path.join(DATA_DIR, 'users.json')
    try:
        try:
            with open(users_file, 'r') as f:
                users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            users = []
        users.append(user_data)
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        print(f"Предупреждение: Не удалось сохранить пользователя: {str(e)}")

def get_portfolio_by_user_id(user_id: int) -> Optional[Dict[str, Any]]:
    portfolios_file = os.path.join(DATA_DIR, 'portfolios.json')
    try:
        with open(portfolios_file, 'r') as f:
            portfolios = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):

        with open(portfolios_file, 'w') as f:
            json.dump([], f, indent=2)
        portfolios = []
    for portfolio in portfolios:
        if portfolio['user_id'] == user_id:
            return portfolio
    return None

def save_portfolio(portfolio_data: Dict[str, Any]) -> None:
    portfolios_file = os.path.join(DATA_DIR, 'portfolios.json')
    try:
        try:
            with open(portfolios_file, 'r') as f:
                portfolios = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            portfolios = []
        for i, portfolio in enumerate(portfolios):
            if portfolio['user_id'] == portfolio_data['user_id']:
                portfolios[i] = portfolio_data
                break
        else:
            portfolios.append(portfolio_data)
        with open(portfolios_file, 'w') as f:
            json.dump(portfolios, f, indent=2)
    except Exception as e:
        print(f"Предупреждение: Не удалось сохранить портфель: {str(e)}")

def update_rates_cache() -> Dict[str, Any]:
    current_time = datetime.now().isoformat()
    default_rates = {
        "EUR_USD": {"rate": 1.0786, "updated_at": current_time},
        "BTC_USD": {"rate": 59337.21, "updated_at": current_time},
        "RUB_USD": {"rate": 0.01016, "updated_at": current_time},
        "ETH_USD": {"rate": 3720.00, "updated_at": current_time},
        "USD_BTC": {"rate": 1 / 59337.21, "updated_at": current_time},
        "USD_EUR": {"rate": 1 / 1.0786, "updated_at": current_time},
        "USD_RUB": {"rate": 1 / 0.01016, "updated_at": current_time},
        "USD_ETH": {"rate": 1 / 3720.00, "updated_at": current_time},
        "source": "ParserService",
        "last_refresh": current_time
    }
    rates_file = os.path.join(DATA_DIR, 'rates.json')
    try:
        with open(rates_file, 'w') as f:
            json.dump(default_rates, f, indent=2)
    except Exception as e:
        print(f"Предупреждение: Не удалось обновить кеш курсов: {str(e)}")
    return default_rates

def get_rates() -> Dict[str, Any]:
    """Получает курсы валют из rates.json или обновляет кеш, если файл отсутствует."""
    rates_file = os.path.join(DATA_DIR, 'rates.json')
    try:
        with open(rates_file, 'r') as f:
            rates = json.load(f)
        last_refresh = rates.get('last_refresh')
        if not last_refresh or not is_rate_fresh(last_refresh):
            return update_rates_cache()
        return rates
    except (FileNotFoundError, json.JSONDecodeError):
        return update_rates_cache()

def is_rate_fresh(updated_at: str) -> bool:
    try:
        updated_time = datetime.fromisoformat(updated_at)
        return datetime.now() - updated_time < timedelta(minutes=5)
    except (ValueError, TypeError):
        return False