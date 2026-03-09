# 📗 MANUAL DE USUARIO  
## Sistema de Selección de Casa - Harry Potter

---

## 1. Introducción

Esta aplicación permite:

- Realizar un test para descubrir tu casa de Hogwarts (Gryffindor, Slytherin, Ravenclaw o Hufflepuff).  
- Administrar preguntas y respuestas desde un panel de administración (solo accesible para admins).

---

## 2. Cómo Realizar el Test (Usuarios normales)

1. Accede a la página principal: http://127.0.0.1:8000/quiz  
2. Lee cada pregunta con atención.  
3. Selecciona **una respuesta** por cada pregunta (obligatorio).  
4. Escribe tu nombre en el campo correspondiente.  
5. Pulsa el botón **"Enviar Respuestas"**.  
6. Espera un segundo... ¡y verás tu casa de Hogwarts asignada!

---

## 3. Panel de Administración (Solo para administradores)

Para acceder:  
**http://127.0.0.1:8000/admin/login**

Usuario por defecto: `admin`  
Contraseña por defecto: `1234` (cámbiala en el script `crear_admin.py` o en la base de datos)

Desde el panel puedes:

- Ver todas las preguntas existentes  
- Crear nuevas preguntas  
- Editar preguntas y respuestas  
- Eliminar preguntas o respuestas individuales  
- Subir imágenes para cada respuesta (opcional)

---

## 4. Crear una Pregunta (Admin)

1. Entra al panel de administración.  
2. Rellena el campo **"Texto de la pregunta"**.  
3. Añade al menos una respuesta (texto + casa asociada).  
4. Opcional: sube una imagen para cada respuesta (formatos recomendados: JPG, PNG, WebP).  
5. Pulsa **"Agregar Pregunta"**.

---

## 5. Editar una Pregunta (Admin)

1. En el panel, pulsa el botón **"Editar"** junto a la pregunta deseada.  
2. Modifica el texto de la pregunta o de las respuestas.  
3. Cambia la casa asociada si es necesario.  
4. Sube una nueva imagen si quieres reemplazar la actual (opcional).  
5. Pulsa **"Actualizar Pregunta"** para guardar.

---

## 6. Editar una Respuesta Individual (Admin)

1. En el panel, busca la respuesta dentro de la pregunta.  
2. Pulsa **"Editar Respuesta"**.  
3. Modifica el texto, la casa o la imagen.  
4. Guarda los cambios.

---

## 7. Eliminar Pregunta o Respuesta (Admin)

1. En el panel, pulsa el botón **"Eliminar Pregunta"** o **"Eliminar"** junto a la respuesta.  
2. Confirma la acción (si el navegador pregunta).  

⚠ **Atención:** Esta acción **no se puede deshacer**. La pregunta y todas sus respuestas se borrarán permanentemente de la base de datos.

---

## 8. Subida de Imágenes (Admin)

- Formatos recomendados: **JPG, JPEG, PNG, WebP** (más compatibles).  
- También se aceptan: AVIF, HEIC, BMP, TIFF, SVG (pero pueden no verse en navegadores antiguos).  
- Las imágenes se guardan automáticamente en el servidor.  
- Se muestran junto a cada respuesta en el test.

---

## 9. Recomendaciones para mejores resultados

- Responde todas las preguntas para obtener un resultado preciso.  
- Usa nombres reales o divertidos (solo se muestra en el resultado).  
- En el panel admin: evita preguntas sin respuestas o con casas repetidas.  
- Usa imágenes cuadradas o rectangulares pequeñas para mejor visualización.  
- Si usas móvil: prueba en modo horizontal para ver mejor las opciones.

---

## 10. Problemas Comunes y Soluciones

- **No veo las preguntas en el quiz** → Asegúrate de haber agregado al menos una pregunta desde el panel admin.  
- **Imagen no carga** → Verifica que el archivo tenga formato válido y que el navegador sea moderno (Chrome/Edge recomendado).  
- **Error al enviar respuestas** → Asegúrate de responder todas las preguntas y escribir un nombre.  
- **Login admin falla** → Credenciales por defecto: admin / 1234. Si cambiaste la contraseña, revísala en la base de datos.  
- **El servidor no responde** → Comprueba que el contenedor Docker esté corriendo (`docker compose ps`).

---

¡Disfruta descubriendo tu casa de Hogwarts! 🪄✨