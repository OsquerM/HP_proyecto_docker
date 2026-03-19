# Modelo entidad
## Usuario
- id PK
- nombre
- password
- rol
- casa

## Pregunta
- id PK
- pregunta

## Respuesta 
- id PK
- respuesta
- casa
- pregunta_id FK

# Relaciones
Pregunta → Respuesta

Tipo: 1 a N

- Una pregunta tiene muchas respuestas

- Una respuesta pertenece a una sola pregunta

## Usuario 
- nombre

- casa final

## Admin
- Crea pregunta

- Borra pregunta

- Edita pregunta



# Diagrama Entidad-Relacion
+-----------------+
|    USUARIO      |
+-----------------+
| id (PK)         |
| nombre          |
| password        |
| rol             |
|   usuario/admin |        
| casa            |
+-----------------+


+-----------------+
|    PREGUNTA     |
+-----------------+
| id (PK)         |
| texto_pregunta  |
+-----------------+
        |
        | 1
        |
        |----------------------< N
                              
                      +------------------+
                      |    RESPUESTA     |
                      +------------------+
                      | id (PK)          |
                      | texto_respuesta  |
                      | casa             |
                      | imagen           |
                      | pregunta_id (FK) |
                      +------------------+


<!-- El sistema está compuesto por tres entidades principales: Usuario, Pregunta y Respuesta.
La entidad Pregunta se relaciona con Respuesta mediante una relación 1:N, donde una pregunta puede tener múltiples respuestas, pero cada respuesta pertenece a una única pregunta.
La entidad Usuario almacena tanto administradores como jugadores, diferenciados mediante el atributo "rol". Además, se almacena la casa asignada tras completar el quiz. -->