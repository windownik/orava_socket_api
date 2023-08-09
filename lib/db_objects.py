import datetime

from fastapi import Depends
from pydantic import BaseModel

from lib import sql_connect as conn


class User(BaseModel):
    user_id: int
    name: str
    middle_name: str
    surname: str
    phone: int
    email: str
    image_link: str
    image_link_little: str
    description: str
    lang: str
    status: str
    last_active: int
    create_date: int


class File(BaseModel):
    file_id: int = 0
    file_type: str = '0'


class Chat(BaseModel):
    chat_id: int = 0
    owner_id: int = 0
    owner_user: User = None
    all_users_count: int = 0
    all_users: list = []
    community_id: int = 0
    name: str = '0'
    img_url: str = '0'
    little_img_url: str = '0'
    chat_type: str = 'dialog'
    status: str = '0'
    open_profile: bool = True
    send_media: bool = True
    send_voice: bool = True
    deleted_date: int = None
    create_date: int = None

    async def to_json(self, db: Depends,):
        users_data = await conn.get_users_in_chat(db=db, chat_id=self.chat_id)
        for one in users_data:
            user = User.parse_obj(one)
            self.all_users.append(user)
        users_count = (await conn.get_count_users_in_chat(db=db, chat_id=self.chat_id))[0][0]

        self.all_users_count = users_count

        user_data = await conn.read_data(table='all_users', id_name='user_id', id_data=self.owner_id, db=db)
        self.owner_user = User.parse_obj(user_data[0])

        resp = self.dict()
        unread_message = []
        unread_count = 0
        if self.status == 'delete':
            pass
        else:
            msg_data = await conn.get_users_unread_messages(db=db, chat_id=self.chat_id)
            unread_count = (await conn.get_users_unread_messages_count(db=db, chat_id=self.chat_id))[0][0]
            for one in msg_data:
                msg = Message.parse_obj(one)
                unread_message.append(msg.dict())

        resp.pop('owner_id')
        resp['unread_message'] = unread_message
        resp['unread_count'] = unread_count
        return resp


class Message(BaseModel):
    """
    msg_type: Может принимать значения 'new_message', 'system',
    """
    msg_id: int = 0
    client_msg_id: int = 0
    msg_type: str = 'new_message'
    text: str = '0'

    from_id: int = 0
    reply_id: int = 0
    chat_id: int = 0
    to_id: int = 0
    file_id: int = 0

    status: str = '0'
    read_date: int = 0
    deleted_date: int = 0
    create_date: int = 0

    sender: User = None

    def to_dialog(self):
        return {
            "msg_id": self.msg_id,
            "client_msg_id": self.client_msg_id,
            "msg_type": self.msg_type,
            "text": self.text,
            "from_id": self.from_id,
            "replay_id": self.reply_id,
            "chat_id": self.chat_id,
            "to_id": self.to_id,
            "file_id": self.file_id,
            "status": self.status,
            "read_date": self.read_date,
            "deleted_date": self.deleted_date,
            "create_date": self.create_date,
        }

    def update_msg_id(self, msg_id: int):
        self.msg_id = msg_id

    def update_user_sender(self, sender: User):
        self.sender = sender

    async def add_user_to_msg(self, db: Depends, reqwest_user: User):
        if self.from_id == reqwest_user.user_id:
            self.update_user_sender(reqwest_user)
        else:
            user_data = await conn.read_data(db=db, name='*', table='all_users', id_name='user_id',
                                             id_data=self.from_id)
            msg_send_user: User = User.parse_obj(user_data[0])
            self.update_user_sender(msg_send_user)


class Community(BaseModel):
    community_id: int = 0
    owner_user: User = None
    name: str = '0'
    main_chat: Chat = None
    join_code: str = '0'
    img_url: str = '0'
    little_img_url: str = '0'
    status: str = '0'
    open_profile: bool = True
    send_media: bool = True
    send_voice: bool = True
    deleted_date: datetime.datetime = None
    create_date: datetime.datetime = None


class ReceiveMessage(BaseModel):
    access_token: str = '0'
    msg_client_id: int = 0
    msg_type: str = '0'
    body: Message = None

    def update_reply(self, msg_data: dict):
        if 'reply' in msg_data.keys():
            reply_msg = Message.parse_obj(msg_data['reply'])
            self.body.reply = reply_msg


class GetUpdatesMessage(BaseModel):
    refresh_token: str = '0'
    msg_type: str = '0'
    date_time: int = 0
    from_id: int = 0
    chat_id: int = 0
    lust_msg_id: int = 0


class DeleteMsg(BaseModel):
    status_code: int
    refresh_token: str
    msg_type: str
    date_time: int
    chat_id: int
    delete_msg_id: int
