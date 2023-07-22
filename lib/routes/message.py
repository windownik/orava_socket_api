import json

from starlette.websockets import WebSocketDisconnect
from fastapi import WebSocket, Depends
from fastapi.responses import HTMLResponse
from lib import sql_connect as conn

from lib.app_init import app
from lib.db_objects import User
from lib.routes.check_message import msg_manager
from lib.routes.connection_manager import manager
from lib.sql_connect import data_b

'127.0.0.1:8000'
"45.82.68.203:10020"

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://45.82.68.203:10020/ws/1");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@data_b.on_init
async def initialization(connect):
    # you can run your db initialization code here
    await connect.execute("SELECT 1")


@app.get("/ws_chat", tags=['Chat'])
async def get():
    return HTMLResponse(html)


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db=Depends(data_b.connection)):
    await manager.connect(websocket, user_id=user_id)
    user_data = await conn.read_data(db=db, name='*', table='all_users', id_name='user_id', id_data=user_id)
    user = User.parse_obj(user_data[0])
    print('Connect', manager.connections.keys())
    # Очищаем пуш метки
    await conn.clear_users_chat_push(db=db, user_id=user_id)
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            await conn.update_user_active(db=db, user_id=user_id)
            data = json.loads(data)
            if 'echo' in data.keys():
                data["user_id"] = user_id
                # await manager.connect(websocket, user_id=user_id)
                await websocket.send_json(str(data))
                continue
            check = await msg_manager(data, db=db, websocket=websocket, manager=manager, user=user)

            if not check:
                continue
    except WebSocketDisconnect:
        await manager.disconnect(user_id=user_id)
    except Exception as ex:
        print('Exception', ex)
    finally:
        print('finally', user_id)
        try:
            await manager.disconnect(user_id)
        except:
            pass
