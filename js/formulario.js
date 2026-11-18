/* ***************************************/
/*           LaVuelta2026                */
/*   Clase Formulario (formulario.js)    */
/* ***************************************/
/*  Nombre y Apellidos: David Álvarez Cabezas */
/*  Correo electrónico (uniovi): UO293944 */
/* ***************************************/

class Formulario {

    puntuacion;
    dureza;
    descripcion;
    usuario;
    resultado; // párrafo con la calificación mostrada

    constructor() {
        this.puntuacion = 0;
        document.querySelector("form button[type=\"submit\"]")
            .addEventListener("click", this.analizar.bind(this));
    }

    analizar(event) {
        event.preventDefault();
        const form = event.target.closest("form");
        if (!form.reportValidity()) {
            return; // faltan campos obligatorios
        }
        this.puntuacion = 0;

        // Preguntas calificadas (respuestas de la etapa 8: Puçol a Xeraco)
        if (form.querySelector("input[name=\"numero-etapa\"]").value === "8") this.puntuacion++;
        if (form.querySelector("input[name=\"fecha-etapa\"]").value === "2026-08-29") this.puntuacion++;
        if (form.querySelector("select[name=\"salida\"]").value === "Puçol") this.puntuacion++;
        if (form.querySelector("select[name=\"llegada\"]").value === "Xeraco") this.puntuacion++;

        const tipo = form.querySelector("input[name=\"tipo-etapa\"]:checked");
        if (tipo !== null && tipo.value === "llana") this.puntuacion++;

        // Hitos: puerto de montaña y sprint intermedio (y ningún otro)
        const hitos = [...form.querySelectorAll("input[name=\"hitos\"]:checked")]
            .map(hito => hito.value).sort().join(",");
        if (hitos === "puerto,sprint-intermedio") this.puntuacion++;

        if (parseFloat(form.querySelector("input[name=\"longitud\"]").value) === 171) this.puntuacion++;
        if (parseInt(form.querySelector("input[name=\"desnivel\"]").value, 10) === 1281) this.puntuacion++;

        // Respuestas no calificadas, necesarias para el mensaje
        this.dureza = form.querySelector("input[name=\"dureza\"]").value;
        this.descripcion = form.querySelector("textarea[name=\"descripcion\"]").value;
        this.usuario = form.querySelector("input[name=\"usuario\"]").value;

        this.calificar();
    }

    calificar() {
        if (this.resultado) {
            this.resultado.remove(); // elimina la calificación anterior
        }
        this.resultado = document.createElement("p");
        this.resultado.setAttribute("role", "status");
        this.resultado.textContent = this.usuario + " has obtenido " + this.puntuacion +
            " puntos, la dureza que has asignado a la etapa es " + this.dureza +
            " y tu descripción " + this.descripcion;
        document.querySelector("form").insertAdjacentElement("afterend", this.resultado);
    }
}

const formulario = new Formulario();
