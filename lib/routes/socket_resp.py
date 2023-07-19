
from lib.db_objects import ReceiveMessage

class SocketResp:
    receive_msg: ReceiveMessage = None
    response_200: dict[str, int | bool | str]
    response_401: dict[str, int | bool | str]
    response_400_rights: dict[str, int | bool | str]
    response_201_confirm_receive: dict[str, int | bool | str]

    def __init__(self):
        self.response_400_not_check = {"ok": False,
                                       'status_code': 400,
                                       "msg_type": "system",
                                       'desc': 'not check message'}

    def update_message(self, receive_msg: ReceiveMessage):
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

        self.response_201_confirm_receive = {"ok": True,
                                             'status_code': 201,
                                             'msg_client_id': receive_msg.msg_client_id,
                                             'msg_server_id': receive_msg.body.msg_id,
                                             "msg_type": "delivery",
                                             'desc': 'success receive'}

        self.response_200 = {"ok": True,
                             'status_code': 200,
                             "msg_type": "send_message",
                             'desc': 'save and send to user',
                             "body": self.receive_msg.body.dict()
                             }