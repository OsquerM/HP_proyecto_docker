# Informe Final del Proyecto  
**Proyecto: Sistema de Selección de Casas - Harry Potter**  
**RA:** 4.e – Definir y elaborar la documentación necesaria para la evaluación del proyecto  
**Fecha:** Mayo 2026  
**Autor:** Óscar Manuel Benito Martín  

## 1. Resumen del proyecto

El proyecto consiste en una aplicación web full-stack que simula el Sombrero Seleccionador de Harry Potter. Permite:

- Realizar un test interactivo con preguntas y respuestas asociadas a casas.  
- Calcular la casa final por mayoría de respuestas.  
- Administrar preguntas/respuestas/imágenes desde un panel admin protegido.  
- Despliegue en Docker con base de datos persistente.

**Objetivos principales cumplidos:**
- Funcionalidad completa del test y administración  
- Autenticación básica con roles  
- Gestión de imágenes y persistencia  
- Despliegue en contenedores

## 2. Seguimiento de tareas (extraído de Git / Jira)

- **Nº total de tareas registradas:** 18 (aprox.)  
  - To Do / Backlog inicial: 5  
  - In Progress durante desarrollo: 8  
  - Done / Cerradas: 18 (100% completadas)

Ejemplos de tareas clave cerradas:
- Configuración inicial FastAPI + SQLite  
- Modelos BD (Pregunta y Respuesta)  
- CRUD completo en panel admin  
- Frontend quiz con carga dinámica  
- Autenticación admin con bcrypt  
- Dockerización (app + MariaDB)  
- Gestión de imágenes con subida y visualización  
- Pruebas funcionales y corrección de incidencias

**Tareas pendientes al cierre:**

## 3. Gestión de incidencias

- **Nº de bugs/incidencias registradas:** 7 (ejemplos reales)  
  - Error CORS en fetch desde quiz.js (origen localhost vs 127.0.0.1) → Prioridad Alta → Solución: cambiar BASE_URL a window.location.origin  
  - 404 en imágenes .avif en navegadores antiguos → Prioridad Media → Solución: fallback a .jpg en JS + recomendación Chrome/Edge  
  - Error al agregar pregunta sin respuestas → Prioridad Media → Solución: validación backend + mensaje claro  
  - Doble /uploads/ en rutas de imagen → Prioridad Baja → Solución: replace en JS  
  - Login admin fallaba por hash incorrecto → Prioridad Alta → Solución: recrear admin con bcrypt  
  - Imágenes no visibles en quiz → Prioridad Alta → Solución: ajuste de rutas en JS  
  - 404 en /preguntas sin prefijo → Prioridad Baja → Solución: usar ruta correcta /quiz/preguntas

- **Incidencias críticas:** 3 (todas resueltas antes de entrega)  
- **Soluciones aplicadas:** Todas verificadas con pruebas manuales y logs.  
- **Trazabilidad:** Todas registradas en Git commits con mensajes claros + comentarios en código y consola.

## 4. Valoración final

- **Cumplimiento de objetivos:** 100% (test funcional, panel admin completo, Docker estable, imágenes visibles)  
- **Calidad del desarrollo:** Alta (código limpio, rutas protegidas, validaciones, manejo de errores)  
- **Fortalezas:**  
  - Interfaz temática e inmersiva  
  - Funcionalidad completa end-to-end  
  - Despliegue sencillo con Docker  
- **Debilidades detectadas:**  
  - Soporte parcial para .avif en navegadores antiguos  
  - Ausencia de CSRF y HTTPS (para producción)  
  - No hay tests unitarios automatizados (solo manuales)  
- **Propuestas de mejora:**  
  - Añadir CSRF y JWT para admin  
  - Implementar HTTPS con Nginx proxy  
  - Añadir tests con pytest  
  - Mejorar accesibilidad (Lighthouse score >90)  
  - Integrar API externa (ej. Harry Potter API pública para más preguntas)

**Conclusión:**  
Proyecto funcional, estable y listo para entrega. Cumple con todos los requisitos principales y está preparado para posibles mejoras en futuras iteraciones.

**Firma:**  
Óscar Manuel Benito Martín  
2026