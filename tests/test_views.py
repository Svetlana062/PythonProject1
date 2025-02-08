import json
import unittest
from unittest.mock import patch

from src.views import views


class TestViews(unittest.TestCase):

    @patch("src.views.greetings")
    @patch("src.views.card_info")
    @patch("src.views.top_5_transactions")
    @patch("src.views.get_currency_rate")
    @patch("src.views.get_stock_prices")
    def test_views_success(
        self, mock_get_stock_prices, mock_get_currency_rate, mock_top_5_transactions, mock_card_info, mock_greetings
    ):
        # Подготовка данных
        mock_greetings.return_value = "Привет!"
        mock_card_info.return_value = [{"card_number": "1234", "total_amount": 500, "cashback": 5}]
        mock_top_5_transactions.return_value = [{"transaction": "buy", "amount": 100}]
        mock_get_currency_rate.return_value = {"USD": 75, "EUR": 90}
        mock_get_stock_prices.return_value = {"AAPL": 150, "TSLA": 700}

        transactions_df = [
            {"Дата операции": "01.11.2021 10:00:00", "Номер карты": "1234", "Сумма": 100},
            {"Дата операции": "15.11.2021 11:30:00", "Номер карты": "5678", "Сумма": 200},
            {"Дата операции": "29.11.2021 14:00:00", "Номер карты": "1234", "Сумма": 150},
            {"Дата операции": "12.12.2021 16:00:00", "Номер карты": "5678", "Сумма": 50},
        ]
        date = "12.12.2021"  # Дата в формате ДД.ММ.ГГГГ.

        result = views(transactions_df, date)

        # Проверки
        self.assertIsInstance(result, str)  # Ожидаем, что результат - строка (JSON)
        result_json = json.loads(result)  # Декодируем из JSON для дальнейшей проверки
        self.assertEqual(result_json["greeting"], "Привет!")
        self.assertIn("cards", result_json)
        self.assertIn("top_transactions", result_json)
        self.assertIn("currency_rates", result_json)
        self.assertIn("stock_prices", result_json)

    @patch("src.views.greetings")
    @patch("src.views.card_info")
    @patch("src.views.top_5_transactions")
    def test_views_exception(self, mock_top_5_transactions, mock_card_info, mock_greetings):
        # Мокаем функции, чтобы вызвать исключение
        mock_greetings.return_value = "Привет!"
        mock_card_info.return_value = [{"card_number": "1234", "total_amount": 500, "cashback": 5}]
        mock_top_5_transactions.side_effect = Exception("Что-то пошло не так")

        transactions_df = [{"Дата операции": "01.11.2021 10:00:00", "Номер карты": "1234", "Сумма": 100}]
        date = "12.12.2021"

        with self.assertRaises(ValueError) as context:
            views(transactions_df, date)

        self.assertEqual(str(context.exception), "При работе функции произошла ошибка.")


if __name__ == "__main__":
    unittest.main()
