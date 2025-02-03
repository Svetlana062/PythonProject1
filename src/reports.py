import functools
import json
import logging
import os
import pathlib
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

root_directory = pathlib.Path(__file__).parent.parent.resolve()

# Формируем абсолютный путь к файлу логов
log_path = root_directory / "logs" / "reports.log"

logger = logging.getLogger("reports")  # логер с именем текущего модуля
file_handler: logging.FileHandler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

logger.debug("Debug message")


def report_decorator(filename: Optional[str] = "./data/report.json") -> Callable:
    """Декоратор для функций-отчетов."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result_ = func(*args, **kwargs)

            # Проверяем наличие директории и создаем, если её нет
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            # Записываем результат в файл
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result_, f, ensure_ascii=False, indent=4)
            logging.info(f"Report saved to {filename}")
            return result_

        return wrapper

    return decorator


@report_decorator()
def spending_by_category(transactions: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
    """Возвращает траты по заданной категории за последние три месяца от самой последней даты в данных."""

    # Получаем список всех дат в транзакциях
    dates = [datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S") for transaction in transactions]

    if not dates:
        logging.warning("No transactions available for filtering.")
        return []

    max_date = max(dates)  # Находим максимальную дату
    start_date = max_date - timedelta(days=90)  # Три месяца до максимальной даты
    filtered_transactions = [  # Фильтруем транзакции по категории и времени
        transaction
        for transaction in transactions
        if transaction["Категория"] == category
        and datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S") >= start_date
    ]
    return filtered_transactions
