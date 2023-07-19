from lib.db_objects import ReceiveMessage
from lib.routes.connection_manager import ConnectionManager
from fastapi import WebSocket, Depends
from lib import sql_connect as conn
from lib.routes.socket_resp import SocketRespMsg


async def handler_chat_message(msg: dict, db: Depends, user_id: int, websocket: WebSocket,
                               manager: ConnectionManager, socket_resp: SocketRespMsg):

    receive_msg = ReceiveMessage.parse_obj(msg)
    socket_resp.update_message(receive_msg)

    # Проверяем права доступа на сообщение
    owner_id = await conn.get_token(db=db, token_type='access', token=receive_msg.access_token)

    if not owner_id:
        await websocket.send_json(socket_resp.response_401)
        return True

    msg_id = await conn.save_msg(db=db, msg=msg['body'])

    msg['body']['msg_id'] = msg_id[0][0]

    receive_msg = ReceiveMessage.parse_obj(msg)
    socket_resp.update_message(receive_msg)

    # отправляем подтверждение о доставке и сохранении
    await websocket.send_json(socket_resp.response_201_confirm_receive)

    user_in_chat = await conn.check_user_in_chat(db=db, user_id=user_id, chat_id=receive_msg.body.chat_id)
    if not user_in_chat:
        await websocket.send_json(socket_resp.response_400_rights)
        return True

    all_users = await conn.read_data(table='users_chat', id_name='chat_id',
                                     id_data=receive_msg.body.chat_id, db=db)

    push_users = await manager.broadcast_dialog(users_in_chat=all_users, body=socket_resp.response_200, msg=receive_msg)
    for user in push_users:
        print('push for', user['user_id'])
        await conn.update_users_chat_push(db=db, chat_id=receive_msg.body.chat_id, user_id=user['user_id'])
        await conn.save_push_to_sending(db=db, msg_id=receive_msg.body.chat_id, push_type='text',
                                        title=f'Новое сообщение',
                                        short_text='У вас новое сообщение в чате: ', user_id=user['user_id'])