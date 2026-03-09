# Procedimiento de Gestión de Incidencias  
**Proyecto: Sistema de Selección de Casas - Harry Potter**  
**RA:** 4.c – Procedimiento para la evaluación de incidencias, solución y registro  
**Fecha de definición:** Marzo 2026  
**Herramienta principal:** Jira 

## 1. Definición del procedimiento

Las incidencias detectadas durante el desarrollo se registran de forma sistemática en **Jira** (o GitHub Issues) como tipo de issue **Bug** o **Incidencia**.

**Flujo completo de gestión:**

1. **Detección**  
   Cualquier miembro del equipo detecta un problema (error funcional, bug visual, fallo de rendimiento, comportamiento inesperado, etc.).

2. **Registro en Jira**  
   Se crea un nuevo issue con los siguientes campos obligatorios:

   - Tipo: **Bug** o **Incidencia**  
   - Título: Claro y conciso (ej. "Error 500 al enviar respuestas del quiz")  
   - Descripción:  
     - Pasos para reproducir  
     - Comportamiento esperado  
     - Comportamiento real  
     - Capturas de pantalla / logs / traceback si aplica  
   - Prioridad / Severidad:  
     - Crítica (impide usar la app)  
     - Alta (funcionalidad importante rota)  
     - Media (molesto pero no crítico)  
     - Baja (mejora cosmética o sugerencia)  
   - Responsable: Asignado al desarrollador más adecuado  
   - Etiquetas: frontend, backend, base-datos, docker, accesibilidad, etc.  
   - Adjuntos: imágenes, logs, etc.

3. **Evaluación**  
   - Se analiza el impacto (¿afecta a usuarios finales?, ¿impide entrega?, ¿seguridad?)  
   - Se estima esfuerzo (Story Points o horas aproximadas)  
   - Se prioriza en el backlog/sprint

4. **Propuesta de solución**  
   - El responsable comenta la solución técnica propuesta  
   - Se crea branch si es necesario (ej. `fix/error-500-quiz-submit`)  
   - Se implementa y prueba localmente

5. **Resolución y verificación**  
   - Commit con mensaje claro (ej. "fix: corrige error 500 en /enviar_respuestas")  
   - Pull Request / Merge con enlace al ticket Jira  
   - Pruebas manuales + verificación en entorno Docker  
   - Cierre del ticket solo si:  
     - Funciona correctamente  
     - No introduce regresiones  
     - Se verifica en varios navegadores

6. **Cierre**  
   - Estado: **Done** o **Closed**  
   - Comentario final: "Verificado en Chrome y Firefox. Imágenes cargan correctamente."

## 2. Evidencias que se comprueban en Jira

- Uso de issues tipo **Bug** o **Incidencia** (no solo tareas genéricas)  
- Cada incidencia tiene:  
  - Descripción clara y reproducibles pasos  
  - Prioridad/Severidad asignada  
  - Responsable claro  
  - Comentarios con solución técnica  
  - Cambio de estado visible: Open → In Progress → Resolved → Closed  
  - Adjuntos (capturas, logs) cuando sea necesario  
- Hay incidencias reales registradas durante el desarrollo (no inventadas al final)

Ejemplo real de ticket creado:

- Título: "Error 404 al cargar preguntas en /quiz"  
- Prioridad: Alta  
- Descripción: "Fetch a /preguntas falla con CORS. Pasos: entrar en /quiz → ver consola"  
- Solución propuesta: "Cambiar BASE_URL a window.location.origin en quiz.js"  
- Estado: Closed tras merge y prueba

Todo queda trazado en Jira sin necesidad de documento adicional. Este procedimiento se definió en la fase de análisis y diseño y se aplicó durante todo el proyecto.