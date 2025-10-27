#!/usr/bin/env python3
import json
import os
from typing import Dict

from .config import ParserConfig


class Storage:
    """Хранит и управляет данными о курсах валют."""
    def __init__(self, config: ParserConfig):
        self.config = config
        os.makedirs('data', exist_ok=True)

    def save_rates(self, rates: Dict[str, Dict[str, any]], last_refresh: str) -> None:
        """Сохраняет курсы валют в rates.json."""
        data = {
            "pairs": rates,
            "last_refresh": last_refresh
        }
        with open(self.config.RATES_FILE_PATH, 'w') as f:
            json.dump(data, f, indent=2)

    def save_history(self, rates: Dict[str, Dict[str, any]]) -> None:
        """Сохраняет историю курсов в exchange_rates.json."""
        history = self._load_history()
        for key, rate_data in rates.items():
            timestamp = rate_data["updated_at"]
            hist_id = f"{key}_{timestamp}"
            entry = {
                "id": hist_id,
                "from_currency": key.split("_")[0],
                "to_currency": key.split("_")[1],
                "rate": rate_data["rate"],
                "timestamp": timestamp,
                "source": rate_data["source"],
                "meta": {}
            }
            if hist_id not in [e["id"] for e in history]:
                history.append(entry)
        with open(self.config.HISTORY_FILE_PATH, 'w') as f:
            json.dump(history, f, indent=2)

    def _load_history(self) -> list:
        """Загружает историю курсов из exchange_rates.json."""
        try:
            with open(self.config.HISTORY_FILE_PATH, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def load_rates(self) -> Dict[str, any]:
        """Загружает курсы валют из rates.json."""
        try:
            with open(self.config.RATES_FILE_PATH, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"pairs": {}, "last_refresh": None}