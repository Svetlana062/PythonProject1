import pytest

from src.services import date_sorting, investment_bank, limit_payment  # Импортируем функции из src


def test_limit_payment() -> None:
    """Тестирование функции limit_payment."""
    assert limit_payment(50, -120) == -150
    assert limit_payment(50, -75) == -100
    assert limit_payment(50, 0) == 0
    assert limit_payment(50, 75) == 75  # Положительные значения игнорируются
    assert limit_payment(50, -20) == -50  # Тест на сумму, которая меньше лимита


@pytest.fixture
def mock_transactions():
    """Тестовая фикстура с транзакциями."""
    return [
        {"Дата операции": "01.01.2023 00:00:00", "Сумма операции": -100},
        {"Дата операции": "15.02.2023 00:00:00", "Сумма операции": -200},
        {"Дата операции": "20.03.2023 00:00:00", "Сумма операции": -150},
        {"Дата операции": "25.03.2023 00:00:00", "Сумма операции": -50},
    ]


def test_date_sorting(mock_transactions):
    """Тест функции сортировки."""
    result = date_sorting("2023-03", mock_transactions)
    assert len(result) == 2  # Ожидается 2 транзакции в марте


def test_date_sorting_no_transactions(mock_transactions):
    """Тестирование сортировки по дате."""
    result = date_sorting("2022-04", mock_transactions)
    assert len(result) == 0  # Ожидаем 0 транзакций


def test_investment_bank(mock_transactions):
    """Тестирование копилки."""
    result = investment_bank("2023-03", mock_transactions, 50)
    expected_result = '{"Investment Bank": 0.0}'
    assert result == expected_result


def test_investment_bank_with_different_limit(mock_transactions):
    """Тестирование округления потраченной суммы по заданному лимиту"""
    result = investment_bank("2023-03", mock_transactions, 30)
    expected_result = '{"Investment Bank": 10.0}'  # Пример ожидаемого результата
    assert result == expected_result
