#!/usr/bin/env python3
import time
from threading import Thread
from .updater import get_updater
from ..infra.settings import SettingsLoader

class Scheduler:
    def __init__(self):
        self.updater = get_updater()
        self.ttl = SettingsLoader().get('rates_ttl_seconds', 300)

    def start(self):
        def run():
            while True:
                self.updater.run_update()
                time.sleep(self.ttl)
        Thread(target=run, daemon=True).start()