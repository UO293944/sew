/* ***************************************/
/*           LaVuelta2026                */
/*  Clases Ciclista y Equipo (equipo.js) */
/* ***************************************/
/*  Nombre y Apellidos: David Álvarez Cabezas */
/*  Correo electrónico (uniovi): UO293944 */
/* ***************************************/

class Ciclista {

    dorsal;
    nombre;
    apellidos;
    fechaNacimiento;
    nacionalidad;

    constructor(dorsal, nombre, apellidos, fechaNacimiento, nacionalidad) {
        this.dorsal = dorsal;
        this.nombre = nombre;
        this.apellidos = apellidos;
        this.fechaNacimiento = fechaNacimiento;
        this.nacionalidad = nacionalidad;
    }

    // Nombre completo: nombre seguido de los apellidos
    getNombreCompleto() {
        return this.nombre + " " + this.apellidos;
    }

    getDorsal() {
        return this.dorsal;
    }

    // Fecha de nacimiento (dd/mm/aaaa) y nacionalidad: "fecha, nacionalidad"
    getInformacionAdicional() {
        let fecha = String(this.fechaNacimiento);
        const iso = /^(\d{4})-(\d{2})-(\d{2})/.exec(fecha);
        if (iso) {
            fecha = iso[3] + "/" + iso[2] + "/" + iso[1];
        }
        return fecha + ", " + this.nacionalidad;
    }
}

class Equipo {

    // Atributos
    nombre;
    codigoUCI;
    pais;
    director;
    categoria;
    paginaWeb;
    alineacion;

    constructor(nombre, codigoUCI, pais) {
        this.nombre = nombre;
        this.codigoUCI = codigoUCI;
        this.pais = pais;
        this.alineacion = [];
    }

    // Rellena el valor del resto de atributos (Anexo I y ficha del equipo en lavuelta.es)
    rellenarAtributos() {
        this.director = "Sep Vanmarcke";
        this.categoria = "UCI WorldTeam";
        this.paginaWeb = "https://www.lavuelta.es/es/equipo/SOQ/soudal-quick-step";
    }

    datosBasicos() {
        return this.nombre + " (" + this.codigoUCI + ")";
    }

    getPais() {
        return this.pais;
    }

    // Devuelve una lista no ordenada HTML5 con la información secundaria
    getInformacionSecundaria() {
        return "<ul>" +
            "<li>Director del equipo: " + this.director + "</li>" +
            "<li>Categoría: " + this.categoria + "</li>" +
            "</ul>";
    }

    // Escribe en la primera sección del documento el enlace a la ficha oficial del equipo
    getPaginaWeb() {
        const parrafo = document.createElement("p");
        const enlace = document.createElement("a");
        enlace.setAttribute("href", this.paginaWeb);
        enlace.textContent = "Ficha oficial de " + this.nombre + " en La Vuelta";
        parrafo.appendChild(enlace);
        document.querySelector("section").appendChild(parrafo);
    }

    // Lee lavuelta.json y se queda con la información del equipo (filtrando por código UCI)
    async leerEquipo() {
        try {
            const respuesta = await fetch("js/recursos/lavuelta.json");
            if (!respuesta.ok) {
                throw new Error("HTTP " + respuesta.status);
            }
            const datos = await respuesta.json();
            const equipos = Array.isArray(datos) ? datos : (datos.equipos ?? Object.values(datos).find(Array.isArray));
            const miEquipo = equipos.find(equipo => (equipo.codigoUCI ?? equipo.codigo_uci ?? equipo.codigo ?? equipo.uci) === this.codigoUCI);
            this.alinearCiclistas(miEquipo.ciclistas ?? miEquipo.corredores ?? miEquipo.alineacion);
        } catch (error) {
            console.error("No se ha podido leer lavuelta.json:", error);
        }
    }

    // Crea un objeto Ciclista por cada corredor leído y lo guarda en la alineación
    alinearCiclistas(ciclistas) {
        this.alineacion = [];
        ciclistas.forEach(c => {
            this.alineacion.push(new Ciclista(
                c.dorsal,
                c.nombre,
                c.apellidos,
                c.fechaNacimiento ?? c.fecha_nacimiento ?? c.nacimiento,
                c.nacionalidad ?? c.pais
            ));
        });
    }

    // Añade a la sección de la alineación una tarjeta por ciclista, ordenados por dorsal
    mostrarAlineacion() {
        const seccion = document.querySelector("main > section:last-of-type");
        [...this.alineacion]
            .sort((a, b) => a.getDorsal() - b.getDorsal())
            .forEach(ciclista => {
                const tarjeta =
                    "<article>" +
                    "<h4>" + ciclista.getNombreCompleto() + "</h4>" +
                    "<img src=\"multimedia/ciclista-icono.png\" alt=\"Icono genérico de un ciclista\" width=\"128\" height=\"128\" />" +
                    "<p>Dorsal: " + ciclista.getDorsal() + "</p>" +
                    "<p>" + ciclista.getInformacionAdicional() + "</p>" +
                    "</article>";
                seccion.insertAdjacentHTML("beforeend", tarjeta);
            });
    }
}

// Equipo del ciclista del proyecto (Anexo I: Soudal Quick-Step, SOQ, Bélgica)
const equipo = new Equipo("Soudal Quick-Step", "SOQ", "Bélgica");
equipo.rellenarAtributos();

// Sección con la información del equipo
const seccionEquipo = document.createElement("section");

const encabezadoEquipo = document.createElement("h3");
encabezadoEquipo.textContent = equipo.datosBasicos() + " – " + equipo.getPais();
seccionEquipo.appendChild(encabezadoEquipo);
seccionEquipo.insertAdjacentHTML("beforeend", equipo.getInformacionSecundaria());

// Se inserta a continuación del encabezado h2, encima de la sección de la alineación
document.querySelector("h2").insertAdjacentElement("afterend", seccionEquipo);

// Enlace a la ficha del equipo y, después, la alineación leída del JSON
equipo.getPaginaWeb();
equipo.leerEquipo().then(() => equipo.mostrarAlineacion());
