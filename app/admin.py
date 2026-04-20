from pathlib import Path                                        # Manejo de rutas multiplataforma (Windows, Linux, Mac)
from fastapi import (
    APIRouter,      # Agrupa rutas bajo un prefijo (/admin)
    Form,           # Lee datos enviados desde formularios HTML
    UploadFile,     # Tipo Maneja archivos subidos (imágenes)
    File,           # Indica que un parámetro es un archivo (como debe leer los archivos)
    Request,        # Recibe las peticiones HTTP
    Depends,        # Inyección de dependencias (ej: verificar autenticación)
    HTTPException,  # Lanza errores HTTP (404, 400, 500...)
    status,         # Constantes de códigos HTTP
    Cookie          # Lee el valor de una cookie de la petición
)
from fastapi.responses import RedirectResponse                  # Redirige al usuario a otra URL
from fastapi.templating import Jinja2Templates                  # Renderiza HTML con variables dinámicas
from sqlalchemy.orm import Session                              # Sesión de BD para hacer consultas
from passlib.context import CryptContext                        # Cifrado y verificación de contraseñas con bcrypt
from app import models                                          # Modelos de la BD (Usuario, Pregunta, Respuesta)
from app.database import get_db                                 # Función que gestiona la sesión de BD
import shutil                                                   # Operaciones con archivos (copiar imagen al disco)
import os                                                       # Interacción con el sistema operativo
import uuid                                                     # Genera nombres de archivo únicos para las imágenes y evitar duplicaciones


# Rutas base del proyecto 
# Así funciona tanto en local como dentro del contenedor Docker
# resolve ruta absoluta
#parent sube el nivel de jerarquia para que base dir apunte a la raiz del proyecto 
#Obtenemos la carpeta raíz
BASE_DIR = Path(__file__).resolve().parent.parent

# Motor de plantillas Jinja2 apuntando a la carpeta templates
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Carpeta donde se guardan las imágenes subidas por el admin
# mkdir con parents=True y exist_ok=True la crea si no existe
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Conjunto de casas válidas para validar las respuestas
VALID_HOUSES = {"Gryffindor", "Slytherin", "Ravenclaw", "Hufflepuff"}

# Contexto de cifrado bcrypt para hashear y verificar contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#Logueo en caso futuro
def hash_password(password: str) -> str:
    """Devuelve la contraseña cifrada con bcrypt"""
    return pwd_context.hash(password)
#Cuando hacemos login compara la contraseña que introducimos con el hash 
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara la contraseña en texto plano con la hasheada"""
    return pwd_context.verify(plain_password, hashed_password)


# Router de administración: todas las rutas empiezan por /admin
#prefix define el prefijo para usar en todas las rutas y tags es una etiqueta que agrupa las rutas

admin_router = APIRouter(prefix="/admin", tags=["admin"])

def get_current_admin(admin_logged_in: str | None = Cookie(None)):
    """
    Dependencia de seguridad: verifica que el usuario está autenticado
    comprobando el valor de la cookie 'admin_logged_in'.
    Si no está autenticado, redirige al login con error 303.
    """
    if admin_logged_in != "true":
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/admin/login"}
        )
    return True


# LOGIN
#async def permite que el servidor atienda otras peticiones mientras espera la respuesta de algo lento (BD, API, disco...).

@admin_router.get("/login")
async def login_form(request: Request):
    """Muestra el formulario de login"""
    return templates.TemplateResponse("login.html", {"request": request})

@admin_router.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Procesa el login del administrador:
    - Busca el usuario en la BD con rol 'admin'
    - Verifica la contraseña con bcrypt
    - Si es correcto, crea una cookie de sesión y redirige al panel
    - Si falla, redirige al login con mensaje de error
    """
    admin = db.query(models.Usuario).filter_by(nombre=username, rol="admin").first()
    if not admin or not verify_password(password, admin.password):
        return RedirectResponse("/admin/login?error=credenciales_invalidas", status_code=303)

    response = RedirectResponse("/admin", status_code=303)
    response.set_cookie(
        key="admin_logged_in",
        value="true",          # Valor que verifica get_current_admin y se guarda en la cookie 
        httponly=True,         # No accesible desde JavaScript, evita inyección maliciosa
        secure=False,  
        samesite="lax",        # Protección contra CSRF, evita  que una web maliciosa haga peticiones a la app usando las cookies de usuarios
        max_age=86400          # La cookie expira en 24 horas
    )
    return response

@admin_router.get("/logout")
async def logout(_ = Depends(get_current_admin)):
    """Cierra la sesión del admin eliminando la cookie"""
    response = RedirectResponse("/admin/login", status_code=303)
    response.delete_cookie("admin_logged_in")
    return response


# PANEL PRINCIPAL


@admin_router.get("")
async def mostrar_admin(
    request: Request,
    db: Session = Depends(get_db),
    _ = Depends(get_current_admin)  # Protege la ruta: solo admins autenticados
):
    """
    Muestra el panel de administración con todas las preguntas
    ordenadas de más reciente a más antigua (ORDER BY id DESC)
    """
    preguntas = db.query(models.Pregunta).order_by(models.Pregunta.id.desc()).all()
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "preguntas": preguntas}
    )


# AGREGAR PREGUNTA


@admin_router.post("/agregar_pregunta")
async def agregar_pregunta(
    #El form(...) hace que la respuesta sea obligatoria, hacemos que la foto sea opcional y si no se sube ningun archivo el valor por defecto es none
    texto_pregunta: str = Form(...),
    respuesta1: str = Form(...), casa1: str = Form(...), imagen1: UploadFile | None = File(None),
    respuesta2: str = Form(...), casa2: str = Form(...), imagen2: UploadFile | None = File(None),
    respuesta3: str = Form(...), casa3: str = Form(...), imagen3: UploadFile | None = File(None),
    respuesta4: str = Form(...), casa4: str = Form(...), imagen4: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    _ = Depends(get_current_admin)
):
    """
    Crea una nueva pregunta con sus 4 respuestas en la BD.
    Para cada respuesta:
    - Valida que la casa sea una de las 4 válidas
    - Si se sube imagen, valida el tipo MIME y la guarda con nombre UUID
    - Guarda la ruta relativa en la BD (uploads/nombre.ext)
    """
    #Si esta vacío entra al if
    if not texto_pregunta.strip():
        raise HTTPException(400, "La pregunta no puede estar vacía")
    #RAISE para la ejecución y nos devuelve el error 
    # Creamos la pregunta y hacemos flush para obtener su ID sin hacer commit aún
    pregunta = models.Pregunta(texto_pregunta=texto_pregunta.strip())
    db.add(pregunta)
    db.flush()  # manda la pregunta a la BD temporalmente y le asignamos la id 

    # Agrupamos las 4 respuestas en una lista de tuplas para procesarlas en bucle
    respuestas_info = [
        (respuesta1.strip(), casa1, imagen1),
        (respuesta2.strip(), casa2, imagen2),
        (respuesta3.strip(), casa3, imagen3),
        (respuesta4.strip(), casa4, imagen4),
    ]

    for texto, casa, archivo in respuestas_info:
        # Saltamos respuestas vacías
        if not texto:
            continue

        # Validamos que la casa sea válida
        if casa not in VALID_HOUSES:
            db.rollback() #deshace los cambios 
            raise HTTPException(400, f"Casa no válida: {casa}. Usa una de: {', '.join(VALID_HOUSES)}")

        ruta_bd = None
        if archivo and archivo.filename and archivo.filename.strip():
            content_type = archivo.content_type or ""

            # Lista de tipos MIME de imagen permitidos
            allowed_types = {
                "image/jpeg", "image/jpg", "image/png", "image/gif",
                "image/webp", "image/avif", "image/heic", "image/heif",
                "image/bmp", "image/tiff", "image/tif", "image/svg+xml",
            }

            if not content_type.startswith("image/") or content_type not in allowed_types:
                db.rollback()
                raise HTTPException(400, f"Tipo de archivo no permitido: {content_type}.")

            # Generamos nombre único con UUID para evitar colisiones
            extension = Path(archivo.filename).suffix # suffix hace que saquemos lo que hay detrás del punto ej : .jpg
            nombre_archivo = f"{uuid.uuid4().hex}{extension}" # uuid Genera un identificador único aleatorio y hex lo convierte a texto sin guiones
            ruta_guardado = UPLOAD_DIR / nombre_archivo # construimos la ruta completa donde se guardará la imagen en disco

            try:
                # Abrimos el archivo en disco en modo escritura binaria
                # wb = binario para archivos como imágenes
                
                with ruta_guardado.open("wb") as f:
                    # Copiamos la imagen subida por el usuario al disco
                    shutil.copyfileobj(archivo.file, f)
                
                # Guardamos la ruta relativa en BD 
                ruta_bd = f"uploads/{nombre_archivo}"

            except Exception as e:
                # Si algo falla, deshacemos los cambios en BD y devolvemos error
                db.rollback()
                raise HTTPException(500, f"Error al guardar imagen: {str(e)}")

        # Creamos el objeto Respuesta y lo añadimos a la sesión
        respuesta = models.Respuesta(
            texto_respuesta=texto,
            casa=casa,
            imagen=ruta_bd,
            pregunta_id=pregunta.id
        )
        db.add(respuesta)

    # Confirmamos todos los cambios en la BD
    db.commit()
    return RedirectResponse("/admin?success=pregunta_agregada", status_code=303)


# EDITAR PREGUNTA


@admin_router.get("/editar_pregunta/{pregunta_id}")
async def editar_pregunta_form(
    pregunta_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _ = Depends(get_current_admin)
):
    """Muestra el formulario de edición con los datos actuales de la pregunta"""
    pregunta = db.query(models.Pregunta).filter_by(id=pregunta_id).first()
    if not pregunta:
        raise HTTPException(404, "Pregunta no encontrada")

    return templates.TemplateResponse(
        "editar_pregunta.html",
        {"request": request, "pregunta": pregunta}
    )

@admin_router.post("/actualizar_pregunta/{pregunta_id}")
async def actualizar_pregunta(
    pregunta_id: int,
    texto_pregunta: str = Form(...),
    respuesta1: str = Form(...), casa1: str = Form(...), imagen1: UploadFile | None = File(None),
    respuesta2: str = Form(...), casa2: str = Form(...), imagen2: UploadFile | None = File(None),
    respuesta3: str = Form(...), casa3: str = Form(...), imagen3: UploadFile | None = File(None),
    respuesta4: str = Form(...), casa4: str = Form(...), imagen4: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    _ = Depends(get_current_admin)
):
    """
    Actualiza una pregunta existente y sus 4 respuestas.
    - Modifica directamente los objetos Respuesta existentes (no los borra y recrea)
    - Si no se sube imagen nueva, conserva la imagen anterior automáticamente
    - Si se sube imagen nueva, la guarda con nombre UUID y actualiza la ruta en BD
    """
    pregunta = db.query(models.Pregunta).filter_by(id=pregunta_id).first()
    if not pregunta:
        raise HTTPException(404, "Pregunta no encontrada")

    if not texto_pregunta.strip():
        raise HTTPException(400, "La pregunta no puede estar vacía")

    # Actualizamos el texto de la pregunta
    pregunta.texto_pregunta = texto_pregunta.strip()

    # Obtenemos las respuestas actuales de la pregunta
    respuestas_actuales = pregunta.respuestas
    if len(respuestas_actuales) != 4:
        raise HTTPException(400, "Se esperan exactamente 4 respuestas")

    # Emparejamos cada conjunto de datos con su respuesta actual en BD
    respuestas_info = [
        (respuesta1.strip(), casa1, imagen1, respuestas_actuales[0]),
        (respuesta2.strip(), casa2, imagen2, respuestas_actuales[1]),
        (respuesta3.strip(), casa3, imagen3, respuestas_actuales[2]),
        (respuesta4.strip(), casa4, imagen4, respuestas_actuales[3]),
    ]

    for texto, casa, archivo, respuesta_actual in respuestas_info:
        if not texto:
            continue

        if casa not in VALID_HOUSES:
            raise HTTPException(400, f"Casa no válida: {casa}")

        # Actualizamos texto y casa de la respuesta
        respuesta_actual.texto_respuesta = texto
        respuesta_actual.casa = casa

        # Solo procesamos la imagen si se subió una nueva
        if archivo and archivo.filename and archivo.filename.strip():
            content_type = archivo.content_type or ""
            allowed_types = {
                "image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp",
                "image/avif", "image/heic", "image/heif", "image/bmp", "image/tiff",
                "image/svg+xml"
            }

            if not content_type.startswith("image/") or content_type not in allowed_types:
                raise HTTPException(400, f"Tipo no permitido: {content_type}.")

            # Nombre limpio: UUID + extensión, sin acumular nombres
            extension = Path(archivo.filename).suffix
            nombre_archivo = f"{uuid.uuid4().hex}{extension}"
            ruta_guardado = UPLOAD_DIR / nombre_archivo

            try:
                with ruta_guardado.open("wb") as f:
                    shutil.copyfileobj(archivo.file, f)
                respuesta_actual.imagen = f"uploads/{nombre_archivo}"
            except Exception as e:
                raise HTTPException(500, f"Error guardando imagen: {str(e)}")
        # Si no se sube imagen nueva, se conserva la antigua automáticamente
        # porque no tocamos respuesta_actual.imagen

    db.commit()
    return RedirectResponse("/admin?success=pregunta_actualizada", status_code=303)


# ELIMINAR


@admin_router.post("/eliminar_pregunta")
async def eliminar_pregunta(
    pregunta_id: int = Form(...),
    db: Session = Depends(get_db),
    _ = Depends(get_current_admin)
):
    """
    Elimina una pregunta y todas sus respuestas de la BD.
    El cascade 'all, delete-orphan' del modelo se encarga de borrar
    las respuestas asociadas automáticamente.
    """
    pregunta = db.query(models.Pregunta).filter_by(id=pregunta_id).first()
    if not pregunta:
        raise HTTPException(404, "Pregunta no encontrada")

    db.delete(pregunta)
    db.commit()
    return RedirectResponse("/admin?success=pregunta_eliminada", status_code=303)

@admin_router.post("/eliminar_respuesta")
async def eliminar_respuesta(
    respuesta_id: int = Form(...),
    db: Session = Depends(get_db),
    _ = Depends(get_current_admin)
):
    """Elimina una respuesta individual sin borrar la pregunta completa"""
    respuesta = db.query(models.Respuesta).filter_by(id=respuesta_id).first()
    if not respuesta:
        raise HTTPException(404, "Respuesta no encontrada")

    db.delete(respuesta)
    db.commit()
    return RedirectResponse("/admin?success=respuesta_eliminada", status_code=303)