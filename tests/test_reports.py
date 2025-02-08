import unittest

import pandas as pd

from src.reports import spending_by_category


class TestSpendingByCategory(unittest.TestCase):

    def setUp(self) -> None:
        """Создание тестового DataFrame для тестов."""
        self.data = {
            "Дата платежа": ["01.11.2021", "15.11.2021", "29.11.2021", "12.12.2021"],
            "Категория": ["Супермаркеты", "Кафе", "Супермаркеты", "Супермаркеты"],
            "Сумма": [100, 200, 150, 50],
        }
        self.df = pd.DataFrame(self.data)

    def test_spending_by_category(self) -> None:
        """Проверка получения трат по категории."""
        result = spending_by_category(self.df, "Супермаркеты", "12.12.2021")
        expected = [
            {"Дата платежа": "2021-11-01", "Категория": "Супермаркеты", "Сумма": "100"},
            {"Дата платежа": "2021-11-29", "Категория": "Супермаркеты", "Сумма": "150"},
            {"Дата платежа": "2021-12-12", "Категория": "Супермаркеты", "Сумма": "50"},
        ]
        self.assertEqual(result, expected)

    def test_spending_by_category_no_transactions(self) -> None:
        """Проверка, когда нет транзакций по категории."""
        result = spending_by_category(self.df, "Книги", "12.12.2021")
        expected = []
        self.assertEqual(result, expected)

    def test_spending_by_category_no_dates(self) -> None:
        """Проверка, когда указана дата, но нет подходящих транзакций."""
        result = spending_by_category(self.df, "Супермаркеты", "01.10.2021")
        expected = []
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
