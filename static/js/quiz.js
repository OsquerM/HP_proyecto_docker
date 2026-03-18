// BASE_URL dinámico → soluciona CORS (usa la misma URL que cargó la página)
const BASE_URL = window.location.origin;

// 🔹 Objeto global del quiz 
const quizData = {
    usuario: "",
    respuestas: {}
};

async function cargarPreguntas() {
    try {
        console.log("Cargando preguntas desde:", `${BASE_URL}/quiz/preguntas`);

        const res = await fetch(`${BASE_URL}/quiz/preguntas`);

        if (!res.ok) {
            throw new Error(`Error ${res.status}: ${res.statusText}`);
        }

        const data = await res.json();
        console.log("Preguntas recibidas:", data);

        const contenedor = document.getElementById("preguntas");
        if (!contenedor) {
            console.error("No se encontró div id='preguntas'");
            return;
        }

        contenedor.innerHTML = "";

        if (!data.preguntas || data.preguntas.length === 0) {
            contenedor.innerHTML = "<p>No hay preguntas disponibles.</p>";
            return;
        }

        data.preguntas.forEach(p => {
            const div = document.createElement("div");
            div.className = "pregunta";

            const titulo = document.createElement("p");
            titulo.textContent = p.texto_pregunta;
            div.appendChild(titulo);

            const grid = document.createElement("div");
            grid.className = "opciones-imagenes";

            p.respuestas.forEach(r => {
                const opcion = document.createElement("div");
                opcion.className = "opcion";

                let imgHtml = "";
                if (r.imagen) {
                    let imagenPath = r.imagen.replace(/^uploads\//, '');
                    imgHtml = `<img src="${BASE_URL}/static/uploads/${imagenPath}" alt="${r.texto}" loading="lazy">`;
                }

                opcion.innerHTML = `
                    ${imgHtml}
                    <br>
                    <input type="radio" name="pregunta_${p.id}" value="${r.id}" required>
                    ${r.texto}
                `;

                opcion.addEventListener("click", () => {
                    const radio = opcion.querySelector("input");
                    radio.checked = true;

                    document.querySelectorAll(`input[name="pregunta_${p.id}"]`).forEach(r => {
                        r.parentElement.classList.remove("seleccionada");
                    });

                    opcion.classList.add("seleccionada");
                });

                grid.appendChild(opcion);
            });

            div.appendChild(grid);
            contenedor.appendChild(div);
        });

    } catch (err) {
        console.error("Error cargando preguntas:", err);
        const contenedor = document.getElementById("preguntas");
        if (contenedor) {
            contenedor.innerHTML = `<p style="color:red">Error: ${err.message}</p>`;
        }
    }
}

// 🔹 VALIDACIÓN EN TIEMPO REAL (UX)
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

const quizForm = document.getElementById("quizForm");
if (quizForm) {
    quizForm.addEventListener("submit", async function(e) {
        e.preventDefault();

        const usuario = document.getElementById("usuario").value.trim();

        if (!usuario) {
            alert("Ingresa tu nombre");
            return;
        }

        const radios = document.querySelectorAll("input[type='radio']:checked");

        if (radios.length === 0) {
            alert("Responde todas las preguntas");
            return;
        }

        const respuestas_usuario = {};

        radios.forEach(r => {
            const pregunta_id = r.name.split("_")[1];
            respuestas_usuario[pregunta_id] = parseInt(r.value);
        });

        quizData.usuario = usuario;
        quizData.respuestas = respuestas_usuario;

        const btn = document.querySelector("button");
        if (btn) {
            btn.disabled = true;
            btn.textContent = "Enviando...";
        }

        try {
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

            const resultado = await res.json();

            // Redirección a resultado (sin llamada aquí, se hace desde resultado.html)
            window.location.href = `${BASE_URL}/quiz/resultado?nombre=${encodeURIComponent(resultado.usuario)}&casa=${encodeURIComponent(resultado.casa)}`;

        } catch (err) {
            console.error("Error:", err);
            alert("Problema al enviar respuestas");

            if (btn) {
                btn.disabled = false;
                btn.textContent = "Enviar";
            }
        }
    });
}

// ────────────────────────────────────────────────
// Cargar personaje random de la casa desde HP-API
// ────────────────────────────────────────────────
async function mostrarPersonajeCasa(casa) {
    const container = document.getElementById('personaje-container');
    if (!container) {
        console.warn('No se encontró #personaje-container en la página');
        return;
    }

    try {
        const casaApi = casa.toLowerCase();
        const res = await fetch(`https://hp-api.onrender.com/api/characters/house/${casaApi}`);

        if (!res.ok) {
            throw new Error('Error al conectar con HP-API');
        }

        const personajes = await res.json();

        if (!personajes || personajes.length === 0) {
            throw new Error('No hay personajes para esta casa');
        }

        // ✅ Filtra primero los que tienen imagen, si no hay ninguno usa todos
        const conImagen = personajes.filter(p => p.image && p.image.trim() !== "");
        const lista = conImagen.length > 0 ? conImagen : personajes;
        const randomIndex = Math.floor(Math.random() * lista.length);
        const personaje = lista[randomIndex];

        let html = `
            <h3 style="margin-bottom: 15px;">¡Un ${casa} famoso te da la bienvenida!</h3>
        `;

        if (personaje.image) {
            html += `
                <img src="${personaje.image}" alt="${personaje.name}" 
                     style="width: 180px; height: 250px; object-fit: cover; border-radius: 12px; box-shadow: 0 0 20px gold; margin-bottom: 15px;">
            `;
        } else {
            html += '<p style="color: #ccc;">(Sin imagen disponible)</p>';
        }

        html += `
            <p style="font-size: 1.3rem; font-weight: bold;">${personaje.name}</p>
            <p>${personaje.species || 'Humano'} • Actor: ${personaje.actor || 'Desconocido'}</p>
        `;

        container.innerHTML = html;
    } catch (err) {
        console.error('Error cargando personaje HP-API:', err);
        
        container.innerHTML = `
            <p style="margin-top: 30px; color: #ffcc00; font-size: 1.1rem;">
                No pudimos cargar un personaje mágico... ¡pero sigues siendo un gran ${casa}! 🪄
            </p>
        `;
    }
}

// Ejecutar cuando la página de resultado se carga
document.addEventListener('DOMContentLoaded', () => {
    // ✅ Primero intenta leer la casa desde la variable inyectada por Jinja2
    if (typeof CASA_ASIGNADA !== 'undefined' && CASA_ASIGNADA) {
        mostrarPersonajeCasa(CASA_ASIGNADA);
        return;
    }
    // Fallback: lee de la URL por si acaso
    const params = new URLSearchParams(window.location.search);
    const casa = params.get('casa');
    if (casa) {
        mostrarPersonajeCasa(casa);
    }
});

// 🔹 Ejecutar carga inicial solo si estamos en la página del quiz
if (document.getElementById("preguntas")) {
    cargarPreguntas();
}