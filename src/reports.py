import functools
import json
import logging
import os
import pathlib
from datetime import datetime
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
            return result_

        return wrapper

    return decorator


def load_transactions_from_excel(file_path: str) -> pd.DataFrame:
    """Загрузка транзакций из Excel файла в DataFrame."""
    try:
        df = pd.read_excel(file_path)
        logger.info("Транзакции успешно загружены, функция load_transactions_from_excel")

        return df
    except FileNotFoundError:
        return pd.DataFrame()  # Возвращаем пустой DataFrame в случае ошибки
    except Exception as e:
        print(f"Ошибка при загрузке файла: {e}, функция load_transactions_from_excel")
        return pd.DataFrame()


@report_decorator()
def spending_by_category(transactions_df: pd.DataFrame, category: str, date: str) -> List[Dict[str, Any]]:
    """Возвращает список транзакций по указанной категории за 3 месяца до указанной даты."""

    end_date = datetime.strptime(date, "%d.%m.%Y")
    start_date = end_date - pd.DateOffset(months=3)

    transactions_df["Дата платежа"] = pd.to_datetime(transactions_df["Дата платежа"], dayfirst=True)

    filtered_data = transactions_df[
        (transactions_df["Категория"] == category)
        & (transactions_df["Дата платежа"] >= start_date)
        & (transactions_df["Дата платежа"] <= end_date)
    ]

    # Преобразуем все значения в строки
    transaction_list = filtered_data.astype(str).to_dict(orient="records")
    return transaction_list
