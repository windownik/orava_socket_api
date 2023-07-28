import asyncio

from lib.db_objects import ReceiveMessage, Message, User
from lib.routes.connection_manager import ConnectionManager
from fastapi import WebSocket, Depends
from lib import sql_connect as conn
from lib.routes.handlers.get_updates import add_user_and_reply_to_msg
from lib.routes.socket_resp import SocketRespMsg


async def handler_chat_message(msg: dict, db: Depends, user: User, websocket: WebSocket,
                               manager: ConnectionManager, socket_resp: SocketRespMsg):
    receive_msg = ReceiveMessage.parse_obj(msg)
    socket_resp.update_message(receive_msg, msg)

    # Проверяем права доступа на сообщение
    owner_id = await conn.get_token(db=db, token_type='access', token=receive_msg.access_token)

    if not owner_id:
        await websocket.send_json(socket_resp.response_401)
        return True

    msg_data = await conn.save_msg(db=db, msg=msg['body'])

    new_msg = Message.parse_obj(msg_data[0])
    msg_json = await add_user_and_reply_to_msg(db=db, msg=new_msg, reqwest_user=user)
    receive_msg: ReceiveMessage = ReceiveMessage.parse_obj(msg)
    receive_msg.update_reply(msg)
    socket_resp.update_message(receive_msg, msg_json)
    user_in_chat = await conn.check_user_in_chat(db=db, user_id=user.user_id, chat_id=receive_msg.body.chat_id)
    if not user_in_chat:
        await websocket.send_json(socket_resp.response_400_rights)
        return True
    else:
        # отправляем подтверждение о доставке и сохранении
        await websocket.send_json(socket_resp.response_201_confirm_receive)

    all_users = await conn.read_data(table='users_chat', id_name='chat_id', id_data=receive_msg.body.chat_id, db=db)
    print(new_msg.status)
    if new_msg.status == 'with_file':
        file_id = 0
        i = 0
        while file_id == 0 and i < 20:
            i += 1
            await asyncio.sleep(3)
            print(file_id)
            file_id = (await conn.read_data(db=db, table='messages', name='file_id', id_name='msg_id',
                                            id_data=new_msg.msg_id))[0][0]
        receive_msg.body.file_id = file_id
        socket_resp.update_message(receive_msg, msg_json)
        await websocket.send_json(socket_resp.response_202_save_file)

    push_users = await manager.broadcast_dialog(users_in_chat=all_users, body=socket_resp.response_200, msg=receive_msg)
    for user in push_users:
        print('push for', user['user_id'])
        await conn.update_users_chat_push(db=db, chat_id=receive_msg.body.chat_id, user_id=user['user_id'])
        await conn.save_push_to_sending(db=db, msg_id=receive_msg.body.chat_id, push_type='text',
                                        title=f'Новое сообщение',
                                        short_text='У вас новое сообщение в чате: ', user_id=user['user_id'])
