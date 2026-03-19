# Manual Técnico
**Versión del proyecto:** 1.0  
**Fecha:** 2026  
**Tecnologías principales:**  
- Backend: FastAPI (Python)  
- Frontend: HTML5 + CSS3 + JavaScript vanilla  
- Base de datos: MariaDB  
- ORM: SQLAlchemy  
- Plantillas: Jinja2  
- Contenedores: Docker + Docker Compose  

## Proyecto: Sistema de Selección de Casas - Harry Potter
Autor: Óscar Manuel Benito Martín  
Tecnologías: FastAPI, Jinja2, SQLAlchemy, MariaDB, HTML, CSS, Docker

---

# 1. Descripción General

Este proyecto es una aplicación web desarrollada con FastAPI que permite:

- Mostrar preguntas tipo test con imágenes asociadas a cada respuesta.
- Asociar respuestas a casas de Hogwarts (Gryffindor, Slytherin, Ravenclaw, Hufflepuff).
- Calcular la casa final según las respuestas seleccionadas por el usuario.
- Administrar preguntas y respuestas desde un panel de administración protegido.
- Mostrar un personaje famoso de la casa asignada usando una API externa (hp-api.onrender.com).

---

# 2. Arquitectura del Proyecto

Estructura principal:

```
HP_Proyecto_Docker/
│
├── app/
│   ├── main.py          → Punto de entrada, rutas principales y API externa
│   ├── admin.py         → Rutas y lógica del panel de administración
│   ├── quiz.py          → Rutas y lógica del quiz
│   ├── models.py        → Modelos de la base de datos (SQLAlchemy)
│   └── database.py      → Configuración de la conexión a MariaDB
│
├── templates/
│   ├── index.html
│   ├── quiz.html
│   ├── resultado.html
│   ├── admin.html
│   ├── editar_pregunta.html
│   └── login.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/         → Imágenes subidas por el administrador
│
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

# 3. Tecnologías Utilizadas

- **FastAPI** → Framework backend en Python
- **SQLAlchemy** → ORM para gestión de la base de datos
- **MariaDB** → Base de datos relacional (desplegada en Docker)
- **Jinja2** → Motor de plantillas HTML
- **HTML/CSS/JavaScript** → Interfaz visual del usuario
- **Docker + Docker Compose** → Contenedores para despliegue
- **bcrypt (passlib)** → Cifrado de contraseñas
- **httpx** → Cliente HTTP para consumir la API externa

---

# 4. Base de Datos

## 4.1 Modelos

```python
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    password = Column(String(255), nullable=True)
    rol = Column(String(20), default="usuario")  # 'admin' o 'usuario'
    casa = Column(String(20), nullable=True)      # casa asignada al jugador

class Pregunta(Base):
    __tablename__ = "preguntas"
    id = Column(Integer, primary_key=True)
    texto_pregunta = Column(Text, nullable=False)
    respuestas = relationship("Respuesta", back_populates="pregunta", cascade="all, delete-orphan")

class Respuesta(Base):
    __tablename__ = "respuestas"
    id = Column(Integer, primary_key=True)
    texto_respuesta = Column(String(255), nullable=False)
    casa = Column(String(20), nullable=False)
    imagen = Column(String(255), nullable=True)  # ruta relativa: uploads/nombre.jpg
    pregunta_id = Column(Integer, ForeignKey("preguntas.id"))
    pregunta = relationship("Pregunta", back_populates="respuestas")
```

## 4.2 Relaciones

- **Pregunta → Respuesta**: relación 1:N. Una pregunta tiene múltiples respuestas, cada respuesta pertenece a una única pregunta.
- **Usuario**: almacena tanto administradores (rol="admin") como jugadores (rol="usuario"). La casa asignada se guarda tras completar el quiz.

---

# 5. Sistema de Rutas

## 5.1 Rutas públicas

| Método | Ruta | Función |
|--------|------|---------|
| GET | / | Página de inicio |
| GET | /quiz | Mostrar el test |
| GET | /quiz/preguntas | API: devuelve preguntas en JSON |
| POST | /quiz/enviar_respuestas | Procesa respuestas y calcula casa |
| GET | /quiz/resultado | Muestra la casa asignada |

## 5.2 Rutas de administración

| Método | Ruta | Función |
|--------|------|---------|
| GET | /admin/login | Formulario de login |
| POST | /admin/login | Procesar login |
| GET | /admin/logout | Cerrar sesión |
| GET | /admin | Panel principal |
| POST | /admin/agregar_pregunta | Crear nueva pregunta |
| GET | /admin/editar_pregunta/{id} | Formulario de edición |
| POST | /admin/actualizar_pregunta/{id} | Guardar cambios |
| POST | /admin/eliminar_pregunta | Eliminar pregunta |
| POST | /admin/eliminar_respuesta | Eliminar respuesta individual |

## 5.3 Rutas API externa

| Método | Ruta | Función |
|--------|------|---------|
| GET | /api-externa/personaje/{casa} | Devuelve personaje aleatorio de HP-API |

---

# 6. Flujo de Funcionamiento

1. El usuario accede a `/quiz` y ve las preguntas cargadas dinámicamente desde la BD.
2. Selecciona una respuesta por pregunta y escribe su nombre.
3. Al enviar, el backend cuenta cuántas respuestas corresponden a cada casa.
4. La casa con más respuestas es la asignada (en caso de empate, se elige la primera).
5. Se redirige a `/quiz/resultado` donde se muestra la casa y un personaje famoso de esa casa obtenido de hp-api.onrender.com.

---

# 7. Gestión de Imágenes

- Las imágenes se almacenan en `/static/uploads/`.
- El nombre del archivo se genera con UUID para evitar colisiones: `{uuid}.{extension}`.
- En la base de datos solo se guarda la ruta relativa: `uploads/nombre.jpg`.
- Se accede desde el HTML con: `<img src="/static/{{ respuesta.imagen }}">`.
- Las imágenes persisten entre reinicios gracias al volumen Docker: `./static/uploads:/app/static/uploads`.

---

# 8. Seguridad

- **Autenticación**: login con usuario y contraseña cifrada con bcrypt.
- **Sesiones**: cookie `admin_logged_in` con `httponly=True` y expiración de 24h.
- **Control de roles**: solo usuarios con `rol="admin"` pueden acceder al panel.
- **Validación de archivos**: solo se aceptan tipos de imagen válidos (jpg, png, webp, avif, etc.).
- **Recomendación para producción**: cambiar `secure=False` a `secure=True` en la cookie y usar HTTPS.

---

# 9. Ejecución del Proyecto

## Con Docker (recomendado)

```bash
# Construir y levantar los contenedores
docker compose up --build -d

# Ver logs
docker compose logs hp_quiz_app -f

# Detener
docker compose down

# Detener y borrar datos de BD
docker compose down -v
```

## Acceso

- Quiz: http://localhost:8000/quiz
- Admin: http://localhost:8000/admin/login

## Sin Docker (desarrollo local)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

# 10. Despliegue con Docker

El `docker-compose.yml` define dos servicios:

- **hp_mariadb**: base de datos MariaDB con volumen persistente para los datos.
- **hp_quiz_app**: aplicación FastAPI construida desde el Dockerfile, con volumen para las imágenes subidas.

Las variables de entorno (`DB_HOST`, `DB_USER`, etc.) se pasan al contenedor de la app para la conexión a la BD.

---

# 11. Pruebas Realizadas

| Prueba | Resultado |
|--------|-----------|
| Login admin con credenciales correctas | ✅ OK |
| Login admin con credenciales incorrectas | ✅ Redirige con error |
| Agregar pregunta con imagen | ✅ OK |
| Agregar pregunta sin imagen | ✅ OK |
| Editar pregunta conservando imagen anterior | ✅ OK |
| Eliminar pregunta | ✅ OK |
| Realizar quiz completo | ✅ OK (calcula casa por mayoría) |
| Visualización de imágenes (jpg, png, webp, avif) | ✅ OK |
| API externa HP-API (personaje con imagen) | ✅ OK |
| Compatibilidad navegadores | ✅ Chrome, Edge |
| Persistencia de imágenes tras reinicio Docker | ✅ OK (volumen montado) |