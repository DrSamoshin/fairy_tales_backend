from enum import Enum


class OrderPaymentMethod(str, Enum):
    cash = "cash"
    card = "card"
