import os
import sys
from typing import Any, Optional

from itsdangerous.url_safe import URLSafeTimedSerializer
from itsdangerous.exc import BadSignature, SignatureExpired
from werkzeug.security import check_password_hash

from model import User

sys.path.append('..')


class AuthenticationManager:
    """Class used to manage user authentication"""

    def __init__(self, key: str, max_age: int = 604800) -> None:
        """
        Args:
            key (str): An encryption key
            max_age (int): The maximum life time of single authentication token in seconds 
                (default is 604800 seconds or 7 days)
        """

        self.max_age = max_age
        self.serilizer = URLSafeTimedSerializer(key)

    def generate_auth_token(self, data: Any) -> str:
        """
        Generates signed authentication token for given data

        Args:
            data (Any): the data to serialize

        Returns:
            str: a signed string that can later be loaded
        """

        return self.serilizer.dumps(data)

    def verify_token(self, token: str) -> Any:
        """
        Verifies and loads authentication token generated by serilizer

        Args:
            token (str): authentication token to verify

        Returns:
            Any: data from token if the token is valid, None otherwise        
        """

        try:
            data = self.serilizer.loads(token, max_age=self.max_age)
            return data
        except BadSignature:
            return None
        except SignatureExpired:
            return None

    def verify_credentials(self, email: str, password: str) -> bool:
        """
        Verifies the existance of given credentials on database

        Args:
            email (str): email of user
            password (str): password of user

        Returns:
            bool: True if email and password are valid, False otherwise
        """

        user = User.get_by_email(email)
        if not user:
            return False

        return check_password_hash(user.password, password)


def load_user(token: str, secret_key=os.getenv('FLASK_SECRET_KEY')) -> Optional[User]:
    """
    Validates user token and loads user from database if user token is valid

    Args:
        token (str): a user token generated by AuthenticationManager

    Returns:
        User: the user object for which the token belongs if the token is valid, None otherwise
    """

    auth_manager = AuthenticationManager(secret_key)
    user_id = auth_manager.verify_token(token)

    if user_id:
        user = User.get(user_id)
        if user.token == token:
            return user
