from fastapi import FastAPI, Form, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from backend import models, database
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


app = FastAPI(title="Resume Project")

from fastapi import WebSocket, WebSocketDisconnect

# لیست کاربران آنلاین
active_connections: list[WebSocket] = []

# مدیریت اتصال‌ها
async def connect(ws: WebSocket):
    await ws.accept()
    active_connections.append(ws)

def disconnect(ws: WebSocket):
    active_connections.remove(ws)

async def broadcast(message: str):
    for connection in active_connections:
        await connection.send_text(message)

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await connect(ws)
    try:
        # ارسال تعداد اولیه
        await broadcast(str(len(active_connections)))
        while True:
            # نگه داشتن اتصال فعال (می‌توانیم پیام‌ها را هم دریافت کنیم)
            data = await ws.receive_text()
    except WebSocketDisconnect:
        disconnect(ws)
        await broadcast(str(len(active_connections)))


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

frontend_path = Path(__file__).parent.parent / "frontend"


app.mount("/static", StaticFiles(directory=frontend_path), name="static")


templates = Jinja2Templates(directory="frontend")


models.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------- یوزر ادمین -------------------
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

# ------------------- فرم رزومه -------------------
from pydantic import BaseModel

class RequestCreate(BaseModel):
    name: str
    email: str
    project_type: str
    project_desc: str

@app.post("/submit")
def submit_request(request: RequestCreate, db: Session = Depends(get_db)):
    new_request = models.Request(
        name=request.name,
        email=request.email,
        project_type=request.project_type,
        project_desc=request.project_desc
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return {"message": "Request submitted successfully!", "id": new_request.id}





# ------------------- صفحه login -------------------
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and password == ADMIN_PASS:
        response = RedirectResponse(url="/admin", status_code=302)
        # ست کردن کوکی ساده برای احراز هویت
        response.set_cookie(key="admin", value="true")
        return response
    return HTMLResponse("<h2>Invalid username or password</h2>")

# ------------------- صفحه admin -------------------

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse



@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request, db: Session = Depends(get_db)):
   
    if request.cookies.get("admin") != "true":
        return RedirectResponse(url="/login")

    requests_list = db.query(models.Request).all()
    return templates.TemplateResponse("admin.html", {"request": request, "requests": requests_list})

@app.post("/accept/{request_id}")
def accept_request(request_id: int, db: Session = Depends(get_db)):
    req = db.query(models.Request).filter(models.Request.id == request_id).first()
    if req:
        req.status = "accepted"  
        db.commit()
        return JSONResponse(content={"message": "Request accepted"})
    return JSONResponse(status_code=404, content={"message": "Request not found"})


@app.delete("/delete/{request_id}")
def delete_request(request_id: int, db: Session = Depends(get_db), request: Request = None):
    # چک کردن کوکی
    if request.cookies.get("admin") != "true":
        return HTMLResponse("Unauthorized", status_code=401)

    req = db.query(models.Request).filter(models.Request.id == request_id).first()
    if req:
        db.delete(req)
        db.commit()
        return {"message": "Deleted"}
    return {"message": "Request not found"}

