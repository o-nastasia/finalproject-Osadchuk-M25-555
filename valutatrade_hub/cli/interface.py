#!/usr/bin/env python3
import argparse
from ..core.models import User
from ..core.usecases import UseCases

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

        # Команда help
        help_parser = self.subparsers.add_parser('help')

        # Вывод приветствия
        print("Добро пожаловать в ValutaTrade CLI!")
        self.show_help()

    def show_help(self):
        """Выводит список доступных команд и их использование."""
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
        print("Получить курс валют\n*******")
        print("\ndeposit --currency <currency> --amount <amount>")
        print("Пополнить баланс\n*******")
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
        if args.command == 'register':
            print(UseCases.register(args.username, args.password))
        elif args.command == 'login':
            user, message = UseCases.login(args.username, args.password)
            self.current_user = user
            print(message)
        elif args.command in ['show-portfolio', 'buy', 'sell']:
            if not self.current_user:
                print("Сначала выполните login")
                return
            if args.command == 'show-portfolio':
                print(UseCases.show_portfolio(self.current_user.user_id, args.base))
            elif args.command == 'buy':
                print(UseCases.buy(self.current_user.user_id, args.currency.upper(), args.amount))
            elif args.command == 'sell':
                print(UseCases.sell(self.current_user.user_id, args.currency.upper(), args.amount))
        elif args.command == 'get-rate':
            print(UseCases.get_rate(args.__dict__['from'].upper(), args.to.upper()))
        elif args.command == 'deposit':
            if not self.current_user:
                print("Сначала выполните login")
                return
            print(UseCases.deposit(self.current_user.user_id, args.currency.upper(), args.amount))
        elif args.command == 'help':
            self.show_help()
        else:
            print("Неизвестная команда. Используйте 'help' для списка команд.")

if __name__ == "__main__":
    cli = CLI()
    cli.run()