#!/usr/bin/env python3
import json
import os
from typing import Any


class SettingsLoader:
    """Загружает и хранит конфигурацию из config.json."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsLoader, cls).__new__(cls)
            cls._instance._config = {
                'data_dir': 'data',
                'rates_ttl_seconds': 300,
                'default_base_currency': 'USD',
                'log_file': 'logs/actions.log'
            }
            config_file = 'config.json'
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        cls._instance._config.update(json.load(f))
                except Exception as e:
                    print(f"Предупреждение: Не удалось загрузить конфигурацию: {str(e)}")#noqa: E501
        return cls._instance

    def get(self, key: str, default: Any = None) -> Any:
        """Получает значение конфигурации по ключу."""
        return self._config.get(key, default)

    def reload(self):
        """Перезагружает конфигурацию из config.json."""
        config_file = 'config.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    self._config.update(json.load(f))
            except Exception as e:
                print(f"Предупреждение: Не удалось перезагрузить конфигурацию: {str(e)}")#noqa: E501