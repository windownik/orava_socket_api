from typing import List, Any

from fastapi import WebSocket
from lib import sql_connect as conn

from lib.db_objects import Message, ReceiveMessage


class ConnectionManager:
    def __init__(self):
        self.connections: dict = {int: WebSocket}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.connections[user_id] = websocket

    async def disconnect(self, user_id: int):
        self.connections.pop(user_id)

    async def broadcast(self, data: dict):
        for connect in self.connections:
            await connect.send_json(data)

    async def broadcast_dialog(self, body: dict, users_in_chat: tuple, msg: ReceiveMessage) -> list[Any]:
        user_id_list = self.connections.keys()
        users_for_push = []
        print(111, len(users_in_chat), self.connections.keys())
        for user in users_in_chat:
            print(user['user_id'])
            if user['user_id'] == msg.body.from_id:
                continue
            if user['user_id'] in user_id_list:
                connect = self.connections[user['user_id']]
                await connect.send_json(body)
            else:
                if user['push_sent']:
                    continue
                else:
                    users_for_push.append(user)
        return users_for_push


manager = ConnectionManager()
