
from lib.db_objects import ChangeMsg, Message, User
from fastapi import WebSocket, Depends
from lib import sql_connect as conn
from lib.routes.connection_manager import ConnectionManager
from lib.routes.handlers.get_updates import add_user_and_reply_to_msg
from lib.routes.socket_resp import SocketRespGetUpdates


async def handler_change_msg(msg: dict, db: Depends, websocket: WebSocket, manager: ConnectionManager,
                             reqwest_user: User):
    change_msg = Message.parse_obj(msg['message'])
    socket_resp = SocketRespGetUpdates()

    # Проверяем права доступа на сообщение
    owner_id = await conn.get_token(db=db, token_type='refresh', token=msg['refresh_token'])
    if not owner_id:
        await websocket.send_json(socket_resp.response_401)
        return True
    print('check user')
    await conn.update_msg(db=db, msg=change_msg)
    print("update message")
    msg_data = await conn.read_data(table='messages', id_name='msg_id', id_data=change_msg.msg_id, db=db)
    print(change_msg.msg_id, msg_data)
    new_msg = Message.parse_obj(msg_data[0])
    msg_json = await add_user_and_reply_to_msg(db=db, msg=new_msg, reqwest_user=reqwest_user)
    all_users = await conn.read_data(table='users_chat', id_name='chat_id', id_data=change_msg.chat_id, db=db)

    await manager.broadcast_all_in_chat(body={
        "status_code": 200,
        "msg_type": "change_msg",
        "message": msg_json
    }, users_in_chat=all_users)

    return True
