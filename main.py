from src.reports import load_transactions_from_excel, spending_by_category
from src.services import investment_bank
from src.utils import read_transactions_from_excel
from src.views import views

"""Запуск всех функций из одного модуля"""
if __name__ == "__main__":
    transaction_info = read_transactions_from_excel(
        "data/operations.xlsx",
    )
    transaction_df = load_transactions_from_excel("data/operations.xlsx")
    print(views(transaction_info, "20.05.2020"))
    print("\n###################\n")
    print(investment_bank("2021-10", transaction_info, 50))
    print("\n###################\n")
    print((spending_by_category(transaction_df, "Супермаркеты", "12.11.2021")))
