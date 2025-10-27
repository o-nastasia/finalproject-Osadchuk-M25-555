#!/usr/bin/env python3
import logging
from datetime import datetime
from typing import List

from ..core.exceptions import ApiRequestError
from .api_clients import BaseApiClient, CoinGeckoClient, ExchangeRateApiClient
from .config import ParserConfig
from .storage import Storage

logger = logging.getLogger('ParserService')

class RatesUpdater:
    """Обновляет курсы валют из внешних API."""
    def __init__(self, clients: List[BaseApiClient], storage: Storage):
        self.clients = clients
        self.storage = storage
        self.config = ParserConfig()

    def run_update(self, source: str = None) -> int:
        """Обновляет курсы валют из указанного или всех источников."""
        logger.info("Starting rates update...")
        all_rates = {}
        updated_count = 0
        for client in self.clients:
            client_name = type(client).__name__.replace("Client", "")
            if source and source.lower() != client_name.lower():
                continue
            try:
                rates = client.fetch_rates()
                all_rates.update(rates)
                updated_count += len(rates)
                logger.info(f"Fetching from {client_name}... OK ({len(rates)} rates)")
            except ApiRequestError as e:
                logger.error(f"Failed to fetch from {client_name}: {str(e)}")
        if all_rates:
            current_time = datetime.utcnow().isoformat() + "Z"
            self.storage.save_rates(all_rates, current_time)
            self.storage.save_history(all_rates)
            logger.info(f"Writing {updated_count} rates to {self.config.RATES_FILE_PATH}...")#noqa: E501
        return updated_count

def get_updater() -> RatesUpdater:
    """Создаёт экземпляр RatesUpdater."""
    config = ParserConfig()
    clients = [
        CoinGeckoClient(config),
        ExchangeRateApiClient(config)
    ]
    storage = Storage(config)
    return RatesUpdater(clients, storage)