import os
import sys
import json
from typing import Optional

from flask import Blueprint, render_template, request, url_for, redirect, jsonify

from flask_login import login_required, current_user

from flask_socketio import SocketIO, join_room

from model import User, Chat, Message, File, ContentType, UserType

from utils import FileManager
from auth import AuthenticationManager, load_user
from .ChatManager import ChatManager
import re

sys.path.append('..')

chat_bp = Blueprint('chat_bp', __name__,
                    static_folder='static', template_folder='templates')

socketio = SocketIO(cors_allowed_origins="*")
file_mgr = FileManager(os.getenv('UPLOAD_FOLDER'))

CLEANR = re.compile('<.*?>')


def text_only(raw_html):
    clean_text = re.sub(CLEANR, '', raw_html)
    return clean_text


@chat_bp.route('/')
@login_required
def message():
    return render_template('messages.html', text_only=text_only)


@chat_bp.route('/<user_id>')
@login_required
def initiate_message(user_id):
    if current_user.user_type == UserType.EMPLOYER:
        chat_mgr = ChatManager(current_user.id)

        if User.get(user_id):
            chat_mgr.initiate_chat(user_id)

    return redirect(url_for('chat_bp.message'))


@chat_bp.route('/', methods=['POST'])
def get_messages():
    user_token = request.json.get("authentication_token")
    user = load_user(user_token)

    if not user:
        return ""

    chat_id = request.json.get('chat_id')
    chat = Chat.get(chat_id)

    if not chat:
        return ""

    result = []
    for message in chat.messages:
        if message.content_type == ContentType.TEXT:
            result.append({
                "id": message.id,
                "content": message.content,
                "content_type": message.content_type,
                "timestamp": message.time_stamp,
                "sent": user.id == message.sender_id
            })

        elif message.content_type == ContentType.FILE:
            file = File.get(message.content)
            if file:
                result.append({
                    "id": message.id,
                    "file_name": file.file_name,
                    "file_link": url_for('files', id=file.id),
                    "content_type": message.content_type,
                    "timestamp": message.time_stamp,
                    "sent": user.id == message.sender_id
                })

    return jsonify(result)


@chat_bp.route('/uploadfile', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return ""

    file = request.files['file']
    if file and file.filename:
        file_id = file_mgr.save(file)
        return json.dumps({'status': 'success', 'file_id': file_id})

    return json.dumps({'status': 'failure'})


@socketio.on('join')
def handle_join(data):
    token = data.get('authentication_token', '')
    user: User = load_user(token)

    if user:
        chat_ids = [chat.id for chat in user.chats]

        for chat_id in chat_ids:
            join_room(chat_id)
        join_room(user.id)

        socketio.emit('online_announcement',
                      {
                          'user_id': user.id
                      },
                      rooms=chat_ids)


@socketio.on('send_message')
def handle_message(data):
    token = data.get('authentication_token', '')
    user = load_user(token)

    if not user:
        return

    message = data["message"]
    chat_id = data['chat_id']

    chat = Chat.get(int(chat_id))
    chat_mgr = ChatManager(user.id)

    if not chat:
        return

    chat_mgr.send_message(chat_id, message)
    socketio.emit('receive_message', rooms=chat_id)


@socketio.on('send_file')
def handle_file(data):
    token = data.get('authentication_token', '')
    user = load_user(token)

    if not user:
        return

    file_id = data["file_id"]
    chat_id = data['chat_id']

    chat = Chat.get(int(chat_id))
    chat_mgr = ChatManager(user.id)

    file = File.get(file_id)

    if not (chat and file):
        return

    chat_mgr.send_message(chat_id, file.id,
                          content_type=ContentType.FILE)
    socketio.emit('receive_message', rooms=chat_id)


@socketio.on('event')
def handle_event(data):
    pass
