#!/usr/bin/env python3
from datetime import datetime
from functools import wraps
from typing import Callable

from .core.utils import get_portfolio_by_user_id, get_rates, get_user_by_id
from .logging_config import setup_logging

logger = setup_logging()

def log_action(verbose: bool = False) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            action = func.__name__.upper()
            user_id = args[0] if action in ['BUY', 'SELL', 'DEPOSIT'] else None
            user = get_user_by_id(user_id) if user_id else None
            username = user.username if user else "unknown"
            
            currency = kwargs.get('currency', args[1] if len(args) > 1 else None)
            amount = kwargs.get('amount', args[2] if len(args) > 2 else None)
            base = kwargs.get('base', 'USD')
            rate = None
            
            try:
                result = func(*args, **kwargs)
                if action in ['BUY', 'SELL']:
                    rates = get_rates()
                    rate_key = f"{currency}_{base}"
                    rate = rates.get(rate_key, {}).get('rate', None)
                
                log_data = {
                    'timestamp': datetime.now().isoformat(),
                    'action': action,
                    'username': username,
                    'currency_code': currency,
                    'amount': amount,
                    'rate': rate,
                    'base': base,
                    'result': 'OK'
                }
                if verbose and action in ['BUY', 'SELL', 'DEPOSIT']:
                    portfolio_before = get_portfolio_by_user_id(user_id)
                    log_data['portfolio_before'] = portfolio_before.get('wallets', {}) if portfolio_before else {}
                
                logger.info(f"{log_data}")
                return result
            except Exception as e:
                log_data = {
                    'timestamp': datetime.now().isoformat(),
                    'action': action,
                    'username': username,
                    'currency_code': currency,
                    'amount': amount,
                    'rate': rate,
                    'base': base,
                    'result': 'ERROR',
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                }
                logger.error(f"{log_data}")
                raise
        return wrapper
    return decorator