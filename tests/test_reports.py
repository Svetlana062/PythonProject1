import json
import os
from unittest import mock

import pytest

from src.reports import report_decorator, spending_by_category


@pytest.fixture
def mock_transactions():
    return [
        {"Дата операции": "01.01.2023 00:00:00", "Категория": "Супермаркеты", "Сумма операции": -100},
        {"Дата операции": "15.02.2023 00:00:00", "Категория": "Кафе", "Сумма операции": -200},
        {"Дата операции": "20.03.2023 00:00:00", "Категория": "Супермаркеты", "Сумма операции": -150},
        {"Дата операции": "25.03.2023 00:00:00", "Категория": "Книги", "Сумма операции": -50},
        {"Дата операции": "30.03.2023 00:00:00", "Категория": "Супермаркеты", "Сумма операции": -80},
    ]


def test_spending_by_category(mock_transactions):
    result = spending_by_category(mock_transactions, "Супермаркеты")

    assert len(result) == 3  # Ожидаем 3 транзакции по категории 'Супермаркеты'
    assert all(tx["Категория"] == "Супермаркеты" for tx in result)


def test_spending_by_category_no_transactions(mock_transactions):
    result = spending_by_category(mock_transactions, "Товары")

    assert len(result) == 0  # Ожидаем 0 транзакций по несуществующей категории


def test_spending_by_category_no_dates():
    result = spending_by_category([], "Супермаркеты")

    assert len(result) == 0  # Ожидаем 0 транзакций, так как нет данных


def test_report_decorator():
    # Проверяем функцию, которая будет декорироваться
    mock_function = mock.Mock(return_value={"result": "test_data"})
    wrapped_function = report_decorator("data/test_report.json")(mock_function)

    # Вызываем декорированную функцию
    result = wrapped_function()

    # Проверяем, что результат функции возвращается правильно
    assert result == {"result": "test_data"}

    # Проверяем, что mock_function была вызвана
    mock_function.assert_called_once()

    # Проверяем, что файл создался с правильными данными
    assert os.path.exists("data/test_report.json")  # Проверяем, существует ли файл

    with open("data/test_report.json", "r", encoding="utf-8") as f:
        saved_data = json.load(f)
        assert saved_data == {"result": "test_data"}  # Проверяем, что содержимое файла правильное

    # Удаляем созданный файл после теста
    os.remove("data/test_report.json")
