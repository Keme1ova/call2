### 📁 main.py — FastAPI сервер ###

from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from firebase_config import auth
import uuid

app = FastAPI()

# Подключение статики и шаблонов
app.mount("/static", StaticFiles(directory="public"), name="static")
templates = Jinja2Templates(directory="public")

# Сохраняем активные WebSocket-соединения
active_connections = {}

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/login")
def login(email: str = Form(...), password: str = Form(...)):
    try:
        user = auth.get_user_by_email(email)
        return RedirectResponse(url=f"/call?uid={user.uid}", status_code=302)
    except:
        return HTMLResponse("Пользователь не найден", status_code=401)

@app.post("/register")
def register(email: str = Form(...), password: str = Form(...)):
    try:
        user = auth.create_user(email=email, password=password)
        return RedirectResponse(url=f"/call?uid={user.uid}", status_code=302)
    except:
        return HTMLResponse("Ошибка при регистрации", status_code=400)

@app.get("/call", response_class=HTMLResponse)
def call_ui(request: Request, uid: str):
    return templates.TemplateResponse("main.html", {"request": request, "uid": uid})

@app.websocket("/ws/{uid}")
async def websocket_endpoint(websocket: WebSocket, uid: str):
    await websocket.accept()
    active_connections[uid] = websocket
    try:
        while True:
            data = await websocket.receive_json()
            target = data.get("to")
            if target in active_connections:
                await active_connections[target].send_json({"from": uid, "data": data["data"]})
    except WebSocketDisconnect:
        del active_connections[uid]