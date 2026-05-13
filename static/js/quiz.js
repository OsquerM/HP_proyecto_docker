// BASE_URL: obtiene la URL base de la página actual (protocolo + dominio + puerto)
// Ejemplo: si estás en http://localhost:5000/quiz, BASE_URL = "http://localhost:5000"
// Así evitamos problemas de CORS y la app funciona en cualquier entorno sin hardcodear rutas

const BASE_URL = window.location.origin;


// Objeto global que actúa como estado temporal del quiz en memoria
// Guarda el nombre del usuario y sus respuestas mientras dura la sesión en el navegador
// Se pierde al recargar la página ya que vive solo en JavaScript

const quizData = {
    usuario: "",      // nombre del usuario introducido en el formulario
    respuestas: {}    // respuestas seleccionadas: { pregunta_id: respuesta_id }
};


// cargarPreguntas: llama a la API del backend para obtener las preguntas
// y construye dinámicamente el HTML del formulario con sus opciones de respuesta

async function cargarPreguntas() {
    try {
        console.log("Cargando preguntas desde:", `${BASE_URL}/quiz/preguntas`);

        // Petición GET al backend para obtener las preguntas almacenadas en la BD
        const res = await fetch(`${BASE_URL}/quiz/preguntas`);

        // Si el servidor responde con error (ej: 404, 500), lanzamos una excepción
        // ok es una propiedad nativa del objeto Response que viene de usar fetch()
        if (!res.ok) {
            throw new Error(`Error ${res.status}: ${res.statusText}`);
        }

        // Convertimos la respuesta JSON que manda el backend a un objeto JavaScript para poder manipular los datos 
        // y construir el HTML dinámicamente
        const data = await res.json();
        console.log("Preguntas recibidas:", data);

        // Buscamos el contenedor donde se mostrarán las preguntas en el DOM
        const contenedor = document.getElementById("preguntas");
        if (!contenedor) {
            // Si no existe el div#preguntas, no estamos en quiz.html → salimos sin hacer nada
            console.error("No se encontró div id='preguntas'");
            return;
        }

        // Limpiamos el contenedor para evitar duplicados
        contenedor.innerHTML = "";

        // Si no hay preguntas en la BD, mostramos un mensaje informativo al usuario
        if (!data.preguntas || data.preguntas.length === 0) {
            contenedor.innerHTML = "<p>No hay preguntas disponibles.</p>";
            return;
        }

        // Recorremos cada pregunta recibida y construimos su HTML dinámicamente
        data.preguntas.forEach(p => {
            // Creamos el div contenedor de cada pregunta individual
            const div = document.createElement("div");
            div.className = "pregunta";

            // Creamos el párrafo con el texto de la pregunta
            const titulo = document.createElement("p");
            titulo.textContent = p.texto_pregunta;
            div.appendChild(titulo);

            // Creamos el grid donde irán las opciones de respuesta en forma de tarjetas
            const grid = document.createElement("div");
            grid.className = "opciones-imagenes";

            // Recorremos cada respuesta posible de la pregunta
            p.respuestas.forEach(r => {
                // Creamos el div de cada opción individual
                const opcion = document.createElement("div");
                opcion.className = "opcion";

                // Si la respuesta tiene imagen asociada, construimos su HTML
                let imgHtml = "";
                if (r.imagen) {
                    // Eliminamos el prefijo "uploads/" para construir la URL correcta del servidor
                    //Evitamos que se construya duplicado
                    let imagenPath = r.imagen.replace(/^uploads\//, '');
                    imgHtml = `<img src="${BASE_URL}/static/uploads/${imagenPath}" alt="${r.texto}" loading="lazy">`;
                }

                // Inyectamos la imagen + radio button + texto de la respuesta en la opción
                opcion.innerHTML = `
                    ${imgHtml}
                    <br>
                    <input type="radio" name="pregunta_${p.id}" value="${r.id}" required>
                    ${r.texto}
                `;

                // Al hacer click en la opción, marcamos su radio y resaltamos visualmente la selección
                opcion.addEventListener("click", () => {
                    const radio = opcion.querySelector("input");
                    radio.checked = true;

                    // Quitamos la clase "seleccionada" de todas las opciones de esta pregunta
                    // para que solo quede resaltada la recién clicada
                    //r abreviacion radio
                    document.querySelectorAll(`input[name="pregunta_${p.id}"]`).forEach(r => {
                        r.parentElement.classList.remove("seleccionada");
                    });
                    //parentElement es el elemento padre
                    // Añadimos la clase "seleccionada" solo a la opción clicada
                    opcion.classList.add("seleccionada");
                });
                //Montamos todo el DOM con appendchild
                grid.appendChild(opcion);
            });

            div.appendChild(grid);
            contenedor.appendChild(div);
        });

    } catch (err) {
        // Si hay cualquier error en el proceso, lo mostramos en rojo dentro del contenedor
        console.error("Error cargando preguntas:", err);
        const contenedor = document.getElementById("preguntas");
        if (contenedor) {
            contenedor.innerHTML = `<p style="color:red">Error: ${err.message}</p>`;
        }
    }
}


// Validación en tiempo real del campo nombre:
// Colorea el borde en rojo si tiene menos de 3 caracteres, verde si cumple el mínimo
// Solo se registra si el elemento existe en el DOM (protección para otras páginas)
//value obtiene el texto
//trim quita los espacios al principio y final
//length lee el numero de caracteres 

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
// Recoge las respuestas seleccionadas, las valida y las manda al backend
// Solo se ejecuta si existe el formulario en el DOM (protección para otras páginas)

const quizForm = document.getElementById("quizForm");
if (quizForm) {
    // e = evento abreviación 
    quizForm.addEventListener("submit", async function(e) {
        // Evitamos que el formulario recargue la página con su comportamiento por defecto
        e.preventDefault();
        //evita que la página se recargue
        //evita que el form se envíe “solo”
        //te deja usar fetch() en su lugar
        
        const usuario = document.getElementById("usuario").value.trim();

        // Validamos que el nombre no esté vacío antes de continuar
        if (!usuario) {
            alert("Ingresa tu nombre");
            return;
        }

        // Recogemos todos los radios que el usuario ha marcado
        const radios = document.querySelectorAll("input[type='radio']:checked");

        if (radios.length === 0) {
            alert("Responde todas las preguntas");
            return;
        }

        // Construimos el objeto de respuestas con formato { pregunta_id: respuesta_id }
        const respuestas_usuario = {};
        radios.forEach(r => {
            const pregunta_id = r.name.split("_")[1]; // extraemos el id numérico de "pregunta_X"
            respuestas_usuario[pregunta_id] = parseInt(r.value);
        });

        // Guardamos los datos en el objeto global quizData por si se necesitan después
        quizData.usuario = usuario;
        quizData.respuestas = respuestas_usuario;

        // Deshabilitamos el botón para evitar que el usuario envíe el formulario dos veces
        const btn = document.querySelector("button");
        if (btn) {
            btn.disabled = true;
            btn.textContent = "Enviando...";
        }

        try {
            // Enviamos las respuestas al backend mediante POST en formato JSON
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

            // Recibimos el resultado del backend con la casa de Hogwarts asignada
            const resultado = await res.json();

            // Redirigimos a la página de resultado pasando nombre y casa por parámetros de URL
            window.location.href = `${BASE_URL}/quiz/resultado?nombre=${encodeURIComponent(resultado.usuario)}&casa=${encodeURIComponent(resultado.casa)}`;
            //Convierte caracteres especiales como espacios o acentos y evitamos romper la URL y el backend 

        } catch (err) {
            console.error("Error:", err);
            alert("Problema al enviar respuestas");

            // Rehabilitamos el botón si hubo error para que el usuario pueda reintentar
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
    // Buscamos el contenedor donde se inyectará el personaje en el DOM
    const container = document.getElementById('personaje-container');
    if (!container) {
        console.warn('No se encontró #personaje-container en la página');
        return;
    }

    try {
        // Convertimos la casa a minúsculas para que coincida con el formato que espera la API
        const casaApi = casa.toLowerCase();
        const res = await fetch(`https://hp-api.onrender.com/api/characters/house/${casaApi}`);
        //Si no responde nos manda el error
        if (!res.ok) {
            throw new Error('Error al conectar con HP-API');
        }

        const personajes = await res.json();

        if (!personajes || personajes.length === 0) {
            throw new Error('No hay personajes para esta casa');
        }

        // Filtramos solo los personajes que tienen imagen disponible para mostrar
        // Si ninguno tiene imagen, usamos la lista completa como fallback
        const conImagen = personajes.filter(p => p.image && p.image.trim() !== "");
        const lista = conImagen.length > 0 ? conImagen : personajes;

        // Elegimos un personaje al azar de la lista filtrada
        const randomIndex = Math.floor(Math.random() * lista.length);
        const personaje = lista[randomIndex];

        // Construimos el HTML con los datos del personaje obtenido
        let html = `
            <h3 style="margin-bottom: 15px;">¡Un ${casa} famoso<br>te da la bienvenida!</h3>
        `;

        // Si tiene imagen la mostramos, si no ponemos un mensaje informativo
        if (personaje.image) {
            html += `
                <img src="${personaje.image}" alt="${personaje.name}" 
                     style="width: 180px; height: 250px; object-fit: cover; border-radius: 12px; box-shadow: 0 0 20px gold; margin-bottom: 15px;">
            `;
        } else {
            html += '<p style="color: #ccc;">(Sin imagen disponible)</p>';
        }

        // Añadimos nombre, especie y actor del personaje debajo de la imagen
        html += `
            <p style="font-size: 1.3rem; font-weight: bold;">${personaje.name}</p>
            <p> Actor: ${personaje.actor || 'Desconocido'}</p>
        `;

        // Inyectamos todo el HTML generado en el contenedor de la página
        container.innerHTML = html;

    } catch (err) {
        // Si la API falla, mostramos un mensaje amigable en lugar de romper la página
        console.error('Error cargando personaje HP-API:', err);
        container.innerHTML = `
            <p style="margin-top: 30px; color: #ffcc00; font-size: 1.1rem;">
                No pudimos cargar un personaje mágico... ¡pero sigues siendo un gran ${casa}! 🪄
            </p>
        `;
    }
}


// Cuando el DOM está completamente cargado, intentamos mostrar el personaje
// usando dos métodos en orden de prioridad:
// 1. La variable CASA_ASIGNADA inyectada directamente por Jinja2 en resultado.html
// 2. El parámetro ?casa= de la URL como fallback si no existe la variable de Jinja2

document.addEventListener('DOMContentLoaded', () => {
    if (typeof CASA_ASIGNADA !== 'undefined' && CASA_ASIGNADA) {
        mostrarPersonajeCasa(CASA_ASIGNADA);
        return;
    }
    // Fallback: lee la casa del parámetro de URL (?casa=Gryffindor)
    const params = new URLSearchParams(window.location.search);
    const casa = params.get('casa');
    if (casa) {
        mostrarPersonajeCasa(casa);
    }
});


// Comprobamos si existe el div#preguntas en el DOM antes de llamar a cargarPreguntas()
// Así el script puede estar incluido en varias páginas sin romperse:
// solo carga las preguntas cuando realmente se está en quiz.html

if (document.getElementById("preguntas")) {
    cargarPreguntas();
}