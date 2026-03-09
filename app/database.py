import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import time

# 🔹 Variables de entorno (desde docker-compose o .env)
DB_USER = os.getenv("DB_USER", "hpuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "hppassword")
DB_HOST = os.getenv("DB_HOST", "hp_mariadb")
DB_PORT = os.getenv("DB_PORT", "3306")  # string porque getenv devuelve str
DB_NAME = os.getenv("DB_NAME", "harryquiz")

# 🔹 URL completa de conexión
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 🔹 Motor de conexión con espera inteligente (crucial en Docker)
engine = None
while True:
    try:
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            echo=True,               # logs SQL útiles para debug
            pool_pre_ping=True,      # evita conexiones muertas
            pool_recycle=3600,       # recicla conexiones cada 1 hora
            future=True              # compatibilidad moderna SQLAlchemy 2.0+
        )
        # Prueba conexión real
        conn = engine.connect()
        conn.close()
        print("✅ Base de datos lista")
        break
    except Exception as e:
        print("⏳ Esperando a que MariaDB esté lista...", e)
        time.sleep(2)

# 🔹 Sesión local para inyección de dependencias
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 🔹 Base para todos los modelos ORM
Base = declarative_base()

# 🔹 Dependencia para endpoints FastAPI (inyecta DB)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()