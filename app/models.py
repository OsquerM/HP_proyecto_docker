from sqlalchemy import Column, Integer, String, Text, ForeignKey
# Column: define una columna en la tabla
# Integer, String, Text: tipos de datos de las columnas
# ForeignKey: crea una relación entre tablas (clave foránea)
from sqlalchemy.orm import relationship
# relationship: define la relación entre modelos Python (no en BD, sino en código)
from .database import Base
# Base: clase padre de todos los modelos, la importamos del archivo database.py


# Modelo Usuario
# declarative_base() es como registrar que los modelos creados son tablas y se puede manejar para consultas
# Cada clase que hereda de Base se convierte en una tabla en MariaDB
class Usuario(Base):
    __tablename__ = "usuarios"  # nombre de la tabla en la BD

    # Columnas de la tabla
    id = Column(Integer, primary_key=True, index=True)
    # primary_key: identificador único de cada fila
    # index=True: crea un índice para buscar más rápido por id
    nombre = Column(String(50), nullable=False)
    # String(50): texto de máximo 50 caracteres
    # nullable=False: el campo es obligatorio, no puede estar vacío
    password = Column(String(255), nullable=True)   # contraseña hasheada para admin
    # nullable=True: campo opcional, puede estar vacío
    rol = Column(String(20), default="usuario")     # 'admin' o 'usuario'
    # default: valor por defecto si no se especifica al crear el usuario
    casa = Column(String(20), nullable=True)        # casa asignada al jugador

    def es_admin(self):
        # Método auxiliar que devuelve True si el usuario es admin
        # Evita comparar el rol manualmente cada vez en el código
        return self.rol == "admin"


# Modelo Pregunta

class Pregunta(Base):
    __tablename__ = "preguntas"

    id = Column(Integer, primary_key=True, index=True)
    texto_pregunta = Column(Text, nullable=False)
    # Text: igual que String pero sin límite de caracteres, ideal para preguntas largas

    # Relación con respuestas: una pregunta puede tener muchas respuestas (1 a muchos)
    # Este campo no crea una columna en la BD, es solo para acceder a las respuestas desde Python
    respuestas = relationship(
        "Respuesta",                        # modelo con el que se relaciona
        back_populates="pregunta",          # nombre del campo inverso en Respuesta
        cascade="all, delete-orphan"        # si se borra la pregunta, se borran sus respuestas automáticamente
    )

    def total_respuestas(self):
        # Método auxiliar que devuelve cuántas respuestas tiene la pregunta
        return len(self.respuestas)


# Modelo Respuesta

class Respuesta(Base):
    __tablename__ = "respuestas"

    id = Column(Integer, primary_key=True, index=True)
    pregunta_id = Column(Integer, ForeignKey("preguntas.id", ondelete="CASCADE"), nullable=False)
    # ForeignKey: enlaza esta columna con el id de la tabla preguntas
    # ondelete="CASCADE": si se borra la pregunta en la BD, se borran sus respuestas también
    # (complementa al cascade del relationship de arriba, pero actúa a nivel de BD)
    texto_respuesta = Column(String(255), nullable=False)
    casa = Column(String(20), nullable=False)   # Gryffindor, Slytherin, Ravenclaw, Hufflepuff
    # la casa a la que suma puntos esta respuesta
    imagen = Column(String(255), nullable=True) # ruta de la imagen de la respuesta

    # Relación inversa: desde una respuesta podemos acceder a su pregunta
    # back_populates conecta ambos lados de la relación entre Pregunta y Respuesta
    pregunta = relationship("Pregunta", back_populates="respuestas")

    def tiene_imagen(self):
        # Método auxiliar que devuelve True si la respuesta tiene imagen asociada
        return self.imagen is not None