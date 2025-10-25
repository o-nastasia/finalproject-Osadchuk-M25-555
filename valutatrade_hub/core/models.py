#!/usr/bin/env python3
from typing import Dict, Optional
import hashlib
import uuid
from datetime import datetime
from copy import deepcopy
from .utils import get_user_by_id, get_rates

class User:
    def __init__(self, user_id: int, username: str, password: str):
        self._user_id = self._validate_user_id(user_id)
        self._username = self._validate_username(username)
        self._salt = str(uuid.uuid4())
        self._hashed_password = self._hash_password(password, self._salt)
        self._registration_date = datetime.now()

    def _validate_user_id(self, user_id: int) -> int:
        if not isinstance(user_id, int):
            print("Предупреждение: User ID должен быть целым числом")
            return 0
        return user_id

    def _validate_username(self, username: str) -> str:
        if not isinstance(username, str) or not username.strip():
            print("Предупреждение: Имя пользователя не может быть пустым")
            return "default_user"
        return username.strip()

    def _validate_password(self, password: str) -> Optional[str]:
        if not isinstance(password, str) or len(password) < 4:
            print("Предупреждение: Пароль должен быть строкой длиной не менее 4 символов")
            return None
        return password

    def _hash_password(self, password: str, salt: str) -> str:
        if not isinstance(password, str) or not isinstance(salt, str):
            print("Предупреждение: Пароль и соль должны быть строками")
            return ""
        return hashlib.sha256((password + salt).encode()).hexdigest()

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @property
    def registration_date(self) -> datetime:
        return self._registration_date

    @username.setter
    def username(self, new_username: str):
        validated_username = self._validate_username(new_username)
        self._username = validated_username

    def get_user_info(self) -> dict:
        return {
            "user_id": self._user_id,
            "username": self._username,
            "registration_date": self._registration_date
        }

    def change_password(self, new_password: str) -> bool:
        validated_password = self._validate_password(new_password)
        if validated_password is None:
            return False
        self._hashed_password = self._hash_password(validated_password, self._salt)
        return True

    def verify_password(self, password: str) -> bool:
        hashed_input = self._hash_password(password, self._salt)
        return hashed_input == self._hashed_password and hashed_input != ""

    def to_json(self) -> dict:
        return {
            "user_id": self._user_id,
            "username": self._username,
            "hashed_password": self._hashed_password,
            "salt": self._salt,
            "registration_date": self._registration_date.isoformat()
        }

class Wallet:
    def __init__(self, currency_code: str, balance: float = 0.0):
        self.currency_code = self._validate_currency_code(currency_code)
        self._balance = self._validate_balance(balance)

    def _validate_currency_code(self, currency_code: str) -> str:
        if not isinstance(currency_code, str) or not currency_code.strip():
            print("Предупреждение: Код валюты должен быть непустой строкой")
            return "UNKNOWN"
        return currency_code.strip()

    def _validate_balance(self, value: float) -> float:
        if not isinstance(value, (int, float)):
            print("Предупреждение: Баланс должен быть числом")
            return 0.0
        if value < 0:
            print("Предупреждение: Баланс не может быть отрицательным")
            return 0.0
        return float(value)

    def _validate_amount(self, amount: float) -> Optional[float]:
        if not isinstance(amount, (int, float)):
            print("Предупреждение: Сумма должна быть числом")
            return None
        if amount <= 0:
            print("Предупреждение: Сумма должна быть положительной")
            return None
        return float(amount)

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:
        self._balance = self._validate_balance(value)

    def deposit(self, amount: float) -> bool:
        validated_amount = self._validate_amount(amount)
        if validated_amount is None:
            return False
        self._balance += validated_amount
        return True

    def withdraw(self, amount: float) -> bool:
        validated_amount = self._validate_amount(amount)
        if validated_amount is None:
            return False
        if validated_amount > self._balance:
            print("Предупреждение: Недостаточно средств для снятия")
            return False
        self._balance -= validated_amount
        return True

    def get_balance_info(self) -> str:
        return f"Wallet {self.currency_code}: {self._balance:.2f}"

    def to_dict(self) -> dict:
        return {
            "currency_code": self.currency_code,
            "balance": self._balance
        }
    
class Portfolio:
    def __init__(self, user_id: int):
        self._user_id = user_id
        self._wallets: Dict[str, Wallet] = {}

    @property
    def user(self) -> User:
        user = get_user_by_id(self._user_id)
        if user is None:
            raise ValueError(f"Пользователь с ID {self._user_id} не найден")
        return user

    @property
    def wallets(self) -> Dict[str, Wallet]:
        return deepcopy(self._wallets)

    def add_currency(self, currency_code: str) -> bool:
        if not isinstance(currency_code, str) or not currency_code.strip():
            print(f"Предупреждение: Код валюты должен быть непустой строкой")
            return False
            
        if currency_code in self._wallets:
            print(f"Предупреждение: Кошелёк для валюты {currency_code} уже существует")
            return False
        
        self._wallets[currency_code] = Wallet(currency_code)
        return True

    def get_wallet(self, currency_code: str) -> Optional[Wallet]:
        if not isinstance(currency_code, str) or not currency_code.strip():
            print(f"Предупреждение: Код валюты должен быть непустой строкой")
            return None
            
        wallet = self._wallets.get(currency_code)
        if wallet is None:
            print(f"Предупреждение: Кошелёк для валюты {currency_code} не найден")
        return wallet

    def get_total_value(self, base_currency: str = 'USD') -> float:
        if not isinstance(base_currency, str) or not base_currency.strip():
            print(f"Предупреждение: Код базовой валюты должен быть непустой строкой")
            return 0.0
        
        rates = get_rates()

        total_value = 0.0
        for currency, wallet in self._wallets.items():
            if wallet is None:
                continue
            balance = wallet.balance
            try:
                if currency == base_currency:
                    total_value += balance
                else:
                    rate_key = f"{currency}_{base_currency}"
                    rate = rates.get(rate_key, {}).get('rate', None)
                    if rate is None:
                        print(f"Предупреждение: Курс для валюты {currency}→{base_currency} не найден")
                        return 0.0
                    total_value += balance * rate
            except Exception as e:
                print(f"Предупреждение: Ошибка при конвертации валюты {currency}: {str(e)}")
                return 0.0
        
        return round(total_value, 2)

    def to_json(self) -> dict:
        return {
            "user_id": self._user_id,
            "wallets": {code: {"balance": wallet.balance} for code, wallet in self._wallets.items()}
        }