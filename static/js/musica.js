// Obtenemos el elemento de audio y el botón del DOM
const music = document.getElementById("bgMusic");
const btn = document.getElementById("musicButton");

// Variable que controla si la música está sonando o no
let playing = false;

// toggleMusic: alterna entre reproducir y pausar la música
// y actualiza el texto del botón según el estado
function toggleMusic() {
    if (music.paused) {
        // Si la música está pausada la reproducimos
        music.play();
        btn.innerText = "🔊 Música ON";
        playing = true;
    } else {
        // Si la música está sonando la pausamos
        music.pause();
        btn.innerText = "🔇 Música OFF";
        playing = false;
    }
}

// Asignamos la función toggleMusic al click del botón
// en lugar de usar onclick en el HTML
btn.addEventListener("click", toggleMusic);

// Los navegadores bloquean el autoplay hasta que el usuario
// interactúa con la página, por eso esperamos al primer click
// en cualquier parte del body para intentar arrancar la música
document.body.addEventListener("click", function initMusic() {
    if (!playing) {
        // Intentamos reproducir la música
        // play() devuelve una promesa, por eso usamos .then() y .catch()
        music.play().then(() => {
            // Si el navegador permite el autoplay, actualizamos el botón
            btn.innerText = "🔊 Música ON";
            playing = true;
        }).catch(err => {
            // Si el navegador bloquea el autoplay, esperamos a que el usuario
            // pulse el botón manualmente
            console.log("Autoplay bloqueado, espera a pulsar el botón");
        });
    }
    // Eliminamos este listener después del primer click porque
    // solo necesitamos intentar arrancar la música una vez
    document.body.removeEventListener("click", initMusic);
});