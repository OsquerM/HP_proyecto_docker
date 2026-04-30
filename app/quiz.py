# Importaciones necesarias
from pathlib import Path  # Para manejar rutas de forma segura 
from fastapi import APIRouter, Depends, Request, HTTPException  # FastAPI básico
from sqlalchemy.orm import Session  # Para trabajar con la base de datos
from pydantic import BaseModel  # Para validar datos que llegan al backend
from fastapi.templating import Jinja2Templates  # Para renderizar HTML
from . import models  # Modelos de la base de datos
from .database import get_db  # Función para obtener conexión a la BD
import random  # Para desempates aleatorios

# Creamos un router específico para el quiz
quiz_router = APIRouter(prefix="/quiz", tags=["quiz"])

# Ruta absoluta a la carpeta templates (IMPORTANTE en Docker)
# __file__ → archivo actual
# parent.parent → subimos dos niveles (hasta raíz del proyecto)
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración de plantillas HTML
templates = Jinja2Templates(directory=BASE_DIR / "templates")


# MODELO DE DATOS (entrada del usuario)


class RespuestaUsuario(BaseModel):
    # Nombre del usuario (string)
    usuario_nombre: str

    # Diccionario con respuestas:
    # clave = id de la pregunta
    # valor = id de la respuesta elegida
    # Ejemplo: {1: 3, 2: 5, 3: 1}
    respuestas_usuario: dict[int, int]


# IMÁGENES DE LAS CASAS


# Diccionario que relaciona cada casa con su imagen
IMAGENES_CASAS = {
    "Gryffindor": "uploads/gryffindor.jpg",
    "Slytherin": "uploads/slytherin.jpg",
    "Ravenclaw": "uploads/ravenclaw.jpg",
    "Hufflepuff": "uploads/hufflepuff.jpg",
}


# ENDPOINT: OBTENER PREGUNTAS


@quiz_router.get("/preguntas")
def obtener_preguntas(db: Session = Depends(get_db)):
    # Obtenemos todas las preguntas de la BD
    preguntas = db.query(models.Pregunta).all()

    # Si no hay preguntas → error 404
    if not preguntas:
        raise HTTPException(status_code=404, detail="No hay preguntas disponibles")

    resultado = []

    # Recorremos cada pregunta
    for pregunta in preguntas:
        # Obtenemos sus respuestas asociadas
        respuestas = [
            {
                "id": r.id,
                "texto": r.texto_respuesta,
                # Si no hay imagen → devolvemos None
                "imagen": r.imagen if r.imagen else None,
            }
            for r in pregunta.respuestas
        ]

        # Construimos estructura final
        resultado.append({
            "id": pregunta.id,
            "texto_pregunta": pregunta.texto_pregunta,
            "respuestas": respuestas
        })

    # Devolvemos JSON con todas las preguntas
    return {"preguntas": resultado}


# ENDPOINT: ENVIAR RESPUESTAS


@quiz_router.post("/enviar_respuestas")
def enviar_respuestas(datos: RespuestaUsuario, db: Session = Depends(get_db)):
    # Limpiamos el nombre (quitamos espacios)
    usuario_nombre = datos.usuario_nombre.strip()
    respuestas_usuario = datos.respuestas_usuario

    # Validación: nombre obligatorio
    if not usuario_nombre:
        raise HTTPException(status_code=400, detail="El nombre de usuario es obligatorio")

    # Contamos cuántas preguntas hay en la BD
    total_preguntas = db.query(models.Pregunta).count()

    # Validamos que haya respondido todas
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

    # VALIDACIÓN Y SUMA DE PUNTOS
    #.items() devuelve los pares clave-valor del diccionario a la vez
    for pregunta_id, respuesta_id in respuestas_usuario.items():
        # Buscamos la respuesta en la BD
        respuesta = db.query(models.Respuesta).filter_by(id=respuesta_id).first()

        # Si no existe → error
        if not respuesta:
            raise HTTPException(400, f"Respuesta ID {respuesta_id} no existe")

        # Validamos que la respuesta corresponde a esa pregunta
        if respuesta.pregunta_id != int(pregunta_id):
            raise HTTPException(400, f"La respuesta {respuesta_id} no pertenece a la pregunta {pregunta_id}")
        
        # Sumamos punto a la casa correspondiente
        contador_casas[respuesta.casa] += 1

    # CALCULAR CASA GANADORA

    # Obtenemos la puntuación máxima
    max_puntos = max(contador_casas.values())
    #values devuelve solo la puntuación de las casas
    #max devuelve la casa con mayor puntuación 

    # Obtenemos las casas que tienen esa puntuación
    casas_maximas = [casa for casa, puntos in contador_casas.items() if puntos == max_puntos]
    #items devuelve clave-valor al mismo tiempo
    # Si hay empate → elegimos aleatoriamente
    casa_resultado = random.choice(casas_maximas) if len(casas_maximas) > 1 else casas_maximas[0]

    # GUARDAR USUARIO EN BD

    nuevo_usuario = models.Usuario(
        nombre=usuario_nombre,
        casa=casa_resultado
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    # Devolvemos resultado
    return {
        "usuario": usuario_nombre,
        "casa": casa_resultado,
        "puntos": contador_casas  
    }


# ENDPOINT: RESULTADO EN HTML


@quiz_router.get("/resultado")
def mostrar_resultado(
    request: Request,
    nombre: str,
    casa: str
):
    # Lista de casas válidas (seguridad)
    casas_validas = ["Gryffindor", "Slytherin", "Ravenclaw", "Hufflepuff"]
    
    # Si la casa no es válida → fallback
    if casa not in casas_validas:
        casa = "Gryffindor"

    # Obtenemos imagen de la casa (o default)
    imagen_casa = IMAGENES_CASAS.get(casa, "uploads/default.jpg")

    # Renderizamos plantilla HTML con datos
    return templates.TemplateResponse(
        "resultado.html",
        {
            "request": request,  
            "nombre": nombre,
            "casa": casa,
            "imagen_casa": imagen_casa
        }
    )