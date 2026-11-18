/* ***************************************/
/*           LaVuelta2026                */
/*     Clase Ciudad (ciudad.js)          */
/* ***************************************/
/*  Nombre y Apellidos: David Álvarez Cabezas */
/*  Correo electrónico (uniovi): UO293944 */
/* ***************************************/

class Ciudad {

    // Atributos: nombre, pais, gentilicio, poblacion y coordenadas del punto central
    nombre;
    pais;
    gentilicio;
    poblacion;
    coordenadas;

    constructor(nombre, pais, gentilicio) {
        this.nombre = nombre;
        this.pais = pais;
        this.gentilicio = gentilicio;
    }

    // Rellena el valor del resto de atributos (los datos proceden de etapa.xml)
    rellenarAtributos() {
        this.poblacion = 21659; // Habitantes (INE)
        this.coordenadas = {
            latitud: 39.5936,   // grados
            longitud: -0.3081,  // grados
            altitud: 50         // metros
        };
    }

    getCiudad() {
        return this.nombre;
    }

    getPais() {
        return this.pais;
    }

    // Devuelve, en forma de texto, una lista no ordenada HTML5 con la información secundaria
    getInformacionSecundaria() {
        return "<ul>" +
            "<li>Gentilicio: " + this.gentilicio + "</li>" +
            "<li>Población: " + this.poblacion.toLocaleString("es-ES") + " habitantes</li>" +
            "</ul>";
    }

    // Escribe en la primera sección del documento las coordenadas del punto elegido
    escribeCoordenadas() {
        const parrafo = document.createElement("p");
        parrafo.textContent = "Coordenadas del punto central: latitud " + this.coordenadas.latitud +
            "°, longitud " + this.coordenadas.longitud + "°, altitud " + this.coordenadas.altitud + " m.";
        document.querySelector("section").appendChild(parrafo);
    }
}

// Ciudad de salida de la etapa 8 (Puçol – Xeraco)
const ciudad = new Ciudad("Puçol", "España", "puzolense");
ciudad.rellenarAtributos();

// Sección con la información de la ciudad
const seccionCiudad = document.createElement("section");

const encabezadoCiudad = document.createElement("h3");
encabezadoCiudad.textContent = ciudad.getCiudad() + " (" + ciudad.getPais() + ")";
seccionCiudad.appendChild(encabezadoCiudad);
seccionCiudad.insertAdjacentHTML("beforeend", ciudad.getInformacionSecundaria());

// Se inserta a continuación del encabezado h2 "Meteorología"
document.querySelector("h2").insertAdjacentElement("afterend", seccionCiudad);

// Coordenadas en la sección recién añadida (primera sección del documento)
ciudad.escribeCoordenadas();
