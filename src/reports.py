import functools
import json
import logging
import os
import pathlib
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

import pandas as pd

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


def load_transactions_from_excel(file_path: str) -> pd.DataFrame:
    """Загрузка транзакций из Excel файла в DataFrame."""
    try:
        df = pd.read_excel(file_path)
        return df
    except FileNotFoundError:
        print(f"Файл не найден: {file_path}")
        return pd.DataFrame()  # Возвращаем пустой DataFrame в случае ошибки
    except Exception as e:
        print(f"Ошибка при загрузке файла: {e}")
        return pd.DataFrame()


@report_decorator()
def spending_by_category(
    transactions_df: pd.DataFrame, category: str, reference_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Возвращает траты по заданной категории за последние три месяца от указанной даты."""

    # Если дата не передана, используем текущую дату
    if reference_date is None:
        reference_date = datetime.now().strftime("%d.%m.%Y")

    # Преобразуем строку с датой в объект datetime
    reference_date = datetime.strptime(reference_date, "%d.%m.%Y")
    start_date = reference_date - timedelta(days=90)  # Три месяца до указанной даты

    # Фильтруем DataFrame по категории и дате
    filtered_transactions = transactions_df[
        (transactions_df["Категория"] == category) & (pd.to_datetime(transactions_df["Дата операции"]) >= start_date)
    ]

    # Преобразуем отфильтрованные DataFrame в список словарей для возврата
    result = filtered_transactions.to_dict(orient="records")

    logging.info(f"Успешное завершение операции для категории: {category}")
    return result
