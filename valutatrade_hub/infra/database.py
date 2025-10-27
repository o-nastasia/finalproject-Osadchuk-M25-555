#!/usr/bin/env python3
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from .settings import SettingsLoader


class DatabaseManager:
    """Управляет хранением данных в JSON-файлах."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._settings = SettingsLoader()
            cls._instance._data_dir = cls._instance._settings.get('data_dir', 'data')
            os.makedirs(cls._instance._data_dir, exist_ok=True)
        return cls._instance

    def _read_json(self, filename: str) -> list:
        """Читает данные из JSON-файла."""
        file_path = os.path.join(self._data_dir, filename)
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(file_path, 'w') as f:
                json.dump([], f)
            return []

    def _write_json(self, filename: str, data: list) -> None:
        """Записывает данные в JSON-файл."""
        file_path = os.path.join(self._data_dir, filename)
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Предупреждение: Не удалось сохранить данные в {filename}: {str(e)}")

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получает данные пользователя по ID."""
        users = self._read_json('users.json')
        for user_data in users:
            if user_data['user_id'] == user_id:
                return user_data
        return None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Получает данные пользователя по имени."""
        users = self._read_json('users.json')
        for user_data in users:
            if user_data['username'] == username:
                return user_data
        return None

    def save_user(self, user_data: Dict[str, Any]) -> None:
        """Сохраняет данные пользователя."""
        users = self._read_json('users.json')
        users.append(user_data)
        self._write_json('users.json', users)

    def get_portfolio_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получает портфель пользователя по ID."""
        portfolios = self._read_json('portfolios.json')
        for portfolio in portfolios:
            if portfolio['user_id'] == user_id:
                return portfolio
        return None

    def save_portfolio(self, portfolio_data: Dict[str, Any]) -> None:
        """Сохраняет данные портфеля."""
        portfolios = self._read_json('portfolios.json')
        for i, portfolio in enumerate(portfolios):
            if portfolio['user_id'] == portfolio_data['user_id']:
                portfolios[i] = portfolio_data
                break
        else:
            portfolios.append(portfolio_data)
        self._write_json('portfolios.json', portfolios)

    def get_rates(self) -> Dict[str, Any]:
        """Получает курсы валют из кэша."""
        file_path = os.path.join(self._data_dir, 'rates.json')
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            if not self._is_rate_fresh(data.get('last_refresh')):
                print("Курс устарел. Примените команду 'update-rates'.")
            return data.get("pairs", {})
        except (FileNotFoundError, json.JSONDecodeError):
            print("Файл с курсами валют не найден. римените команду 'update-rates'.")
            return {}

    def update_rates_cache(self) -> Dict[str, Any]:
        """Обновляет кэш курсов валют."""
        print("Команда для обновления курса валют 'update-rates'.")
        return self.get_rates()

    def _is_rate_fresh(self, updated_at: str) -> bool:
        """Проверяет актуальность курсов."""
        try:
            updated_time = datetime.fromisoformat(updated_at.replace("Z", ""))
            ttl = self._settings.get('rates_ttl_seconds', 300)
            return datetime.now() - updated_time < timedelta(seconds=ttl)
        except (ValueError, TypeError):
            return False