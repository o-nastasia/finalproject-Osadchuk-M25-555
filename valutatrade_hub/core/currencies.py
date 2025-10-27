#!/usr/bin/env python3
from abc import ABC, abstractmethod

from .exceptions import CurrencyNotFoundError


class Currency(ABC):
    def __init__(self, name: str, code: str):
        if not isinstance(code, str) or not (2 <= len(code.strip()) <= 5) or ' ' in code:
            raise ValueError("Код валюты должен быть строкой от 2 до 5 символов без пробелов")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Имя валюты не может быть пустым")
        self._name = name.strip()
        self._code = code.strip().upper()

    @property
    def name(self) -> str:
        return self._name

    @property
    def code(self) -> str:
        return self._code

    @abstractmethod
    def get_display_info(self) -> str:
        pass

class FiatCurrency(Currency):
    def __init__(self, name: str, code: str, issuing_country: str):
        super().__init__(name, code)
        if not isinstance(issuing_country, str) or not issuing_country.strip():
            raise ValueError("Страна эмиссии не может быть пустой")
        self._issuing_country = issuing_country.strip()

    def get_display_info(self) -> str:
        return f"[FIAT] {self.code} — {self.name} (Issuing: {self._issuing_country})"

class CryptoCurrency(Currency):
    def __init__(self, name: str, code: str, algorithm: str, market_cap: float):
        super().__init__(name, code)
        if not isinstance(algorithm, str) or not algorithm.strip():
            raise ValueError("Алгоритм не может быть пустым")
        if not isinstance(market_cap, (int, float)) or market_cap < 0:
            raise ValueError("Капитализация должна быть неотрицательным числом")
        self._algorithm = algorithm.strip()
        self._market_cap = float(market_cap)

    def get_display_info(self) -> str:
        return f"[CRYPTO] {self.code} — {self.name} (Algo: {self._algorithm}, MCAP: {self._market_cap:.2e})"

# Реестр валют
_currency_registry = {
    "USD": FiatCurrency("US Dollar", "USD", "United States"),
    "EUR": FiatCurrency("Euro", "EUR", "Eurozone"),
    "BTC": CryptoCurrency("Bitcoin", "BTC", "SHA-256", 1.12e12),
    "ETH": CryptoCurrency("Ethereum", "ETH", "Ethash", 3.45e11)
}

def get_currency(code: str) -> Currency:
    if not isinstance(code, str) or not code.strip():
        raise CurrencyNotFoundError("Код валюты должен быть непустой строкой")
    code = code.strip().upper()
    currency = _currency_registry.get(code)
    if currency is None:
        raise CurrencyNotFoundError(f"Неизвестная валюта '{code}'")
    return currency