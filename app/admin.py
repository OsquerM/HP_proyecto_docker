from pathlib import Path
from fastapi import APIRouter, Form, UploadFile, File, Request, Depends, HTTPException, status, Cookie
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app import models
from app.database import get_db
import shutil
import os
import uuid

# Rutas base seguras (funciona en local y Docker)
BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(directory=BASE_DIR / "templates")

UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

VALID_HOUSES = {"Gryffindor", "Slytherin", "Ravenclaw", "Hufflepuff"}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

admin_router = APIRouter(prefix="/admin", tags=["admin"])

# ✅ CORREGIDO: compara con "true" (igual que lo que guarda el login)
def get_current_admin(admin_logged_in: str | None = Cookie(None)):
    if admin_logged_in != "true":
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/admin/login"}
        )
    return True

# Login form
@admin_router.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Procesar login
@admin_router.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    admin = db.query(models.Usuario).filter_by(nombre=username, rol="admin").first()
    if not admin or not verify_password(password, admin.password):
        return RedirectResponse("/admin/login?error=credenciales_invalidas", status_code=303)

    response = RedirectResponse("/admin", status_code=303)
    response.set_cookie(
        key="admin_logged_in",
        value="true",  # ✅ consistente con get_current_admin
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=86400
    )
    return response

@admin_router.get("/logout")
async def logout(_ = Depends(get_current_admin)):
    response = RedirectResponse("/admin/login", status_code=303)
    response.delete_cookie("admin_logged_in")
    return response

# Panel principal
@admin_router.get("")
async def mostrar_admin(
    request: Request,
    db: Session = Depends(get_db),
    _ = Depends(get_current_admin)
):
    preguntas = db.query(models.Pregunta).order_by(models.Pregunta.id.desc()).all()
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "preguntas": preguntas}
    )

# Agregar pregunta
@admin_router.post("/agregar_pregunta")
async def agregar_pregunta(
    texto_pregunta: str = Form(...),
    respuesta1: str = Form(...), casa1: str = Form(...), imagen1: UploadFile | None = File(None),
    respuesta2: str = Form(...), casa2: str = Form(...), imagen2: UploadFile | None = File(None),
    respuesta3: str = Form(...), casa3: str = Form(...), imagen3: UploadFile | None = File(None),
    respuesta4: str = Form(...), casa4: str = Form(...), imagen4: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    _ = Depends(get_current_admin)
):
    if not texto_pregunta.strip():
        raise HTTPException(400, "La pregunta no puede estar vacía")

    pregunta = models.Pregunta(texto_pregunta=texto_pregunta.strip())
    db.add(pregunta)
    db.flush()

    respuestas_info = [
        (respuesta1.strip(), casa1, imagen1),
        (respuesta2.strip(), casa2, imagen2),
        (respuesta3.strip(), casa3, imagen3),
        (respuesta4.strip(), casa4, imagen4),
    ]

    for texto, casa, archivo in respuestas_info:
        if not texto:
            continue

        if casa not in VALID_HOUSES:
            db.rollback()
            raise HTTPException(400, f"Casa no válida: {casa}. Usa una de: {', '.join(VALID_HOUSES)}")

        ruta_bd = None
        if archivo and archivo.filename and archivo.filename.strip():
            content_type = archivo.content_type or ""
            allowed_types = {
                "image/jpeg", "image/jpg", "image/png", "image/gif",
                "image/webp", "image/avif", "image/heic", "image/heif",
                "image/bmp", "image/tiff", "image/tif", "image/svg+xml",
            }

            if not content_type.startswith("image/") or content_type not in allowed_types:
                db.rollback()
                raise HTTPException(400, f"Tipo de archivo no permitido: {content_type}.")

            # ✅ Nombre limpio: UUID + extensión, sin acumular nombres
            extension = Path(archivo.filename).suffix
            nombre_archivo = f"{uuid.uuid4().hex}{extension}"
            ruta_guardado = UPLOAD_DIR / nombre_archivo

            try:
                with ruta_guardado.open("wb") as f:
                    shutil.copyfileobj(archivo.file, f)
                ruta_bd = f"uploads/{nombre_archivo}"
            except Exception as e:
                db.rollback()
                raise HTTPException(500, f"Error al guardar imagen: {str(e)}")

        respuesta = models.Respuesta(
            texto_respuesta=texto,
            casa=casa,
            imagen=ruta_bd,
            pregunta_id=pregunta.id
        )
        db.add(respuesta)

    db.commit()
    return RedirectResponse("/admin?success=pregunta_agregada", status_code=303)

# Mostrar formulario de edición
@admin_router.get("/editar_pregunta/{pregunta_id}")
async def editar_pregunta_form(
    pregunta_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _ = Depends(get_current_admin)
):
    pregunta = db.query(models.Pregunta).filter_by(id=pregunta_id).first()
    if not pregunta:
        raise HTTPException(404, "Pregunta no encontrada")

    return templates.TemplateResponse(
        "editar_pregunta.html",
        {"request": request, "pregunta": pregunta}
    )

# Guardar cambios de edición
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
    pregunta = db.query(models.Pregunta).filter_by(id=pregunta_id).first()
    if not pregunta:
        raise HTTPException(404, "Pregunta no encontrada")

    if not texto_pregunta.strip():
        raise HTTPException(400, "La pregunta no puede estar vacía")

    pregunta.texto_pregunta = texto_pregunta.strip()

    respuestas_actuales = pregunta.respuestas
    if len(respuestas_actuales) != 4:
        raise HTTPException(400, "Se esperan exactamente 4 respuestas")

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

        respuesta_actual.texto_respuesta = texto
        respuesta_actual.casa = casa

        if archivo and archivo.filename and archivo.filename.strip():
            content_type = archivo.content_type or ""
            allowed_types = {
                "image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp",
                "image/avif", "image/heic", "image/heif", "image/bmp", "image/tiff",
                "image/svg+xml"
            }

            if not content_type.startswith("image/") or content_type not in allowed_types:
                raise HTTPException(400, f"Tipo no permitido: {content_type}.")

            # ✅ Nombre limpio: UUID + extensión, sin acumular nombres
            extension = Path(archivo.filename).suffix
            nombre_archivo = f"{uuid.uuid4().hex}{extension}"
            ruta_guardado = UPLOAD_DIR / nombre_archivo

            try:
                with ruta_guardado.open("wb") as f:
                    shutil.copyfileobj(archivo.file, f)
                respuesta_actual.imagen = f"uploads/{nombre_archivo}"
            except Exception as e:
                raise HTTPException(500, f"Error guardando imagen: {str(e)}")
        # ✅ Si no se sube imagen nueva, se conserva la antigua automáticamente
        # porque no tocamos respuesta_actual.imagen

    db.commit()
    return RedirectResponse("/admin?success=pregunta_actualizada", status_code=303)

# Eliminar pregunta
@admin_router.post("/eliminar_pregunta")
async def eliminar_pregunta(
    pregunta_id: int = Form(...),
    db: Session = Depends(get_db),
    _ = Depends(get_current_admin)
):
    pregunta = db.query(models.Pregunta).filter_by(id=pregunta_id).first()
    if not pregunta:
        raise HTTPException(404, "Pregunta no encontrada")

    db.delete(pregunta)
    db.commit()
    return RedirectResponse("/admin?success=pregunta_eliminada", status_code=303)

# Eliminar respuesta individual
@admin_router.post("/eliminar_respuesta")
async def eliminar_respuesta(
    respuesta_id: int = Form(...),
    db: Session = Depends(get_db),
    _ = Depends(get_current_admin)
):
    respuesta = db.query(models.Respuesta).filter_by(id=respuesta_id).first()
    if not respuesta:
        raise HTTPException(404, "Respuesta no encontrada")

    db.delete(respuesta)
    db.commit()
    return RedirectResponse("/admin?success=respuesta_eliminada", status_code=303)