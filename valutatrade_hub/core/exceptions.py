#!/usr/bin/env python3

class InsufficientFundsError(Exception):
    def __init__(self, available: float, required: float, code: str):
        self.message = f"Недостаточно средств: доступно {available:.4f} {code}, требуется {required:.4f} {code}"
        super().__init__(self.message)

class CurrencyNotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ApiRequestError(Exception):
    def __init__(self, reason: str):
        self.message = f"Ошибка при обращении к внешнему API: {reason}"
        super().__init__(self.message)