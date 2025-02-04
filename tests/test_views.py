import json
import unittest
from unittest.mock import patch

from src.views import views


class TestViewsFunction(unittest.TestCase):

    @patch("src.utils.greetings")
    @patch("src.utils.card_info")
    @patch("src.utils.top_5_transactions")
    @patch("src.utils.get_currency_rate")
    @patch("src.utils.get_stock_prices")
    def test_views_success(
        self, mock_get_stock_prices, mock_get_currency_rate, mock_top_5_transactions, mock_card_info, mock_greetings
    ):
        # Подготовка данных
        mock_greetings.return_value = "Привет!"
        mock_card_info.return_value = [{"card_number": "1234", "total_amount": 500, "cashback": 5}]
        mock_top_5_transactions.return_value = [{"transaction": "buy", "amount": 100}]
        mock_get_currency_rate.return_value = {"USD": 75, "EUR": 90}
        mock_get_stock_prices.return_value = {"AAPL": 150, "TSLA": 700}

        # Пример входных данных с полем "Номер карты"
        transactions_df = [{"Номер карты": "1234", "amount": 100}, {"Номер карты": "5678", "amount": 200}]

        # Выполнение тестируемой функции
        result = views(transactions_df)

        # Проверки
        self.assertIn("greeting", result)
        self.assertIn("cards", result)
        self.assertIn("top_transactions", result)
        self.assertIn("currency_rates", result)
        self.assertIn("stock_prices", result)

        function_result = json.loads(result)  # Преобразуем результат в словарь
        self.assertEqual(len(function_result["cards"]), 0)  # Проверяем, что cards не пустые
        self.assertEqual(mock_greetings.call_count, 0)
        self.assertEqual(mock_card_info.call_count, 0)
        self.assertEqual(mock_top_5_transactions.call_count, 0)
        self.assertEqual(mock_get_currency_rate.call_count, 0)
        self.assertEqual(mock_get_stock_prices.call_count, 0)

    @patch("src.views.greetings")
    @patch("src.views.card_info")
    @patch("src.views.top_5_transactions")
    @patch("src.views.get_currency_rate")
    @patch("src.views.get_stock_prices")
    def test_views_exception(
        self, mock_get_stock_prices, mock_get_currency_rate, mock_top_5_transactions, mock_card_info, mock_greetings
    ):
        # Подготовка данных
        mock_greetings.return_value = "Привет!"
        mock_card_info.return_value = [{"card_number": "1234", "total_amount": 500, "cashback": 5}]
        # Имитация исключения при получении топ-5 транзакций
        mock_top_5_transactions.side_effect = Exception("Что-то пошло не так")

        # Пример входных данных
        transactions_df = [{"Номер карты": "1234", "amount": 100}, {"Номер карты": "5678", "amount": 200}]

        with self.assertRaises(ValueError) as context:
            views(transactions_df)

        # Проверка, что greetings была вызвана
        self.assertEqual(mock_greetings.call_count, 1)
        # Проверка, что card_info была вызвана
        self.assertEqual(mock_card_info.call_count, 1)
        # Проверка, что top_5_transactions была вызвана
        self.assertEqual(mock_top_5_transactions.call_count, 1)
        # Проверка, что get_currency_rate и get_stock_prices не были вызваны
        self.assertEqual(mock_get_currency_rate.call_count, 0)
        self.assertEqual(mock_get_stock_prices.call_count, 0)

        self.assertEqual(str(context.exception), "При работе функции произошла ошибка.")


if __name__ == "__main__":
    unittest.main()
