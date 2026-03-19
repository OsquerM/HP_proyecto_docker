from pathlib import Path
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from . import models
from .database import get_db
import random  # para manejar empates de forma más interesante

quiz_router = APIRouter(prefix="/quiz", tags=["quiz"])

# Ruta absoluta y segura para templates (funciona en local y Docker)
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Modelo Pydantic para recibir las respuestas
class RespuestaUsuario(BaseModel):
    usuario_nombre: str
    respuestas_usuario: dict[int, int]  # {pregunta_id: respuesta_id}

# Diccionario de imágenes de casas
IMAGENES_CASAS = {
    "Gryffindor": "uploads/gryffindor.jpg",
    "Slytherin": "uploads/slytherin.jpg",
    "Ravenclaw": "uploads/ravenclaw.jpg",
    "Hufflepuff": "uploads/hufflepuff.jpg",
}

# ============================
# Endpoint: Obtener todas las preguntas con respuestas
# ============================
@quiz_router.get("/preguntas")
def obtener_preguntas(db: Session = Depends(get_db)):
    preguntas = db.query(models.Pregunta).all()
    if not preguntas:
        raise HTTPException(status_code=404, detail="No hay preguntas disponibles")

    resultado = []
    for pregunta in preguntas:
        respuestas = [
            {
                "id": r.id,
                "texto": r.texto_respuesta,
                "imagen": r.imagen if r.imagen else None,  # None si no hay imagen
            }
            for r in pregunta.respuestas
        ]
        resultado.append({
            "id": pregunta.id,
            "texto_pregunta": pregunta.texto_pregunta,
            "respuestas": respuestas
        })
    return {"preguntas": resultado}

# ============================
# Endpoint: Enviar respuestas y calcular casa
# ============================
@quiz_router.post("/enviar_respuestas")
def enviar_respuestas(datos: RespuestaUsuario, db: Session = Depends(get_db)):
    usuario_nombre = datos.usuario_nombre.strip()
    respuestas_usuario = datos.respuestas_usuario

    if not usuario_nombre:
        raise HTTPException(status_code=400, detail="El nombre de usuario es obligatorio")

    # Contar cuántas preguntas hay en la BD
    total_preguntas = db.query(models.Pregunta).count()

    if len(respuestas_usuario) != total_preguntas:
        raise HTTPException(
            status_code=400,
            detail=f"Debes responder exactamente {total_preguntas} preguntas. Respondidas: {len(respuestas_usuario)}"
        )

    # Contador de puntos por casa
    contador_casas = {
        "Gryffindor": 0,
        "Slytherin": 0,
        "Ravenclaw": 0,
        "Hufflepuff": 0
    }

    # Validar y sumar puntos
    for pregunta_id, respuesta_id in respuestas_usuario.items():
        respuesta = db.query(models.Respuesta).filter_by(id=respuesta_id).first()
        if not respuesta:
            raise HTTPException(400, f"Respuesta ID {respuesta_id} no existe")
        if respuesta.pregunta_id != int(pregunta_id):
            raise HTTPException(400, f"La respuesta {respuesta_id} no pertenece a la pregunta {pregunta_id}")
        
        contador_casas[respuesta.casa] += 1

    # Encontrar la(s) casa(s) con máxima puntuación
    max_puntos = max(contador_casas.values())
    casas_maximas = [casa for casa, puntos in contador_casas.items() if puntos == max_puntos]

    # Elegir una 
    casa_resultado = random.choice(casas_maximas) if len(casas_maximas) > 1 else casas_maximas[0]

    # Guardar en BD
    nuevo_usuario = models.Usuario(
        nombre=usuario_nombre,
        casa=casa_resultado
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {
        "usuario": usuario_nombre,
        "casa": casa_resultado,
        "puntos": contador_casas  
    }

# ============================
# Endpoint: Mostrar resultado en HTML
# ============================
@quiz_router.get("/resultado")
def mostrar_resultado(
    request: Request,
    nombre: str,
    casa: str
):
    casas_validas = ["Gryffindor", "Slytherin", "Ravenclaw", "Hufflepuff"]
    
    if casa not in casas_validas:
        casa = "Gryffindor"  # fallback seguro

    imagen_casa = IMAGENES_CASAS.get(casa, "uploads/default.jpg")  # fallback si no existe

    return templates.TemplateResponse(
        "resultado.html",
        {
            "request": request,
            "nombre": nombre,
            "casa": casa,
            "imagen_casa": imagen_casa
        }
    )