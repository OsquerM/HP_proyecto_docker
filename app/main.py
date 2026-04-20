from pathlib import Path                              # Manejo de rutas multiplataforma
from fastapi import FastAPI, Request, APIRouter       # FastAPI: framework principal, Request: recibe peticiones HTTP, APIRouter: agrupa rutas
from fastapi.staticfiles import StaticFiles           # Sirve archivos estáticos (CSS, JS, imágenes)
from fastapi.templating import Jinja2Templates        # Motor de plantillas para renderizar HTML
from fastapi.responses import HTMLResponse            # Indica que la respuesta es HTML
import httpx                                          # Cliente HTTP asíncrono para llamar a APIs externas
import random                                         # Para elegir un personaje aleatorio de la lista

# Calculamos la ruta base del proyecto subiendo dos niveles
# desde main.py → /app/app/main.py → /app/app/ → /app/
BASE_DIR = Path(__file__).resolve().parent.parent

# Creamos la aplicación FastAPI con su título
# Es el objeto principal que gestiona todas las rutas y peticiones
app = FastAPI(title="Harry Potter Quiz")

# Configuramos la carpeta de archivos estáticos (CSS, JS, imágenes)
# Cualquier petición a /static/... buscará el archivo en BASE_DIR/static/
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Configuramos el motor de plantillas Jinja2
# Apunta a la carpeta templates/ donde están los archivos HTML
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Importamos y registramos los routers de quiz y admin
# Se importan aquí y no arriba para evitar importaciones circulares:
# quiz.py y admin.py necesitan que 'app' esté creada antes de importarse
# Sin include_router las rutas de esos archivos no existirían en la app
from app.quiz import quiz_router
from app.admin import admin_router

app.include_router(quiz_router)   # registra todas las rutas de /quiz
app.include_router(admin_router)  # registra todas las rutas de /admin

# Crea las tablas en MariaDB si no existen
# Lee los modelos (Usuario, Pregunta, Respuesta) y genera el SQL necesario
# Se importa aquí para asegurarse de que la app esté lista antes
from app.database import engine, Base
from app import models
Base.metadata.create_all(bind=engine)

# RUTAS PRINCIPALES
# response_class=HTMLResponse indica que la respuesta es HTML

@app.get("/", response_class=HTMLResponse)
def leer_inicio(request: Request):
    # Página de inicio → renderiza index.html
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/quiz", response_class=HTMLResponse)
def mostrar_quiz(request: Request):
    # Página del quiz → renderiza quiz.html
    return templates.TemplateResponse(request=request, name="quiz.html")

# CONEXIÓN A HP-API PÚBLICA
# Router separado para la integración con la API externa de Harry Potter
# Todas las rutas empiezan por /api-externa
externa_router = APIRouter(prefix="/api-externa", tags=["API Externa"])

@externa_router.get("/personaje/{casa}")
async def personaje_por_casa(casa: str):
    """
    Devuelve un personaje aleatorio de la casa indicada usando HP-API pública.
    Ejemplo: /api-externa/personaje/gryffindor
    """
    # Convertimos la casa a minúsculas para la URL de la API
    casa_lower = casa.lower()
    url = f"https://hp-api.onrender.com/api/characters/house/{casa_lower}"

    # httpx.AsyncClient es el cliente HTTP asíncrono
    # Mientras espera la respuesta de la API, el servidor puede atender otras peticiones
    async with httpx.AsyncClient() as client:
        try:
            # Hacemos la petición GET a la API con timeout de 10 segundos
            response = await client.get(url, timeout=10.0)

            # Si la API devuelve un error HTTP, lanza una excepción
            response.raise_for_status()

            # Convertimos la respuesta JSON a lista de Python
            personajes = response.json()

            # Si la API no devuelve personajes para esa casa
            if not personajes:
                return {"mensaje": f"No hay personajes conocidos de {casa}"}

            # Elegimos un personaje al azar de la lista
            personaje = random.choice(personajes)

            # Devolvemos solo los campos que nos interesan
            # .get("name", "Desconocido") → si no existe el campo, usa "Desconocido"
            return {
                "nombre": personaje.get("name", "Desconocido"),
                "especie": personaje.get("species", "Humano"),
                "actor": personaje.get("actor", "Desconocido"),
                "imagen": personaje.get("image", None),
                "casa": personaje.get("house", casa)
            }
        except httpx.HTTPStatusError as e:
            # Error específico de HTTP (ej: 404, 500 de la API externa)
            return {"error": f"Error al conectar con HP-API ({e.response.status_code})"}
        except Exception as e:
            # Cualquier otro error inesperado (timeout, sin conexión, etc.)
            return {"error": f"Error inesperado: {str(e)}"}

# Registramos el router de la API externa en la app
app.include_router(externa_router)