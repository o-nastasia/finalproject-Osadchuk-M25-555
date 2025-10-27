#!/usr/bin/env python3
import argparse
from datetime import datetime

from ..core.exceptions import (
    ApiRequestError,
    CurrencyNotFoundError,
    InsufficientFundsError,
)
from ..core.models import User
from ..core.usecases import UseCases
from ..parser_service.config import ParserConfig
from ..parser_service.storage import Storage
from ..parser_service.updater import get_updater


class CLI:
    def __init__(self):
        self.current_user: User = None
        self.parser = argparse.ArgumentParser(description="ValutaTrade CLI")
        self.subparsers = self.parser.add_subparsers(dest='command')

        register_parser = self.subparsers.add_parser('register')
        register_parser.add_argument('--username', type=str, required=True)
        register_parser.add_argument('--password', type=str, required=True)

        login_parser = self.subparsers.add_parser('login')
        login_parser.add_argument('--username', type=str, required=True)
        login_parser.add_argument('--password', type=str, required=True)

        portfolio_parser = self.subparsers.add_parser('show-portfolio')
        portfolio_parser.add_argument('--base', type=str, default='USD')

        buy_parser = self.subparsers.add_parser('buy')
        buy_parser.add_argument('--currency', type=str, required=True)
        buy_parser.add_argument('--amount', type=float, required=True)

        sell_parser = self.subparsers.add_parser('sell')
        sell_parser.add_argument('--currency', type=str, required=True)
        sell_parser.add_argument('--amount', type=float, required=True)

        rate_parser = self.subparsers.add_parser('get-rate')
        rate_parser.add_argument('--from', type=str, required=True)
        rate_parser.add_argument('--to', type=str, required=True)

        deposit_parser = self.subparsers.add_parser('deposit')
        deposit_parser.add_argument('--currency', type=str, required=True)
        deposit_parser.add_argument('--amount', type=float, required=True)

        update_rates_parser = self.subparsers.add_parser('update-rates')
        update_rates_parser.add_argument('--source', type=str, required=False)

        show_rates_parser = self.subparsers.add_parser('show-rates')
        show_rates_parser.add_argument('--currency', type=str, required=False)
        show_rates_parser.add_argument('--top', type=int, required=False)
        show_rates_parser.add_argument('--base', type=str, default='USD')

        self.subparsers.add_parser('help')

        print("Добро пожаловать в ValutaTrade CLI!")
        self.show_help()

    def show_help(self):
        print("\nДоступные команды:\n*******")
        print("\nregister --username <username> --password <password>")
        print("Регистрация нового пользователя\n*******")
        print("\nlogin --username <username> --password <password>")
        print("Вход в систему\n*******")
        print("\nshow-portfolio [--base <currency>]")
        print("Показать портфель пользователя (валюта по умолчанию: USD)\n*******")
        print("\nbuy --currency <currency> --amount <amount>")
        print("Купить валюту\n*******")
        print("\nsell --currency <currency> --amount <amount>")
        print("Продать валюту\n*******")
        print("\nget-rate --from <currency> --to <currency>")
        print("Получить курс валют (поддерживаемые валюты: USD, EUR, BTC, ETH)\n*******")#noqa: E501
        print("\ndeposit --currency <currency> --amount <amount>")
        print("Пополнить баланс\n*******")
        print("\nupdate-rates [--source <coingecko|exchangerate>]")
        print("Обновить курсы валют\n*******")
        print("\nshow-rates [--currency <currency>] [--top <N>] [--base <currency>]")
        print("Показать актуальные курсы\n*******")
        print("\nhelp")
        print("Показать список команд\n*******")
        print("\nexit")
        print("Выйти из программы\n")

    def run(self):
        while True:
            try:
                command = input("> ").strip()
                if command.lower() == 'exit':
                    print("Выход из программы")
                    break
                args = self.parser.parse_args(command.split())
                self.handle_command(args)
            except KeyboardInterrupt:
                print("\nВыход из программы")
                break
            except SystemExit:
                continue
            except Exception as e:
                print(f"Ошибка: {str(e)}")

    def handle_command(self, args):
        try:
            if args.command == 'register':
                print(UseCases.register(args.username, args.password))
            elif args.command == 'login':
                user, message = UseCases.login(args.username, args.password)
                self.current_user = user
                print(message)
            elif args.command in ['show-portfolio', 'buy', 'sell', 'deposit']:
                if not self.current_user:
                    print("Сначала выполните login")
                    return
                if args.command == 'show-portfolio':
                    print(UseCases.show_portfolio(self.current_user.user_id, args.base.upper()))#noqa: E501
                elif args.command == 'buy':
                    print(UseCases.buy(self.current_user.user_id, args.currency.upper(), args.amount))#noqa: E501
                elif args.command == 'sell':
                    print(UseCases.sell(self.current_user.user_id, args.currency.upper(), args.amount))#noqa: E501
                elif args.command == 'deposit':
                    print(UseCases.deposit(self.current_user.user_id, args.currency.upper(), args.amount))#noqa: E501
            elif args.command == 'get-rate':
                print(UseCases.get_rate(args.__dict__['from'].upper(), args.to.upper()))
            elif args.command == 'update-rates':
                updater = get_updater()
                count = updater.run_update(args.source)
                if count > 0:
                    print(f"Успешно обновлены курсы для {count} валют. Последнее обновление: {datetime.utcnow().strftime("%Y-%m-%d %H:%M")}")#noqa: E501
                else:
                    print("Ошибка при обновлении. Подробности в файле logs")
            elif args.command == 'show-rates':
                config = ParserConfig()
                storage = Storage(config)
                data = storage.load_rates()
                pairs = data.get("pairs", {})
                last_refresh = data.get("last_refresh", "Unknown")
                last_refresh = last_refresh[:16].replace("T", " ")

                if not pairs:
                    print("Локальный кеш курсов пуст. Выполните 'update-rates', чтобы загрузить данные.")#noqa: E501
                    return

                filtered = {}
                base = args.base.upper()
                for key, value in pairs.items():
                    from_curr, to_curr = key.split("_")
                    if to_curr != base:
                        continue
                    if args.currency and from_curr != args.currency.upper():
                        continue
                    filtered[key] = value

                if not filtered:
                    if args.currency:
                        print(f"Курс для '{args.currency.upper()}' не найден в кеше.")
                    else:
                        print("Нет данных по указанным фильтрам.")
                    return

                sorted_pairs = sorted(filtered.items(), \
                                      key=lambda x: x[1]["rate"], reverse=True)
                if args.top:
                    sorted_pairs = sorted_pairs[:args.top]

                print(f"Курсы из кеша (последнее обновление {last_refresh}):")
                for key, value in sorted_pairs:
                    print(f"- {key}: {value['rate']:.2f}")
            elif args.command == 'help':
                self.show_help()
            else:
                print("Неизвестная команда. Используйте 'help' для списка команд.")
        except InsufficientFundsError as e:
            print(f"Ошибка: {e.message}")
        except CurrencyNotFoundError as e:
            print(f"Ошибка: {e.message}. Поддерживаемые валюты: USD, EUR, BTC, ETH.")
        except ApiRequestError as e:
            print(f"Ошибка: {e.message}. Повторите попытку позже или проверьте сеть.")
        except ValueError as e:
            print(f"Ошибка конфигурации: {str(e)}")

if __name__ == "__main__":
    cli = CLI()
    cli.run()