# ValutaTrade Hub

ValutaTrade Hub — это CLI-приложение для симуляции торговли валютой (фиатной и криптовалютой). Оно позволяет регистрировать пользователей, авторизовываться, просматривать портфель, покупать/продавать валюту, пополнять баланс и получать курсы валют из внешних API (CoinGecko и ExchangeRate-API). Данные хранятся в JSON-файлах, логирование действий ведётся в файл. Приложение использует Poetry для управления зависимостями и Make для автоматизации задач.

Проект разработан на Python 3 и включает функциональность для обновления курсов валют по расписанию.

## Функции

- **Регистрация и авторизация пользователей**: Создание аккаунта и вход в систему.
- **Управление портфелем**: Просмотр баланса в разных валютах, конвертация в базовую валюту (по умолчанию USD).
- **Покупка/продажа валюты**: Обмен между USD и другими валютами (EUR, BTC, ETH и т.д.) с использованием актуальных курсов.
- **Пополнение баланса**: Депозит в указанную валюту.
- **Получение курсов**: Запрос текущего курса между двумя валютами.
- **Обновление курсов**: Автоматическое или ручное обновление курсов из API с кэшированием.
- **Логирование**: Все действия логируются в файл `logs/actions.log` с деталями (время, пользователь, результат).
- **Поддержка валют**: Фиат (USD, EUR, GBP, RUB), крипто (BTC, ETH, SOL). Курсы обновляются из CoinGecko (крипто) и ExchangeRate-API (фиат).
- **Расписание обновлений**: Фоновый планировщик обновляет курсы каждые 5 минут (TTL = 300 секунд).

## Требования

- Python 3.8+ (рекомендуется 3.12.3).
- Poetry для управления зависимостями (установите через `pip install poetry`).
- API-ключи:
  - `EXCHANGERATE_API_KEY` для ExchangeRate-API (получите на [exchangerate-api.com](https://www.exchangerate-api.com/)).
- Доступ к интернету для запросов к API.
- ОС: Linux/macOS/Windows (тестировалось на Unix-подобных системах).

Зависимости (управляются Poetry): requests, python-dotenv, argparse и другие (см. `pyproject.toml`).

## Установка

# Инструкция по настройке и использованию проекта

1. **Клонируйте репозиторий**:
    ```bash
    git clone https://github.com/o-nastasia/finalproject-Osadchuk-M25-555.git
    cd finalproject-Osadchuk-M25-555
    ```

2. **Установите зависимости** с помощью Make:
    ```bash
    make install
    ```
    Это создаст виртуальное окружение и установит все необходимые зависимости.

3. **Настройте окружение**:
   - Создайте файл `\.env` в корне проекта и добавьте API-ключ:
    ```bash
     EXCHANGERATE_API_KEY=ваш_ключ
     ```

## Использование

Запустите приложение с помощью Make:
    ```bash
    make project
    ```

### CLI-команды

После запуска вы увидите приветствие и список команд. Используйте их в формате:
команда --аргумент значение
- **register --username <username> --password <password>**: Регистрация нового пользователя.
- **login --username <username> --password <password>**: Вход в систему.
- **show-portfolio [--base <currency>]**: Показать портфель (баланс в базовой валюте, по умолчанию USD).
- **buy --currency <currency> --amount <amount>**: Купить валюту за USD.
- **sell --currency <currency> --amount <amount>**: Продать валюту за USD.
- **get-rate --from <currency> --to <currency>**: Получить курс обмена.
- **deposit --currency <currency> --amount <amount>**: Пополнить баланс.
- **update-rates [--source <coingecko|exchangerate>]** : Обновить курсы (из указанного источника или всех).
- **show-rates [--currency <currency>] [--top <N>] [--base <USD>]**: Показать кэшированные курсы (топ N, фильтр по валюте).
- **help**: Список команд.

**Пример сессии**:
1. Зарегистрируйтесь: `register --username testuser --password testpass`
2. Войдите: `login --username testuser --password testpass`
3. Пополните: `deposit --currency USD --amount 1000`
4. Купите: `buy --currency BTC --amount 0.1`
5. Покажите портфель: `show-portfolio`
6. Обновите курсы: `update-rates`

### Обновление курсов

- Автоматически: Планировщик запускается в фоне и обновляет курсы каждые 300 секунд.
- Ручное: Используйте `update-rates`.
- Кеш: Хранится в `data/rates.json`. Если устарел, приложение предложит обновить.

## Структура проекта

- `main.py`: Точка входа, запускает CLI и планировщик.
- `cli/interface.py`: CLI-интерфейс с парсером аргументов.
- `core/`: Бизнес-логика (модели, use cases, exceptions, currencies).
- `infra/`: Инфраструктура (database.py для JSON-хранения, settings.py).
- `parser_service/`: Сервис парсинга курсов (updater, api_clients, storage).
- `decorators.py`: Декоратор для логирования действий.
- `logging_config.py`: Настройка логирования.
- `Makefile`: Автоматизация задач.
- `data/`: Директория для JSON-файлов (users.json, portfolios.json, rates.json).
- `logs/`: Логи действий (actions.log).

## Логирование и отладка

- Логи в `logs/actions.log`.
- Формат: `%Y-%m-%dT%H:%M:%S INFO/ERROR {data}`.
- Включает timestamp, action, username, currency, amount, rate, result.

## Ошибки и исключения

- **InsufficientFundsError**: Недостаточно средств.
- **CurrencyNotFoundError**: Неизвестная валюта.
- **ApiRequestError**: Ошибка API-запроса.
- Проверки: Валидация кодов валют, сумм, паролей.

Поддерживаемые валюты: USD, EUR, BTC, ETH (расширяемо в `currencies.py` и `config.py`).

## Демо

## Автор

Анастасия Осадчук ([o-nastasia](https://github.com/o-nastasia)) группа M25-555.