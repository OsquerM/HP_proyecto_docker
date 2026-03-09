import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import time

DB_USER = os.getenv("DB_USER", "hpuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "hppassword")
DB_HOST = os.getenv("DB_HOST", "hp_mariadb")
DB_PORT = os.getenv("DB_PORT", 3306)
DB_NAME = os.getenv("DB_NAME", "harryquiz")

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Espera a que la base de datos esté lista
while True:
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
        conn = engine.connect()
        conn.close()
        print("✅ Base de datos lista")
        break
    except Exception as e:
        print("⏳ Esperando a que MariaDB esté lista...", e)
        time.sleep(2)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()