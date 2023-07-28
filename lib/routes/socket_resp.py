from lib.db_objects import ReceiveMessage, GetUpdatesMessage, Message


class SocketRespMsg:
    receive_msg: ReceiveMessage = None
    response_200: dict[str, int | bool | str]
    response_401: dict[str, int | bool | str]
    response_400_rights: dict[str, int | bool | str]

    def __init__(self):
        self.response_400_not_check = {"ok": False,
                                       'status_code': 400,
                                       "msg_type": "system",
                                       'desc': 'not check message'}

    def update_message(self, receive_msg: ReceiveMessage, msg_body: dict):
        self.receive_msg = receive_msg

        self.response_401 = {"ok": False,
                             'status_code': 401,
                             'msg_client_id': receive_msg.msg_client_id,
                             "msg_type": "system",
                             'desc': 'bad access'}

        self.response_401 = {"ok": False,
                             'status_code': 400,
                             'msg_client_id': receive_msg.msg_client_id,
                             "msg_type": "system",
                             'desc': 'not enough rights'}

        self.response_200 = {"ok": True,
                             'status_code': 200,
                             "msg_type": "send_message",
                             'desc': 'save and send to user',
                             "body": msg_body
                             }

    def response_201_confirm_receive(self, msg_data: dict):
        return {"ok": True,
                'status_code': 201,
                'msg_client_id': self.receive_msg.msg_client_id,
                'msg_server_id': msg_data['msg_id'],
                "msg_type": "delivery",
                'desc': 'success receive'}

    def response_202_save_file(self, msg_data: dict, file_id: int):
        return {"ok": True,
                'status_code': 202,
                'msg_client_id': self.receive_msg.msg_client_id,
                'msg_server_id': msg_data['msg_id'],
                'file_id': file_id,
                "msg_type": "file_delivery",
                'desc': 'success receive'}


class SocketRespGetUpdates:
    receive_msg: GetUpdatesMessage = None
    response_401: dict[str, int | bool | str]
    response_400_rights: dict[str, int | bool | str]

    def __init__(self):
        self.response_400_not_check = {"ok": False,
                                       'status_code': 400,
                                       "msg_type": "system",
                                       'desc': 'not check message'}

    def update_message(self, receive_msg: GetUpdatesMessage):
        self.receive_msg = receive_msg

        self.response_401 = {"ok": False,
                             'status_code': 401,
                             "msg_type": "system",
                             'desc': 'bad refresh'}

        self.response_401 = {"ok": False,
                             'status_code': 400,
                             "msg_type": "system",
                             'desc': 'not enough rights'}

    def get_message(self, msg_data: list):
        print('create')
        return {"ok": True,
                'status_code': 200,
                "msg_type": "send_updates",
                'to_user_id': self.receive_msg.from_id,
                "messages": msg_data
                }
