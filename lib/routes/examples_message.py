example_text_message = {
    'access_token': 'fnriverino',
    'msg_client_id': 12,
    'msg_type': 'chat_message',
    'body': {
        'msg_id': 2132,
        'text': 'Text of this message',
        'from_id': 32,
        'reply_id': 342,
        'chat_id': 65,
        'file_id': 0,
        'status': 'not_read',
        'read_date': 0,
        'deleted_date': 0,
        'create_date': 124321412,
    }
}

example_get_updates_message = {
    'refresh_token': 'fnriverino',
    'msg_type': 'chat_message',
    "date_time": 123,
    'from_id': 32,
    'lust_msg_id': 65,
}

example_delete_message = {
    'refresh_token': 'fnriverino',
    'msg_type': 'delete_msg',
    "date_time": 123,
    'chat_id': 32,
    'delete_msg_id': 65,
}