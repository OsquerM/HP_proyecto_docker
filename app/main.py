from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# Calculamos la ruta base del proyecto (subimos dos niveles desde main.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# 🔹 Crear la app
app = FastAPI(title="Harry Potter Quiz")

# 🔹 Carpeta static y templates (rutas absolutas → mucho más seguro)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "templates")

# 🔹 Importar routers
from app.quiz import quiz_router
from app.admin import admin_router

app.include_router(quiz_router)
app.include_router(admin_router)

# 🔹 Base de datos y modelos
from app.database import engine, Base
from app import models
Base.metadata.create_all(bind=engine)

# 🔹 Rutas principales
@app.get("/", response_class=HTMLResponse)
def leer_inicio(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/index", response_class=HTMLResponse)
def mostrar_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/quiz", response_class=HTMLResponse)
def mostrar_quiz(request: Request):
    return templates.TemplateResponse("quiz.html", {"request": request})