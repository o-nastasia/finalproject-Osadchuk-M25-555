#!/usr/bin/env python3
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict

import requests

from ..core.exceptions import ApiRequestError
from .config import ParserConfig


class BaseApiClient(ABC):
    """Абстрактный клиент для получения курсов валют."""
    @abstractmethod
    def fetch_rates(self) -> Dict[str, Dict[str, any]]:
        pass

class CoinGeckoClient(BaseApiClient):
    """Клиент для API CoinGecko."""
    def __init__(self, config: ParserConfig):
        self.config = config
        self.config.validate()

    def fetch_rates(self) -> Dict[str, Dict[str, any]]:
        ids = ",".join(self.config.CRYPTO_ID_MAP.values())
        params = {
            "ids": ids,
            "vs_currencies": self.config.BASE_CURRENCY.lower()
        }
        try:
            response = requests.get(
                self.config.COINGECKO_URL,
                params=params,
                timeout=self.config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            rates = {}
            current_time = datetime.utcnow().isoformat() + "Z"
            for code, id_ in self.config.CRYPTO_ID_MAP.items():
                if id_ in data and self.config.BASE_CURRENCY.lower() in data[id_]:
                    rate = data[id_][self.config.BASE_CURRENCY.lower()]
                    key = f"{code}_{self.config.BASE_CURRENCY}"
                    rates[key] = {
                        "rate": rate,
                        "updated_at": current_time,
                        "source": "CoinGecko"
                    }
            return rates
        except requests.RequestException as e:
            raise ApiRequestError(f"Неудачный запрос CoinGecko: {str(e)}")

class ExchangeRateApiClient(BaseApiClient):
    """Клиент для API ExchangeRate."""
    def __init__(self, config: ParserConfig):
        self.config = config
        self.config.validate()

    def fetch_rates(self) -> Dict[str, Dict[str, any]]:
        url = f"{self.config.EXCHANGERATE_API_URL}/{self.config.EXCHANGERATE_API_KEY}/latest/{self.config.BASE_CURRENCY}"
        try:
            response = requests.get(url, timeout=self.config.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            if data.get("result") != "success":
                raise ApiRequestError(f"Ошибка ExchangeRate-API: {data.get('error-type', 'Unknown')}")
            rates = {}
            current_time = data.get("time_last_update_utc", datetime.utcnow().isoformat() + "Z")
            for fiat in self.config.FIAT_CURRENCIES:
                if fiat in data["conversion_rates"]:
                    rate = data["conversion_rates"][fiat]
                    key = f"{fiat}_{self.config.BASE_CURRENCY}"
                    rates[key] = {
                        "rate": rate,
                        "updated_at": current_time,
                        "source": "ExchangeRate-API"
                    }

                    reverse_key = f"{self.config.BASE_CURRENCY}_{fiat}"
                    rates[reverse_key] = {
                        "rate": 1 / rate if rate != 0 else 0,
                        "updated_at": current_time,
                        "source": "ExchangeRate-API"
                    }
            return rates
        except requests.RequestException as e:
            raise ApiRequestError(f"Ошибка ExchangeRate-API: {str(e)}")