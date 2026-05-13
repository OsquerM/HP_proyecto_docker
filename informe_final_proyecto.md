# Informe Final del Proyecto

**Proyecto:** Harry Potter Quiz  
**Alumno:** Óscar Manuel Benito Martín  
**Ciclo:** 2º DAW  
**Fecha:** Mayo 2026  
**RA:** 4.e – Informe Final del Proyecto

## 1. Resumen del Proyecto

El **Harry Potter Quiz** es una aplicación web full-stack que permite a los usuarios realizar un test interactivo para descubrir a qué casa de Hogwarts pertenecen. Incluye un panel de administración completo para gestionar preguntas, respuestas e imágenes.

**Objetivos principales cumplidos:**
- Quiz funcional con cálculo de casa por mayoría de puntos
- Sistema completo de administración (CRUD)
- Gestión de subida y visualización de imágenes
- Despliegue completo en contenedores con Docker

---

## 2. Seguimiento de Tareas

Se utilizó **Jira** como herramienta principal de planificación y seguimiento.

- **Total de tareas registradas:** 12
- **Tareas completadas:** 12
- **Tareas pendientes:** 3 (mejoras futuras)

Se siguió una metodología Kanban con revisiones semanales para ajustar prioridades y avances.

---

## 3. Gestión de Incidencias

Durante el desarrollo se registraron **10 incidencias** (Bugs).

**Incidencias más relevantes:**

- **Error 500 al crear pregunta con imagen** (Alta) → Solución: ampliación de tipos MIME permitidos.
- **Imágenes no cargaban en el quiz** (Alta) → Solución: corrección de rutas dinámicas con `window.location.origin`.
- **Error "Method Not Allowed" al editar pregunta** (Media) → Solución: corrección del atributo `action` en el formulario.
- **MariaDB no conectaba al iniciar Docker** (Alta) → Solución: implementación de bucle de espera con reintentos.

Todas las incidencias fueron registradas, analizadas, resueltas y verificadas antes de cerrar los tickets en Jira siguiendo el flujo: **Open → In Progress → Done**

---

## 4. Valoración Final

**Cumplimiento de objetivos:** 95%  
Se alcanzó prácticamente toda la funcionalidad planteada, incluyendo el quiz, el panel de administración y el despliegue en Docker.

**Calidad del desarrollo:**  
Buen nivel de código estructurado, uso correcto de Pydantic para validaciones, manejo adecuado de sesiones y buenas prácticas en Docker.

**Fortalezas:**
- Interfaz temática e inmersiva
- Sistema completo de administración
- Portabilidad gracias a Docker

**Debilidades detectadas:**
- Autenticación básica del admin (solo cookies)
- Ausencia de tests unitarios automatizados
- Soporte limitado de algunos formatos de imagen

**Propuestas de mejora:**
- Implementar JWT o sesiones en base de datos para el panel de admin
- Añadir tests automáticos con pytest
- Mejorar el diseño responsive y accesibilidad

**Reflexión personal:**  
Este proyecto me ha permitido integrar conocimientos de Backend, Bases de Datos, Interfaces y Despliegue de Aplicaciones. Ha sido una experiencia muy enriquecedora que me ha ayudado a comprender mejor el ciclo completo de desarrollo de una aplicación web real y la importancia de tomar decisiones técnicas justificadas.

---

**Firma:**  
Óscar Manuel Benito Martín
