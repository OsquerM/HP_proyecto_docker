# MANUAL DE USUARIO
## Sistema de Selección de Casa - Harry Potter

---

## 1. Introducción

Esta aplicación web te permite descubrir a qué casa de Hogwarts perteneces mediante un test de preguntas. También incluye un panel de administración para gestionar el contenido del quiz.

Las casas posibles son:
- 🦁 **Gryffindor**
- 🐍 **Slytherin**
- 🦅 **Ravenclaw**
- 🦡 **Hufflepuff**

---

## 2. Cómo Realizar el Test (Usuarios normales)

1. Accede a la página del quiz: **http://localhost:8000/quiz**
2. Lee cada pregunta con atención.
3. Selecciona **una respuesta** por cada pregunta (obligatorio).
4. Escribe tu nombre en el campo correspondiente (mínimo 3 caracteres).
5. Pulsa el botón **"Enviar Respuestas"**.
6. Espera un momento... ¡y verás tu casa de Hogwarts asignada junto a un personaje famoso de esa casa!

---

## 3. Página de Resultado

Tras enviar el test verás:

- Tu nombre y la casa asignada.
- La imagen del escudo de tu casa.
- Un personaje famoso de esa casa (obtenido en tiempo real desde una API de Harry Potter).
- Un botón para **volver a hacer el quiz**.

---

## 4. Panel de Administración (Solo para administradores)

Para acceder:  
**http://localhost:8000/admin/login**

- **Usuario:** `admin`
- **Contraseña:** la configurada al crear el usuario admin

Desde el panel puedes:

- Ver todas las preguntas existentes con sus respuestas.
- Crear nuevas preguntas.
- Editar preguntas y sus respuestas.
- Eliminar preguntas completas.
- Subir imágenes para cada respuesta (opcional).

---

## 5. Crear una Pregunta (Admin)

1. Entra al panel de administración.
2. Rellena el campo **"Texto de la pregunta"** (mínimo 5 caracteres).
3. Rellena las 4 respuestas, indicando para cada una:
   - **Texto** de la respuesta.
   - **Casa** asociada (Gryffindor, Slytherin, Ravenclaw o Hufflepuff).
   - **Imagen** opcional (formatos: JPG, PNG, WebP, AVIF).
4. Pulsa **"Agregar Pregunta"**.

---

## 6. Editar una Pregunta (Admin)

1. En el panel, pulsa el botón **"Editar"** junto a la pregunta deseada.
2. Modifica el texto de la pregunta o de cualquiera de las respuestas.
3. Cambia la casa asociada si es necesario.
4. Sube una nueva imagen si quieres reemplazar la actual (si no subes ninguna, se conserva la imagen anterior).
5. Pulsa **"Actualizar Pregunta"** para guardar los cambios.

---

## 7. Eliminar una Pregunta (Admin)

1. En el panel, pulsa el botón **"Eliminar"** junto a la pregunta.
2. La acción se ejecuta inmediatamente.

⚠ **Atención:** Esta acción **no se puede deshacer**. La pregunta y todas sus respuestas se borrarán permanentemente de la base de datos.

---

## 8. Subida de Imágenes (Admin)

- Formatos recomendados: **JPG, JPEG, PNG, WebP** (máxima compatibilidad).
- También se aceptan: AVIF, HEIC, BMP, TIFF, SVG.
- Las imágenes se guardan automáticamente en el servidor y persisten aunque se reinicie el sistema.
- Se muestran junto a cada respuesta en el test.

---

## 9. Recomendaciones para Mejores Resultados

- Responde **todas las preguntas** para obtener un resultado preciso.
- Escribe un nombre de al menos 3 caracteres.
- En el panel admin: asegúrate de que cada pregunta tenga exactamente **4 respuestas** con casas diferentes.
- Usa imágenes de tamaño moderado para una mejor visualización.
- Usa un navegador moderno (Chrome o Edge recomendados).

---

## 10. Problemas Comunes y Soluciones

| Problema | Solución |
|----------|----------|
| No se ven preguntas en el quiz | Agrega al menos una pregunta desde el panel admin |
| Una imagen no carga | Verifica que el formato sea válido (JPG, PNG, WebP) |
| Error al enviar respuestas | Asegúrate de responder todas las preguntas y escribir un nombre |
| Login admin falla | Verifica usuario y contraseña. Si la olvidaste, consúltala en la base de datos |
| El servidor no responde | Comprueba que Docker esté corriendo: `docker compose ps` |
| No aparece el personaje de la casa | La API externa puede tardar hasta 30 segundos en responder la primera vez |

---

¡Disfruta descubriendo tu casa de Hogwarts!