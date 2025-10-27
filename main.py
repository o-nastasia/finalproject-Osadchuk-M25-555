#!/usr/bin/env python3

from valutatrade_hub.cli.interface import CLI
from valutatrade_hub.parser_service.scheduler import Scheduler


def main():
    scheduler = Scheduler()
    scheduler.start()
    cli = CLI()
    cli.run()

if __name__ == "__main__":
    main()