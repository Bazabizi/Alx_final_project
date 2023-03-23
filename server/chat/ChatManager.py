import sys
from model import db, Message, Chat, ContentType
sys.path.append('..')


class ChatManager:
    """
    Manages user chat

    Parameters:
        user_id (str): unique user id
    """

    def __init__(self, user_id: str):
        self.user_id = user_id

    def initiate_chat(self, receiver_id: str) -> str:
        """
        Create new chat between two users

        Args:
            receiver_id: the second user in the chat

        Returns: 
            str: the created chat id
        """

        if Chat.get_chat(self.user_id, receiver_id):
            return

        chat = Chat(user_1=self.user_id, user_2=receiver_id)

        db.session.add(chat)
        db.session.commit()

        return chat.id

    def send_message(self, chat_id: str, content: str, content_type: str = ContentType.TEXT):
        """
        Save message under chat_id

        Args:
            chat_id (str): chat containing two users
            sender_id (str): the user id of sender of the message
            content (str): the message sent
            content_type (str): specifies how to interpret the content
                (default is 'TEXT')
        """

        msg = Message(chat_id=chat_id,
                      sender_id=self.user_id,
                      content=content,
                      content_type=content_type)

        db.session.add(msg)
        db.session.commit()
