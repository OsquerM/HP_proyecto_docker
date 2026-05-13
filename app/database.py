import os #lee las variables de entorno
from sqlalchemy import create_engine #crea la conexion 
from sqlalchemy.orm import sessionmaker, declarative_base
#session crea sesiones para consultas y modifica la bd
#declarative crea la bd para definir modelos
import time #hace pausas para que mariadb este listo


# CONFIGURACIÓN DE LA BASE DE DATOS (MariaDB)


# Obtenemos las credenciales desde variables de entorno.
# Si no existen, usamos valores por defecto 
DB_USER = os.getenv("DB_USER", "hpuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "hppassword")
DB_HOST = os.getenv("DB_HOST", "hp_mariadb")      # En Docker el host es el nombre del servicio
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "harryquiz")

# Construimos la URL de conexión a MariaDB
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
#mysql le decimos que la bd es mariadb
#pymysql driver que conecta python con la bd


# CONEXIÓN CON REINTENTO 


engine = None #inicializada en none

# Bucle infinito hasta que MariaDB esté listo
while True:
    try:
        # Creamos el motor de conexión a la base de datos
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            echo=True,           # Muestra todas las consultas SQL en consola (útil para debug)
            pool_pre_ping=True,  # Verifica que la conexión sigue viva antes de usarla
            pool_recycle=3600,   # Reinicia las conexiones cada hora (evita errores de "MySQL gone away")
            future=True          # Usa la versión moderna de SQLAlchemy
        )
        
        # Probamos la conexión
        conn = engine.connect()
        conn.close()
        
        print("✅ Base de datos lista")
        break  # Salimos del bucle cuando la conexión es exitosa
        
    except Exception as e:
        # Si MariaDB aún no está listo (común al iniciar Docker), esperamos
        print("⏳ Esperando a que MariaDB esté lista...", e)
        time.sleep(2)  # Espera 2 segundos antes de volver a intentar



# CONFIGURACIÓN DE SESIONES Y MODELOS


# SessionLocal es una fábrica de sesiones
SessionLocal = sessionmaker(
    autocommit=False,   # No hace commit automáticamente
    autoflush=False,    # No hace flush automáticamente
    bind=engine         # Conecta la sesión al engine
)
#Plantilla que usaran los modelos
# Base es la clase base que usarán todos nuestros modelos (Usuario, Pregunta, Respuesta)
Base = declarative_base()



# FUNCIÓN PARA OBTENER SESIÓN DE BD (Dependencia de FastAPI)


def get_db():
    """
    Esta función se usa con Depends(get_db) en los endpoints.
    Crea una sesión de base de datos y la cierra automáticamente
    cuando termina la petición.
    """
    db = SessionLocal()          # Creamos una nueva sesión
    try:
        yield db                 # Nos sirve de puente entre la funcion get_db y la ruta
    finally:
        db.close()               # Cerramos la sesión aunque ocurra un error