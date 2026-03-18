from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import httpx
import random
from fastapi import APIRouter

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

# ────────────────────────────────────────────────
# Conexión a HP-API pública 
# ────────────────────────────────────────────────


externa_router = APIRouter(prefix="/api-externa", tags=["API Externa"])

@externa_router.get("/personaje/{casa}")
async def personaje_por_casa(casa: str):
    """
    Devuelve un personaje aleatorio de la casa indicada usando HP-API pública.
    Ejemplo: /api-externa/personaje/gryffindor
    """
    casa_lower = casa.lower()
    url = f"https://hp-api.onrender.com/api/characters/house/{casa_lower}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            personajes = response.json()

            if not personajes:
                return {"mensaje": f"No hay personajes conocidos de {casa}"}

            # Elegimos uno al azar
            personaje = random.choice(personajes)

            return {
                "nombre": personaje.get("name", "Desconocido"),
                "especie": personaje.get("species", "Humano"),
                "actor": personaje.get("actor", "Desconocido"),
                "imagen": personaje.get("image", None),
                "casa": personaje.get("house", casa)
            }
        except httpx.HTTPStatusError as e:
            return {"error": f"Error al conectar con HP-API ({e.response.status_code})"}
        except Exception as e:
            return {"error": f"Error inesperado: {str(e)}"}

# Añadimos el router de la API externa
app.include_router(externa_router)