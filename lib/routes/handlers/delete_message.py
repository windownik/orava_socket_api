import datetime
import time

from lib.db_objects import DeleteMsg
from fastapi import WebSocket, Depends
from lib import sql_connect as conn
from lib.routes.connection_manager import ConnectionManager
from lib.routes.socket_resp import SocketRespGetUpdates


async def handler_delete_msg(msg: dict, db: Depends, websocket: WebSocket, manager: ConnectionManager):
    del_msg = DeleteMsg.parse_obj(msg)
    socket_resp = SocketRespGetUpdates()

    # Проверяем права доступа на сообщение
    owner_id = await conn.get_token(db=db, token_type='refresh', token=del_msg.refresh_token)
    if not owner_id:
        await websocket.send_json(socket_resp.response_401)
        return True
    print('check user')
    await conn.update_data(db=db, table='messages', name='status', data='delete', id_name='msg_id',
                           id_data=del_msg.delete_msg_id)
    now = datetime.datetime.now()
    await conn.update_data(db=db, table='messages', name='deleted_date', data=int(time.mktime(now.timetuple())),
                           id_name='msg_id', id_data=del_msg.delete_msg_id)
    print("update to delete")
    all_users = await conn.read_data(table='users_chat', id_name='chat_id', id_data=del_msg.chat_id, db=db)

    await manager.broadcast_all_in_chat(body=del_msg.dict(), users_in_chat=all_users)
    return True
