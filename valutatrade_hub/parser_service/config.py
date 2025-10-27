#!/usr/bin/env python3
import os
from dataclasses import dataclass, field
from typing import Tuple, Dict
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ParserConfig:
    EXCHANGERATE_API_KEY: str = os.getenv("EXCHANGERATE_API_KEY", "KEY")

    COINGECKO_URL: str = "https://api.coingecko.com/api/v3/simple/price"
    EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6/"

    BASE_CURRENCY: str = "USD"
    FIAT_CURRENCIES: Tuple[str, ...] = ("EUR", "GBP", "RUB")
    CRYPTO_CURRENCIES: Tuple[str, ...] = ("BTC", "ETH", "SOL")
    CRYPTO_ID_MAP: Dict[str, str] = field(default_factory=lambda: {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
    })

    RATES_FILE_PATH: str = "data/rates.json"
    HISTORY_FILE_PATH: str = "data/exchange_rates.json"

    REQUEST_TIMEOUT: int = 10

    def validate(self) -> None:
        if self.EXCHANGERATE_API_KEY == "KEY":
            raise ValueError("EXCHANGERATE_API_KEY не задан в переменных окружения")
        if not all(isinstance(code, str) and 2 <= len(code) <= 5 for code in self.FIAT_CURRENCIES):
            raise ValueError("Некорректные коды фиатных валют")
        if not all(isinstance(code, str) and 2 <= len(code) <= 5 for code in self.CRYPTO_CURRENCIES):
            raise ValueError("Некорректные коды криптовалют")