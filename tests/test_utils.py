from unittest import mock

import pytest

from src.utils import (
    card_info,
    get_currency_rate,
    get_stock_prices,
    greetings,
    load_user_settings,
    read_transactions_from_excel,
    top_5_transactions,
)


@pytest.mark.parametrize(
    "mock_hour, expected_greeting",
    [
        (0, "Доброй ночи"),  # 00:00 - 05:59
        (5, "Доброй ночи"),
        (6, "Доброе утро"),  # 06:00 - 11:59
        (10, "Доброе утро"),
        (12, "Добрый день"),  # 12:00 - 17:59
        (15, "Добрый день"),
        (18, "Добрый вечер"),  # 18:00 - 23:59
        (20, "Добрый вечер"),
        (23, "Добрый вечер"),
    ],
)
def test_greetings(mock_hour, expected_greeting, mocker):
    """Патчируем datetime для тестирования разных временных интервалов"""
    mock_datetime = mocker.patch("src.utils.datetime")
    mock_datetime.now.return_value.hour = mock_hour
    # Проверяем, что функция greetings возвращает правильное приветствие
    assert greetings() == expected_greeting


def test_read_transactions_from_excel(mocker):
    """Тестируем функцию на чтение xlsx-файла"""
    mocker.patch(
        "pandas.read_excel",
        return_value=mocker.Mock(to_dict=lambda orient: [{"Номер карты": "****1234", "Сумма операции": -100}]),
    )
    transactions = read_transactions_from_excel("dummy.xlsx")
    assert len(transactions) == 1
    assert transactions[0]["Номер карты"] == "****1234"


def test_card_info():
    """Тестирует вывод информации в соответствии с картой"""
    transactions = [{"Номер карты": "*5678", "Сумма операции": -200}]
    result = card_info(transactions)
    assert len(result) == 1
    assert result[0]["last_digits"] == "5678"  # Проверяем последние 4 цифры
    assert result[0]["total_spent"] == -200
    assert result[0]["cashback"] == 2.0


def test_top_5_transactions():
    """Тестирует, выводит ли функция 5 самых крупных транзакций"""
    transactions = [
        {"Дата операции": "2023-01-01", "Сумма операции": -100, "Категория": "Food", "Описание": "Dinner"},
        {"Дата операции": "2023-01-02", "Сумма операции": -50, "Категория": "Transport", "Описание": "Taxi"},
        {"Дата операции": "2023-01-03", "Сумма операции": -150, "Категория": "Groceries", "Описание": "Supermarket"},
        {"Дата операции": "2023-01-04", "Сумма операции": -200, "Категория": "Health", "Описание": "Medicine"},
        {"Дата операции": "2023-01-05", "Сумма операции": -25, "Категория": "Entertainment", "Описание": "Concert"},
        {"Дата операции": "2023-01-06", "Сумма операции": -30, "Категория": "Food", "Описание": "Takeout"},
    ]
    result = top_5_transactions(transactions)
    assert len(result) == 5


def test_load_user_settings(mocker):
    """Проверяет чтение файла шаблона для курса валют"""
    mock_open = mock.mock_open(read_data='{"user_currencies": ["USD", "EUR"]}')
    with mock.patch("builtins.open", mock_open):
        settings = load_user_settings("dummy_settings.json")
        assert settings["user_currencies"] == ["USD", "EUR"]


def test_get_currency_rate(mocker):
    """Тестирует получение курса валют"""
    mock_settings = {"user_currencies": ["USD", "EUR"]}
    mock_load_user_settings = mock.patch("src.utils.load_user_settings", return_value=mock_settings).start()
    mock_response = mock.Mock()
    mock_response.json.return_value = {"Valute": {"USD": {"Value": 70.0}, "EUR": {"Value": 80.0}}}
    mocker.patch("requests.get", return_value=mock_response)

    result = get_currency_rate()
    assert len(result) == 2
    assert result[0]["currency"] == "USD"
    assert result[0]["rate"] == 70.0

    mock_load_user_settings.stop()


def test_get_stock_prices(mocker):
    """Тестирует получение цен на акции"""
    mock_settings = {"user_stocks": ["AAPL", "GOOGL"]}
    mock_load_user_settings = mock.patch("src.utils.load_user_settings", return_value=mock_settings).start()

    mock_response = mock.Mock()
    mock_response.json.return_value = {"Global Quote": {"05. price": "150.00"}}
    mocker.patch("requests.get", return_value=mock_response)
    mocker.patch("src.utils.os.getenv", return_value="dummy_api_key")

    result = get_stock_prices()
    assert len(result) == 2
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == 150.0

    mock_load_user_settings.stop()


if __name__ == "__main__":
    pytest.main()
