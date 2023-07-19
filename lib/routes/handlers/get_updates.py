from lib.db_objects import GetUpdatesMessage, Message
from fastapi import WebSocket, Depends
from lib import sql_connect as conn
from lib.routes.socket_resp import SocketRespGetUpdates


async def handler_get_updates(msg: dict, db: Depends, websocket: WebSocket):
    socket_resp = SocketRespGetUpdates()
    update_msg = GetUpdatesMessage.parse_obj(msg)
    socket_resp.update_message(update_msg)

    # Проверяем права доступа на сообщение
    owner_id = await conn.get_token(db=db, token_type='refresh', token=update_msg.refresh_token)
    print('owner', owner_id)
    if not owner_id:
        await websocket.send_json(socket_resp.response_401)
        return True
    all_message = []
    users_chats = await conn.get_users_chats(db=db, user_id=owner_id[0][0])
    print('users_chats', users_chats)
    for chat in users_chats:
        messages = await conn.get_users_messages_by_last_msg(db=db, lust_msg_id=update_msg.lust_msg_id, chat_id=chat[0])

        for one in messages:
            print('messages', one)
            new_msg = Message()
            new_msg.msg_from_db(one)
            print(new_msg.text)
            all_message.append(new_msg.dict())

    print(len(all_message), all_message)
    await websocket.send_json(socket_resp.get_message(all_message))
    return True
