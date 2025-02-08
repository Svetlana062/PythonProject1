import datetime
import json
import logging
import pathlib
from math import floor
from typing import Any, Dict, List, Union

# Настройка логирования
root_directory = pathlib.Path(__file__).parent.parent.resolve()
log_path = root_directory / "logs" / "utils.log"
logger = logging.getLogger("services")
file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

logger.debug("Debug message")


def limit_payment(limit: int, payment: Union[int, float]) -> int | float:
    """Округляет сумму операции в соответствии с лимитом."""
    logger.info("Функция начала свою работу.")

    if payment == 0:
        logger.info("Сумма платежа равна 0, возвращаем 0.")
        return 0

    # Поскольку мы работаем с отрицательными расходами
    if payment < 0:
        payment_with_limit = floor(payment / limit) * limit  # Округление вниз
    else:
        # Положительные значения не должны учитываться
        return payment

    logger.info("Функция успешно завершила свою работу.")
    return payment_with_limit


def date_sorting(month: str, transactions: List[Dict[str, Any]]) -> List[Dict]:
    """Фильтрует транзакции по указанному месяцу."""
    logger.info("Функция начала свою работу.")
    sorted_transactions_list = []
    month_of_sorting = datetime.datetime.strptime(month, "%Y-%m").month
    year_of_sorting = datetime.datetime.strptime(month, "%Y-%m").year

    for transaction in transactions:
        month_of_operation = datetime.datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S").month
        year_of_operation = datetime.datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S").year
        if month_of_sorting == month_of_operation and year_of_sorting == year_of_operation:
            sorted_transactions_list.append(transaction)

    logger.info("Функция успешно завершила свою работу.")
    return sorted_transactions_list


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> str:
    """Рассчитывает сумму, которую удалось бы отложить в Инвесткопилку."""
    logger.info("Функция начала свою работу.")
    investment_result = 0
    sorted_transactions_by_month = date_sorting(month, transactions)

    for transaction in sorted_transactions_by_month:
        transaction_amount = transaction["Сумма операции"]

        # Обрабатываем только отрицательные суммы
        if transaction_amount < 0:
            # Округляем до ближайшего лимита
            rounded_payment = limit_payment(limit, transaction_amount)

            # Разница между округленной суммой и фактической
            difference = abs(rounded_payment - transaction_amount)
            investment_result += difference  # добавляем к 'Инвесткопилке'

    logger.info("Функция успешно завершила свою работу.")
    result = round(float(investment_result), 2)

    # Сформируем JSON-ответ с результатом
    result_json = json.dumps({"Investment Bank": result}, ensure_ascii=False)
    return result_json
