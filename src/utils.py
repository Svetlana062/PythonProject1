import json
import logging
import os
import pathlib
from collections import defaultdict
from datetime import datetime
from logging import FileHandler
from typing import Any, Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv

root_directory = pathlib.Path(__file__).parent.parent.resolve()

# Формируем абсолютный путь к файлу логов
log_path = root_directory / "logs" / "utils.log"

logger = logging.getLogger("utils")  # логер с именем текущего модуля
file_handler: FileHandler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

logger.debug("Debug message")


def greetings() -> str:
    """Приветствие, в зависимости от времени суток"""
    logger.info("Начало работы функции greetings")
    date_time = datetime.now()
    logger.info("Совершен запрос на текущие дату и время функции greetings")
    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if 0 <= date_time.hour < 6:
        logger.info("Корректный ответ функции greetings")
        return "Доброй ночи"
    elif 6 <= date_time.hour < 12:
        logger.info("Корректный ответ функции greetings")
        return "Доброе утро"
    elif 12 <= date_time.hour < 18:
        logger.info("Корректный ответ функции greetings")
        return "Добрый день"
    else:
        logger.info("Корректный ответ функции greetings")
        return "Добрый вечер"


def read_transactions_from_excel(filename: str) -> list[dict]:
    """Считывание Excel-файла с транзакциями."""
    if filename.endswith("xls") or filename.endswith("xlsx"):
        logger.info("Начало работы функции read_transactions_from_excel")
        try:
            df = pd.read_excel(filename)
            dict_list = df.to_dict(orient="records")
            logger.info("Корректный ответ функции read_transactions_from_excel")
            return dict_list
        except FileNotFoundError:
            logger.exception("Ошибка в функции read_transactions_from_excel")
            return []
        except pd.errors.EmptyDataError:  # пустой файл
            logger.exception("Ошибка в функции read_transactions_from_excel")
            return []
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            logger.exception("Ошибка в функции views")
            return []


def card_info(transactions: list[dict]) -> list[dict]:
    """Функция принимает список транзакций(словарей).
    Возвращает список словарей с информацией по каждой карте: последние 4 цифры номера карты,
    общая сумма расходов, кешбэк (1 рубль на каждые 100 рублей)."""
    logger.info("Начало работы функции card_info")

    unique_card_nums = list(set(transaction.get("Номер карты") for transaction in transactions))
    expenditure_by_card = defaultdict(int)

    for card_num in unique_card_nums:
        logger.info("Распределение данных в зависимости от номеров карт функции card_info")

        for transaction in transactions:
            if transaction.get("Номер карты") == card_num:
                # без KeyError, если ключ отсутствует, возвращаем 0
                sum_operation = transaction.get("Сумма операции", 0)
                if sum_operation < 0:
                    expenditure_by_card[card_num] += sum_operation

    result_transaction_list = []

    for item in expenditure_by_card:
        logger.info("Вывод данных функции card_info")
        result_transaction_list.append(
            {
                "last_digits": item[1:],  # последние 4 цифры
                "total_spent": round(expenditure_by_card[item], 2),
                "cashback": abs(round(expenditure_by_card[item] / 100, 2)),
            }
        )

    logger.info("Корректный ответ функции card_info")
    return result_transaction_list


def top_5_transactions(transactions: list[dict]) -> list[dict]:
    """Функция возвращает топ-5 транзакций по сумме."""
    try:
        # Фильтруем транзакции с доступным значением 'Сумма операции'
        valid_transactions = [transaction for transaction in transactions if "Сумма операции" in transaction]

        # Сортируем транзакции по 'Сумма операции'
        sorted_transactions_list = sorted(valid_transactions, key=lambda x: abs(x["Сумма операции"]), reverse=True)

        # Берем топ-5 транзакций
        top_5 = sorted_transactions_list[:5]

        # Создаем список для возврата
        result = []
        for transaction in top_5:
            result.append(
                {
                    "Дата операции": transaction["Дата операции"],
                    "Сумма операции": round(transaction["Сумма операции"], 2),  # округляем сумму
                    "Описание": transaction["Описание"],
                }
            )

        return result

    except Exception as e:
        logger.exception("Ошибка в функции top_5_transactions: %s", e)
        raise ValueError("При работе функции top_5_transactions произошла ошибка.")


def load_user_settings(file_name: str = "user_settings.json") -> Dict[str, Any]:
    """Загрузка настроек пользователя из JSON файла"""
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            settings = json.load(f)
            logger.info("Настройки пользователя загружены")
            return settings
    except Exception as e:
        logger.exception("Ошибка при загрузке настроек пользователя")
        return {"error": f"Ошибка при загрузке настроек: {e}"}


def get_currency_rate(file_name: str = "user_settings.json") -> List[Dict[str, Any]]:
    """Получение курса валют согласно настройкам пользователя"""
    settings = load_user_settings(file_name)
    logger.info("Начало работы функции get_currency_rate")

    url = "https://www.cbr-xml-daily.ru/daily_json.js"  # URL для получения курса валют
    logger.info("Запрос информации с сайта курса валют функции get_currency_rate")

    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверяем успешность запроса

        data = response.json()
        currency_rates = []

        for currency in settings.get("user_currencies", []):
            if currency in data["Valute"]:
                rate = data["Valute"][currency]["Value"]
                currency_rates.append({"currency": currency, "rate": rate})
            else:
                currency_rates.append({"currency": currency, "rate": None, "error": "Курс не найден"})

        logger.info("Корректный ответ функции get_currency_rate")
        return currency_rates

    except requests.exceptions.RequestException as e:
        logger.exception("Ошибка в функции get_currency_rate")
        return [{"error": f"Ошибка при выполнении запроса: {e}"}]
    except KeyError as e:
        logger.exception("Ошибка в функции get_currency_rate")
        return [{"error": f"Ошибка при извлечении данных: {e}"}]


def get_stock_prices(file_name: str = "user_settings.json") -> List[Dict[str, Any]]:
    """Получение цен акций согласно настройкам пользователя"""
    settings = load_user_settings(file_name)
    logger.info("Начало работы функции get_stock_prices")

    load_dotenv()  # Загружаем переменные окружения
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")  # Получаем API-ключ из .env

    stocks = settings.get("user_stocks", [])  # Список тикеров акций из настроек
    stock_prices = []

    for stock in stocks:  # Проходим по каждому тикеру для получения цены акций
        try:
            logger.info("Запрос из внешнего источника на акции для функции get_stock_prices")
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key}"
            response = requests.get(url)
            response.raise_for_status()  # Проверяем успешность запроса

            data = response.json()

            if "Global Quote" in data and "05. price" in data["Global Quote"]:
                price = float(data["Global Quote"]["05. price"])
                stock_prices.append({"stock": stock, "price": price})
            else:
                stock_prices.append({"stock": stock, "price": None, "error": "Данные не найдены"})

        except requests.exceptions.RequestException as e:
            logger.exception("Ошибка в функции get_stock_prices")
            stock_prices.append({"stock": stock, "price": None, "error": f"Ошибка при выполнении запроса: {e}"})
        except (KeyError, ValueError) as e:
            logger.exception("Ошибка в функции get_stock_prices")
            stock_prices.append({"stock": stock, "price": None, "error": f"Ошибка при извлечении данных: {e}"})

    logger.info("Корректный ответ функции get_stock_prices")
    return stock_prices
