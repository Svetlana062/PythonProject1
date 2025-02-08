import json
import logging
import pathlib
from datetime import datetime
from logging import FileHandler
from typing import Any, Dict, List

import pandas as pd

from src.utils import card_info, get_currency_rate, get_stock_prices, greetings, top_5_transactions

root_directory = pathlib.Path(__file__).parent.parent.resolve()

# Формируем абсолютный путь к файлу логов
log_path = root_directory / "logs" / "views.log"

logger = logging.getLogger("views")  # логер с именем текущего модуля
file_handler: FileHandler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

logger.debug("Debug message")


def views(transactions_df: List[Dict[str, Any]], date: str) -> Dict[str, Any] | str:
    """Функция принимает дату (строка) и DataFrame с данными по транзакциям.
    Возвращает ответ с приветствием, информацией по картам,
    топ-5 транзакций стоимость валюты и акций в виде json-строки."""
    try:
        logger.info("Начало работы функции views")
        # Преобразуем строку с датой в объект datetime
        reference_date = datetime.strptime(date, "%d.%m.%Y")
        start_of_month = reference_date.replace(day=1)

        # Фильтруем транзакции в диапазоне дат
        transactions_filtered = [
            transaction
            for transaction in transactions_df
            if start_of_month
            <= pd.to_datetime(transaction["Дата операции"], format="%d.%m.%Y %H:%M:%S")
            <= reference_date
        ]

        # transactions = transactions_df
        greeting = greetings()
        cards = card_info(transactions_filtered)
        top_transactions = top_5_transactions(transactions_filtered)
        currency_rates = get_currency_rate()
        stock_prices = get_stock_prices()

        result_dict = {
            "greeting": greeting,
            "cards": cards,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices,
        }
        result_json = json.dumps(result_dict, ensure_ascii=False)
        logger.info("Корректный JSON-ответ функции views")
        return result_json
    except Exception:
        logger.exception("Ошибка в функции views")
        raise ValueError("При работе функции произошла ошибка.")
