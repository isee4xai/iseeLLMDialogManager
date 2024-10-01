import uvicorn
import asyncio

from http import client
from typing import List, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import business.coordinator as c

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://dialog-dev.isee4xai.com/ws/${client_id}`);
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


class ConnectionManager():
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.coordinators: Dict[str, c.Coordinator] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.coordinators[client_id] = c.Coordinator(client_id, self.active_connections[client_id])

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)

    async def start(self, client_id: str, init_data: object):
        self.coordinators[client_id].reset()
        self.coordinators[client_id].init(init_data)
        await self.coordinators[client_id].start()


manager = ConnectionManager()


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
            init_data = await websocket.receive_json()
            await manager.start(client_id, init_data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    print("Starting server")
    uvicorn.run(app, host="0.0.0.0", port=8000)