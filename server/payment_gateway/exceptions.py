class TransactionException(Exception):
    """Exception class for payment related errors"""

    def __init__(self, message):
        super().__init__(self, message)


class InsufficientBalance(TransactionException):
    """Balance is insufficient for specified transaction."""

    def __init__(self, message="Balance is insufficient for specified transaction."):
        super().__init__(self, message)


class InvalidCurrency(TransactionException):
    """Unsupported currency"""

    def __init__(self, message="Unsupported currency"):
        super().__init__(self, message)
