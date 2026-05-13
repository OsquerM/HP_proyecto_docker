# Procedimiento de Gestión de Incidencias

**Proyecto:** Harry Potter Quiz  
**RA:** 4.c  
**Alumno:** Óscar Manuel Benito Martín  
**Herramienta:** Jira

---

## 1. Definición del Procedimiento

Durante el desarrollo del proyecto, las incidencias se gestionaron de la siguiente manera:

- **Registro**: Toda incidencia (bug, error o problema) se registraba en Jira como tipo **Bug** o **Incidencia**.
- **Campos obligatorios**:
  - Título claro y descriptivo
  - Descripción detallada con pasos para reproducir
  - Prioridad (Alta / Media / Baja)
  - Responsable (Óscar Manuel Benito Martín)
  - Capturas de pantalla o logs cuando fuera necesario

---

## 2. Flujo de Gestión

1. Detección del problema
2. Creación del ticket en Jira
3. Análisis y asignación de prioridad
4. Implementación de la solución
5. Pruebas locales y en Docker
6. Cierre del ticket una vez verificado

Los tickets siguen el siguiente flujo de estados en Jira:  
**Open → In Progress → Done**

---

## 3. Ejemplos Reales de Incidencias Gestionadas

| Bug | Prioridad | Solución | Estado |
|-----|-----------|----------|--------|
| Error 500 al crear pregunta con imagen | Alta | Ampliar validación de tipos MIME | Cerrado |
| Imágenes no cargan en el quiz | Media | Corregir rutas en JS con `window.location.origin` | Cerrado |
| MariaDB no conecta al iniciar Docker | Alta | Implementar bucle de espera con reintentos en `database.py` | Cerrado |
| Error "Method Not Allowed" al editar pregunta | Media | Corregir atributo `action` en el formulario HTML | Cerrado |

---

## 4. Conclusión

Se registraron y resolvieron todas las incidencias detectadas durante el desarrollo. El uso de Jira permitió mantener un seguimiento ordenado, priorizar problemas y documentar las soluciones aplicadas. Cada ticket quedó cerrado tras verificar que la solución funcionaba correctamente en el entorno Docker.
