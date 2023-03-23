from abc import ABC, abstractmethod
import requests
from .exceptions import *


class PaymentHandler(ABC):
    """Abstract base class for all payment handlers"""

    def __init__(self, use_sandbox=True):
        """
        Args:
            use_sandbox (bool): initializes payment handler in test/production mode
                (default is True (test mode))
        """

        self.use_sandbox = use_sandbox

    @abstractmethod
    def generate_checkout_url(self, data: dict) -> str:
        pass

    @abstractmethod
    def verify_transaction(self, data: dict) -> bool:
        pass

    @abstractmethod
    def send_payment(self, data: dict):
        pass


class ChapaPaymentHandler(PaymentHandler):
    """PaymentHandler subclass using Chapa as payment provider"""

    API_VERSION = 'v1'

    BASE_URL = 'https://api.chapa.co'
    PAYMENT_URL = f'{BASE_URL}/{API_VERSION}/transaction/initialize'
    VERIFICATION_URL = f'{BASE_URL}/{API_VERSION}/transaction/verify'
    TRANSFER_URL = f'{BASE_URL}/{API_VERSION}/transfers'

    def __init__(self, secret_key, use_sandbox=True):
        """
        Args:
            secret_key (str): secret key provided by Chapa            
            use_sandbox (bool): initializes payment handler in test/production mode
                (default is True (test mode))
        """

        PaymentHandler.__init__(self, use_sandbox=use_sandbox)

        self.headers = {'Authorization': f'Bearer {secret_key}'}

    def __validate_data(self, data: dict) -> None:
        """Raises TransactionException if supplied data is not complient with
        what Chapa API expects

        Args:
            data (dict): key value pairs expected to be send to Chapa API

        Raises:
            KeyError: if one of expected keys is missing in data
            TransactionException: if value of data is invalid
        """

        expected_keys = ['amount', 'currency', 'email', 'first_name',
                         'last_name', 'tx_ref', 'callback_url', 'return_url']

        for key in expected_keys:
            if not data.get(key):
                raise KeyError(f'{key} is missing in transaction data')

        if data['currency'] != 'ETB':
            raise InvalidCurrency

        try:
            if float(data['amount']) <= 0:
                raise TransactionException("amount must be greater than 0")

        except TypeError:
            raise TransactionException("amount must be valid number")

    def generate_checkout_url(self, data: dict) -> str:
        """Generates checkout url that users can use for payment

        Args:
            data (dict): transaction data as key value pairs expected by Chapa API

        Returns:
            str: checkout url
        """

        self.__validate_data(data)

        response = requests.post(self.PAYMENT_URL,
                                 data=data, headers=self.headers)

        response_json = response.json()
        print(response_json)

        if response_json['status'] == 'success':
            return response_json['data']['checkout_url']

    def verify_transaction(self, transaction_reference: str) -> bool:
        response = requests.get(
            f"{self.VERIFICATION_URL}/{transaction_reference}", headers=self.headers)

        try:
            return response.json()["status"] == "success"
        except:
            return False

    def get_transaction_data(self, transaction_reference: str) -> bool:
        response = requests.get(
            f"{self.VERIFICATION_URL}/{transaction_reference}", headers=self.headers)

        try:
            return response.json()['data']
        except:
            return False

    def send_payment(self, data: dict):
        """
        Sends payment to specified account        
        """

        if self.use_sandbox:
            return True

        response = requests.post(
            self.TRANSFER_URL, data=data, headers=self.headers)
        return response.text

    def _get_banks(self):
        response = requests.get(
            "https://api.chapa.co/v1/banks", headers=self.headers)
        return response.json()


if __name__ == '__main__':
    import os
    from dotenv import load_dotenv
    load_dotenv()

    handler = ChapaPaymentHandler(os.getenv('CHAPA_SECRET_KEY'))

    ref = 'tx-234'
    checkout_url = handler.generate_checkout_url({
        'amount': '100',
        'currency': 'ETB',
        'email': 'rak373429@gmail.com',
        'first_name': 'Abebe',
        'last_name': 'Bikila',
        'tx_ref': ref,
        'callback_url': 'http://localhost:5000',
        'return_url': 'http://localhost:5000/login',
        'customization[title]': 'Freelancers',
        'customization[description]': 'Send payment'
    })
    print(checkout_url)

    print(handler.verify_transaction(ref))

    # data = {
    #     'account_name': 'Israel Goytom',
    #     'account_number': '1000012345678',
    #     'amount': '20',
    #     'currency': 'ETB',
    #     'beneficiary_name': 'Abe Kebe',
    #     'reference': '3241342142sfdd',
    #     'bank_code': 'f48ecb7a-6fd8-45bb-9ae1-5de7b6962b0d'
    # }

    # banks = handler._get_banks()['data']
    # print("\n".join([f"{bank['id']}, {bank['name']}"
    #       for bank in banks]))
    # print(banks)
    # print(handler.send_payment(data))
