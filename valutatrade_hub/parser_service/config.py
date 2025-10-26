#!/usr/bin/env python3
# valutatrade_hub/parser_service/config.py
import os
from dataclasses import dataclass, field
from typing import Tuple, Dict
from dotenv import load_dotenv

# Загружаем переменные из .env файла, если он существует
load_dotenv()

@dataclass
class ParserConfig:
    # Ключи API загружаются из переменных окружения
    EXCHANGERATE_API_KEY: str = os.getenv("EXCHANGERATE_API_KEY", "КЛЮЧ")  # Заглушка для тестирования

    # Эндпоинты
    COINGECKO_URL: str = "https://api.coingecko.com/api/v3/simple/price"
    EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6/"

    # Централизованные списки валют и базовая валюта
    BASE_CURRENCY: str = "USD"
    FIAT_CURRENCIES: Tuple[str, ...] = ("EUR", "GBP", "RUB")
    CRYPTO_CURRENCIES: Tuple[str, ...] = ("BTC", "ETH", "SOL")
    CRYPTO_ID_MAP: Dict[str, str] = field(default_factory=lambda: {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
    })

    # Пути к файлам
    RATES_FILE_PATH: str = "data/rates.json"
    HISTORY_FILE_PATH: str = "data/exchange_rates.json"

    # Сетевые параметры
    REQUEST_TIMEOUT: int = 10

    def validate(self) -> None:
        """Проверяет наличие ключей API и корректность конфигурации."""
        if self.EXCHANGERATE_API_KEY == "КЛЮЧ":
            raise ValueError("EXCHANGERATE_API_KEY не задан в переменных окружения")
        if not all(isinstance(code, str) and 2 <= len(code) <= 5 for code in self.FIAT_CURRENCIES):
            raise ValueError("Некорректные коды фиатных валют")
        if not all(isinstance(code, str) and 2 <= len(code) <= 5 for code in self.CRYPTO_CURRENCIES):
            raise ValueError("Некорректные коды криптовалют")