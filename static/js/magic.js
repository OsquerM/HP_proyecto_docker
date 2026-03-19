// Obtenemos el elemento canvas del HTML por su id
const canvas = document.getElementById("magicCanvas");

// Obtenemos el contexto 2D del canvas, que es la herramienta para dibujar
const ctx = canvas.getContext("2d");

// Ajustamos el tamaño del canvas al tamaño de la ventana del navegador
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

// Array que almacenará todas las partículas activas
let particles = [];

// ─────────────────────────────────────────────────────────────
// Clase Particle: representa cada partícula mágica (estrellita dorada)
// ─────────────────────────────────────────────────────────────
class Particle {

    constructor() {
        // Posición horizontal aleatoria dentro del ancho del canvas
        this.x = Math.random() * canvas.width;

        // Posición vertical aleatoria dentro del alto del canvas
        this.y = Math.random() * canvas.height;

        // Tamaño aleatorio de la partícula (entre 0 y 3 píxeles)
        this.size = Math.random() * 3;

        // Velocidad vertical aleatoria (entre 0.2 y 0.7 píxeles por frame)
        this.speedY = Math.random() * 0.5 + 0.2;

        // Opacidad aleatoria (entre 0 totalmente transparente y 1 totalmente opaco)
        this.opacity = Math.random();
    }

    update() {
        // Movemos la partícula hacia arriba restando su velocidad a Y
        this.y -= this.speedY;

        // Si la partícula sale por arriba de la pantalla, la recolocamos abajo
        if (this.y < 0) {
            this.y = canvas.height;                  // vuelve a aparecer abajo
            this.x = Math.random() * canvas.width;   // en una posición horizontal aleatoria
        }
    }

    draw() {
        // Establecemos el color de relleno: dorado (255,215,0) con la opacidad de la partícula
        ctx.fillStyle = "rgba(255,215,0," + this.opacity + ")";

        // Iniciamos un nuevo trazado para dibujar la partícula
        ctx.beginPath();

        // Dibujamos un círculo: centro (x,y), radio (size), ángulo 0 a 2π (círculo completo)
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);

        // Rellenamos el círculo con el color definido
        ctx.fill();
    }
}

// ─────────────────────────────────────────────────────────────
// init: crea las 120 partículas iniciales y las añade al array
// ─────────────────────────────────────────────────────────────
function init() {
    
    for (let i = 0; i < 120; i++) {
        particles.push(new Particle());
    }

}

// ─────────────────────────────────────────────────────────────
// animate: bucle principal de animación, se ejecuta ~60 veces por segundo
// ─────────────────────────────────────────────────────────────
function animate() {
    // Borramos todo el canvas antes de redibujar (evita que queden rastros)
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Actualizamos y dibujamos cada partícula
    particles.forEach(p => {
        p.update(); // mueve la partícula
        p.draw();   // la dibuja en su nueva posición
    });

    // Pedimos al navegador que ejecute animate() en el siguiente frame
    // Esto crea el bucle de animación continuo
    requestAnimationFrame(animate);
}

// Inicializamos las partículas
init();

// Arrancamos el bucle de animación
animate();
