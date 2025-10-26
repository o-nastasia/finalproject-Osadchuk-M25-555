#!/usr/bin/env python3
from typing import Any
import json
import os

class SettingsLoader:
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
                    print(f"Предупреждение: Не удалось загрузить конфигурацию: {str(e)}")
        return cls._instance

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def reload(self):
        config_file = 'config.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    self._config.update(json.load(f))
            except Exception as e:
                print(f"Предупреждение: Не удалось перезагрузить конфигурацию: {str(e)}")