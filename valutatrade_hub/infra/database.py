#!/usr/bin/env python3
import json
import os
from typing import Dict, Any, Optional
from .settings import SettingsLoader

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._settings = SettingsLoader()
            cls._instance._data_dir = cls._instance._settings.get('data_dir', 'data')
            os.makedirs(cls._instance._data_dir, exist_ok=True)
        return cls._instance

    def _read_json(self, filename: str) -> list:
        file_path = os.path.join(self._data_dir, filename)
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(file_path, 'w') as f:
                json.dump([], f)
            return []

    def _write_json(self, filename: str, data: list) -> None:
        file_path = os.path.join(self._data_dir, filename)
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Предупреждение: Не удалось сохранить данные в {filename}: {str(e)}")

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        users = self._read_json('users.json')
        for user_data in users:
            if user_data['user_id'] == user_id:
                return user_data
        return None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        users = self._read_json('users.json')
        for user_data in users:
            if user_data['username'] == username:
                return user_data
        return None

    def save_user(self, user_data: Dict[str, Any]) -> None:
        users = self._read_json('users.json')
        users.append(user_data)
        self._write_json('users.json', users)

    def get_portfolio_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        portfolios = self._read_json('portfolios.json')
        for portfolio in portfolios:
            if portfolio['user_id'] == user_id:
                return portfolio
        return None

    def save_portfolio(self, portfolio_data: Dict[str, Any]) -> None:
        portfolios = self._read_json('portfolios.json')
        for i, portfolio in enumerate(portfolios):
            if portfolio['user_id'] == portfolio_data['user_id']:
                portfolios[i] = portfolio_data
                break
        else:
            portfolios.append(portfolio_data)
        self._write_json('portfolios.json', portfolios)

    def get_rates(self) -> Dict[str, Any]:
        file_path = os.path.join(self._data_dir, 'rates.json')
        try:
            with open(file_path, 'r') as f:
                rates = json.load(f)
            if not self._is_rate_fresh(rates.get('last_refresh')):
                return self.update_rates_cache()
            return rates
        except (FileNotFoundError, json.JSONDecodeError):
            return self.update_rates_cache()

    def update_rates_cache(self) -> Dict[str, Any]:
        from datetime import datetime
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
        self._write_json('rates.json', default_rates)
        return default_rates

    def _is_rate_fresh(self, updated_at: str) -> bool:
        from datetime import datetime, timedelta
        try:
            updated_time = datetime.fromisoformat(updated_at)
            ttl = self._settings.get('rates_ttl_seconds', 300)
            return datetime.now() - updated_time < timedelta(seconds=ttl)
        except (ValueError, TypeError):
            return False