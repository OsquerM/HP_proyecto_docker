
// BASE_URL: obtiene la URL base de la página actual
// Así evitamos problemas de CORS y la app funciona en cualquier entorno

const BASE_URL = window.location.origin;


// Objeto global que almacena temporalmente los datos del quiz
// mientras el usuario lo está haciendo

const quizData = {
    usuario: "",      // nombre del usuario
    respuestas: {}    // respuestas seleccionadas por el usuario
};


// cargarPreguntas: llama a la API del backend para obtener
// las preguntas

async function cargarPreguntas() {
    try {
        console.log("Cargando preguntas desde:", `${BASE_URL}/quiz/preguntas`);

        // Petición GET al backend para obtener las preguntas
        const res = await fetch(`${BASE_URL}/quiz/preguntas`);

        // Si el servidor responde con error, lanzamos una excepción
        if (!res.ok) {
            throw new Error(`Error ${res.status}: ${res.statusText}`);
        }

        // Convertimos la respuesta a JSON
        const data = await res.json();
        console.log("Preguntas recibidas:", data);

        // Buscamos el contenedor donde se mostrarán las preguntas
        const contenedor = document.getElementById("preguntas");
        if (!contenedor) {
            // Si no existe el div#preguntas, no estamos en quiz.html → salimos
            console.error("No se encontró div id='preguntas'");
            return;
        }

        // Limpiamos el contenedor antes de pintar
        contenedor.innerHTML = "";

        // Si no hay preguntas en la BD, mostramos un mensaje
        if (!data.preguntas || data.preguntas.length === 0) {
            contenedor.innerHTML = "<p>No hay preguntas disponibles.</p>";
            return;
        }

        // Recorremos cada pregunta y construimos su HTML dinámicamente
        data.preguntas.forEach(p => {
            // Creamos el div contenedor de la pregunta
            const div = document.createElement("div");
            div.className = "pregunta";

            // Creamos el título de la pregunta
            const titulo = document.createElement("p");
            titulo.textContent = p.texto_pregunta;
            div.appendChild(titulo);

            // Creamos el grid donde irán las opciones de respuesta
            const grid = document.createElement("div");
            grid.className = "opciones-imagenes";

            // Recorremos cada respuesta de la pregunta
            p.respuestas.forEach(r => {
                // Creamos el div de cada opción
                const opcion = document.createElement("div");
                opcion.className = "opcion";

                // Si la respuesta tiene imagen, construimos el HTML de la imagen
                let imgHtml = "";
                if (r.imagen) {
                    // Eliminamos el prefijo "uploads/" para construir la URL correcta
                    let imagenPath = r.imagen.replace(/^uploads\//, '');
                    imgHtml = `<img src="${BASE_URL}/static/uploads/${imagenPath}" alt="${r.texto}" loading="lazy">`;
                }

                // Inyectamos la imagen + radio button + texto de la respuesta
                opcion.innerHTML = `
                    ${imgHtml}
                    <br>
                    <input type="radio" name="pregunta_${p.id}" value="${r.id}" required>
                    ${r.texto}
                `;

                // Al hacer click en la opción, marcamos su radio y resaltamos visualmente
                opcion.addEventListener("click", () => {
                    const radio = opcion.querySelector("input");
                    radio.checked = true;

                    // Quitamos la clase "seleccionada" de todas las opciones de esta pregunta
                    document.querySelectorAll(`input[name="pregunta_${p.id}"]`).forEach(r => {
                        r.parentElement.classList.remove("seleccionada");
                    });

                    // Añadimos la clase "seleccionada" solo a la opción clicada
                    opcion.classList.add("seleccionada");
                });

                grid.appendChild(opcion);
            });

            div.appendChild(grid);
            contenedor.appendChild(div);
        });

    } catch (err) {
        // Si hay cualquier error, lo mostramos en rojo dentro del contenedor
        console.error("Error cargando preguntas:", err);
        const contenedor = document.getElementById("preguntas");
        if (contenedor) {
            contenedor.innerHTML = `<p style="color:red">Error: ${err.message}</p>`;
        }
    }
}


// Validación en tiempo real del campo nombre:
// muestra borde rojo si tiene menos de 3 caracteres, verde si no

const inputUsuario = document.getElementById("usuario");
if (inputUsuario) {
    inputUsuario.addEventListener("input", function() {
        if (this.value.trim().length < 3) {
            this.style.border = "2px solid red";
        } else {
            this.style.border = "2px solid green";
        }
    });
}


// Envío del formulario del quiz:
// recoge las respuestas seleccionadas y las manda al backend
// Solo se ejecuta si existe el formulario 

const quizForm = document.getElementById("quizForm");
if (quizForm) {
    quizForm.addEventListener("submit", async function(e) {
        // Evitamos que el formulario recargue la página
        e.preventDefault();

        const usuario = document.getElementById("usuario").value.trim();

        // Validamos que el nombre no esté vacío
        if (!usuario) {
            alert("Ingresa tu nombre");
            return;
        }

        // Recogemos todos los radios marcados
        const radios = document.querySelectorAll("input[type='radio']:checked");

        if (radios.length === 0) {
            alert("Responde todas las preguntas");
            return;
        }

        // Construimos el objeto de respuestas: { pregunta_id: respuesta_id }
        const respuestas_usuario = {};
        radios.forEach(r => {
            const pregunta_id = r.name.split("_")[1]; // extraemos el id de "pregunta_X"
            respuestas_usuario[pregunta_id] = parseInt(r.value);
        });

        // Guardamos en el objeto global
        quizData.usuario = usuario;
        quizData.respuestas = respuestas_usuario;

        // Deshabilitamos el botón para evitar doble envío
        const btn = document.querySelector("button");
        if (btn) {
            btn.disabled = true;
            btn.textContent = "Enviando...";
        }

        try {
            // Enviamos las respuestas al backend mediante POST
            const res = await fetch(`${BASE_URL}/quiz/enviar_respuestas`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    usuario_nombre: usuario,
                    respuestas_usuario
                })
            });

            if (!res.ok) {
                throw new Error("Error al enviar");
            }

            // Recibimos el resultado con la casa asignada
            const resultado = await res.json();

            // Redirigimos a la página de resultado pasando nombre y casa por URL
            window.location.href = `${BASE_URL}/quiz/resultado?nombre=${encodeURIComponent(resultado.usuario)}&casa=${encodeURIComponent(resultado.casa)}`;

        } catch (err) {
            console.error("Error:", err);
            alert("Problema al enviar respuestas");

            // Rehabilitamos el botón si hubo error
            if (btn) {
                btn.disabled = false;
                btn.textContent = "Enviar";
            }
        }
    });
}


// mostrarPersonajeCasa: llama a la HP-API pública para obtener
// un personaje aleatorio de la casa asignada y lo muestra
// en el div#personaje-container de resultado.html

async function mostrarPersonajeCasa(casa) {
    // Buscamos el contenedor donde se inyectará el personaje
    const container = document.getElementById('personaje-container');
    if (!container) {
        console.warn('No se encontró #personaje-container en la página');
        return;
    }

    try {
        // Convertimos la casa a minúsculas para la URL de la API
        const casaApi = casa.toLowerCase();
        const res = await fetch(`https://hp-api.onrender.com/api/characters/house/${casaApi}`);

        if (!res.ok) {
            throw new Error('Error al conectar con HP-API');
        }

        const personajes = await res.json();

        if (!personajes || personajes.length === 0) {
            throw new Error('No hay personajes para esta casa');
        }

        // Filtramos solo los personajes que tienen imagen disponible
        // Si ninguno tiene imagen, usamos la lista completa como fallback
        const conImagen = personajes.filter(p => p.image && p.image.trim() !== "");
        const lista = conImagen.length > 0 ? conImagen : personajes;

        // Elegimos un personaje al azar de la lista filtrada
        const randomIndex = Math.floor(Math.random() * lista.length);
        const personaje = lista[randomIndex];

        // Construimos el HTML con los datos del personaje
        let html = `
            <h3 style="margin-bottom: 15px;">¡Un ${casa} famoso<br>te da la bienvenida!</h3>
        `;

        // Si tiene imagen la mostramos, si no ponemos un mensaje
        if (personaje.image) {
            html += `
                <img src="${personaje.image}" alt="${personaje.name}" 
                     style="width: 180px; height: 250px; object-fit: cover; border-radius: 12px; box-shadow: 0 0 20px gold; margin-bottom: 15px;">
            `;
        } else {
            html += '<p style="color: #ccc;">(Sin imagen disponible)</p>';
        }

        // Añadimos nombre, especie y actor del personaje
        html += `
            <p style="font-size: 1.3rem; font-weight: bold;">${personaje.name}</p>
            <p> Actor: ${personaje.actor || 'Desconocido'}</p>
        `;

        // Inyectamos todo el HTML en el contenedor
        container.innerHTML = html;

    } catch (err) {
        // Si la API falla, mostramos un mensaje de error amigable
        console.error('Error cargando personaje HP-API:', err);
        container.innerHTML = `
            <p style="margin-top: 30px; color: #ffcc00; font-size: 1.1rem;">
                No pudimos cargar un personaje mágico... ¡pero sigues siendo un gran ${casa}! 🪄
            </p>
        `;
    }
}


// Cuando el DOM está listo, intentamos mostrar el personaje:
// 1. Primero busca la variable CASA_ASIGNADA inyectada por Jinja2
//    (disponible en resultado.html)
// 2. Si no existe, intenta leerla de los parámetros de la URL

document.addEventListener('DOMContentLoaded', () => {
    if (typeof CASA_ASIGNADA !== 'undefined' && CASA_ASIGNADA) {
        mostrarPersonajeCasa(CASA_ASIGNADA);
        return;
    }
    // Fallback: lee la casa de la URL (?casa=Gryffindor)
    const params = new URLSearchParams(window.location.search);
    const casa = params.get('casa');
    if (casa) {
        mostrarPersonajeCasa(casa);
    }
});


// Solo cargamos las preguntas si estamos en quiz.html
// (comprobando que existe el div#preguntas en el DOM)

if (document.getElementById("preguntas")) {
    cargarPreguntas();
}