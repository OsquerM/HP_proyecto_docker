// BASE_URL dinámico → soluciona CORS (usa la misma URL que cargó la página)
const BASE_URL = window.location.origin;

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
                    // Quitamos "uploads/" del principio si existe (para evitar doble /uploads/uploads/)
                    let imagenPath = r.imagen.replace(/^uploads\//, '');
                    imgHtml = `<img src="${BASE_URL}/static/uploads/${imagenPath}" alt="${r.texto}" loading="lazy">`;
                }

                opcion.innerHTML = `
                    ${imgHtml}
                    <br>
                    <input type="radio" name="pregunta_${p.id}" value="${r.id}" required>
                    ${r.texto}
                `;

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

document.getElementById("quizForm").addEventListener("submit", async function(e) {
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

        window.location.href = `${BASE_URL}/quiz/resultado?nombre=${encodeURIComponent(resultado.usuario)}&casa=${encodeURIComponent(resultado.casa)}`;
    } catch (err) {
        console.error("Error:", err);
        alert("Problema al enviar respuestas");
    }
});

cargarPreguntas();