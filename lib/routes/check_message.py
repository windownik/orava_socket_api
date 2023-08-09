from fastapi import WebSocket, Depends

from lib.db_objects import User
from lib.routes.connection_manager import ConnectionManager
from lib.routes.examples_message import example_text_message, example_get_updates_message, example_delete_message
from lib.routes.handlers.chat_message import handler_chat_message
from lib.routes.handlers.delete_message import handler_delete_msg
from lib.routes.handlers.get_updates import handler_get_updates
from lib.routes.socket_resp import SocketRespMsg


def check_msg(msg: dict, main_message: dict):
    for key in main_message.keys():
        if key not in msg.keys():
            return False
    if 'body' not in main_message.keys():
        return True

    for key in main_message['body'].keys():
        if key not in msg['body'].keys():
            return False
    return True


async def msg_manager(msg: dict, db: Depends, user: User, websocket: WebSocket,
                      manager: ConnectionManager):
    # Определяем тип сообщения
    socket_resp = SocketRespMsg()
    if msg['msg_type'] == 'send_msg':
        print('send_msg')
        # Проверяем структуру сообщения по шаблону example_text_message
        if not check_msg(msg, example_text_message):
            await websocket.send_json(socket_resp.response_400_not_check)
            return True
        await handler_chat_message(msg=msg, db=db, user=user, websocket=websocket, manager=manager,
                                   socket_resp=socket_resp)
    # Определяем тип сообщения
    elif msg['msg_type'] == 'get_updates':
        print('get_updates')
        # Проверяем структуру сообщения по шаблону example_get_updates_message
        if not check_msg(msg, example_get_updates_message):
            await websocket.send_json(socket_resp.response_400_not_check)
            return True
        await handler_get_updates(db=db, msg=msg, websocket=websocket, reqwest_user=user)

    # Определяем тип сообщения
    elif msg['msg_type'] == 'delete_msg':
        print('delete_msg')
        # Проверяем структуру сообщения по шаблону example_get_updates_message
        if not check_msg(msg, example_delete_message):
            await websocket.send_json(socket_resp.response_400_not_check)
            return True
        print('check')
        await handler_delete_msg(db=db, msg=msg, websocket=websocket,  manager=manager)
