#!/usr/bin/env python3
from typing import Optional, Dict, Any
from ..infra.database import DatabaseManager
from .currencies import get_currency
from .exceptions import CurrencyNotFoundError
from datetime import datetime

def get_user_by_id(user_id: int):
    from .models import User
    db = DatabaseManager()
    user_data = db.get_user_by_id(user_id)
    if user_data:
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
    db = DatabaseManager()
    return db.get_user_by_username(username)

def save_user(user_data: Dict[str, Any]) -> None:
    db = DatabaseManager()
    db.save_user(user_data)

def get_portfolio_by_user_id(user_id: int) -> Optional[Dict[str, Any]]:
    db = DatabaseManager()
    return db.get_portfolio_by_user_id(user_id)

def save_portfolio(portfolio_data: Dict[str, Any]) -> None:
    db = DatabaseManager()
    db.save_portfolio(portfolio_data)

def get_rates() -> Dict[str, Any]:
    db = DatabaseManager()
    return db.get_rates()

def update_rates_cache() -> Dict[str, Any]:
    db = DatabaseManager()
    return db.update_rates_cache()

def is_rate_fresh(updated_at: str) -> bool:
    db = DatabaseManager()
    return db._is_rate_fresh(updated_at)

def validate_currency_code(code: str) -> str:
    try:
        currency = get_currency(code)
        return currency.code
    except CurrencyNotFoundError as e:
        raise CurrencyNotFoundError(e.message)