from lib.db_objects import GetUpdatesMessage, Message, User
from fastapi import WebSocket, Depends
from lib import sql_connect as conn
from lib.routes.handlers.fancs import create_file_json
from lib.routes.socket_resp import SocketRespGetUpdates


async def handler_get_updates(msg: dict, db: Depends, websocket: WebSocket, reqwest_user: User):
    socket_resp = SocketRespGetUpdates()
    update_msg = GetUpdatesMessage.parse_obj(msg)
    socket_resp.update_message(update_msg)

    # Проверяем права доступа на сообщение
    owner_id = await conn.get_token(db=db, token_type='refresh', token=update_msg.refresh_token)
    if not owner_id:
        await websocket.send_json(socket_resp.response_401)
        return True
    all_message = []
    users_chats = await conn.get_users_chats(db=db, user_id=owner_id[0][0])
    for chat in users_chats:
        messages = await conn.get_users_messages_by_last_msg(db=db, lust_msg_id=update_msg.lust_msg_id, chat_id=chat[0])

        for one in messages:
            new_msg = Message.parse_obj(one)
            msg_json = await add_user_and_reply_to_msg(db=db, msg=new_msg, reqwest_user=reqwest_user)
            all_message.append(msg_json)

    await websocket.send_json(socket_resp.get_message(all_message))
    return True


async def add_user_and_reply_to_msg(db: Depends, msg: Message, reqwest_user: User) -> dict:

    await msg.add_user_to_msg(reqwest_user=reqwest_user, db=db)

    msg_dict = msg.dict()
    msg_dict = await add_file_to_dict(msg_dict=msg_dict, msg=msg, db=db)

    if msg.reply_id != 0:
        reply_msg_data = await conn.read_data(db=db, table='messages', id_name='msg_id', id_data=msg.reply_id)
        reply_msg: Message = Message.parse_obj(reply_msg_data[0])
        await reply_msg.add_user_to_msg(reqwest_user=reqwest_user, db=db)

        msg_dict['reply'] = reply_msg.dict()
    return msg_dict


async def add_file_to_dict(msg_dict: dict, msg: Message, db: Depends,) -> dict:
    if msg.file_id == 0:
        return msg_dict
    file = await conn.read_data(db=db, table='files', id_name='id', id_data=msg.file_id, name='*')
    resp = create_file_json(file[0])
    msg_dict['file'] = resp
    return msg_dict
