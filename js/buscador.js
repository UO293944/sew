/* ***************************************/
/*           LaVuelta2026                */
/*    Clase Buscador (buscador.js)       */
/* ***************************************/
/*  Nombre y Apellidos: David Álvarez Cabezas */
/*  Correo electrónico (uniovi): UO293944 */
/* ***************************************/

class Buscador {

    constructor() {
        // Clic sobre la lupa
        document.querySelector("search label img")
            .addEventListener("click", this.buscar.bind(this));
        // Tecla intro dentro del campo de búsqueda
        document.querySelector("search input")
            .addEventListener("keypress", (evento) => {
                if (evento.key === "Enter") {
                    this.buscar();
                }
            });
    }

    // Busca el texto introducido en el documento y resalta las apariciones con <mark>
    buscar() {
        this.limpiar_busqueda();

        const resultados = [];
        const texto_buscar = document.querySelector("search input").value.trim();

        if (texto_buscar !== "") {
            // Se escapan los caracteres especiales para buscar el texto literal
            const escapado = texto_buscar.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
            const expresion = new RegExp(escapado, "gi");

            const recorrido = document.createTreeWalker(document.querySelector("body"), NodeFilter.SHOW_TEXT);
            let nodo = recorrido.nextNode();
            while (nodo) {
                expresion.lastIndex = 0; // con el indicador 'g', test() recuerda la posición anterior
                if (expresion.test(nodo.textContent)) {
                    resultados.push(nodo);
                }
                nodo = recorrido.nextNode();
            }

            resultados.forEach(node => {
                const partes = node.textContent.split(new RegExp(`(${escapado})`, "gi"));
                node.replaceWith(...partes.map((parte, indice) => {
                    if (indice % 2 === 0) return document.createTextNode(parte);
                    const marca = document.createElement("mark");
                    marca.textContent = parte;
                    return marca;
                }));
            });
        }
    }

    // Elimina los resaltados de una búsqueda anterior conservando su contenido
    limpiar_busqueda() {
        document.querySelectorAll("mark").forEach(marca => {
            marca.replaceWith(document.createTextNode(marca.textContent));
        });
        document.body.normalize();
    }
}

const buscador = new Buscador();
