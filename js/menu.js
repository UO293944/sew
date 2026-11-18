/* ***************************************/
/*           LaVuelta2026                */
/*       Clase Menu (menu.js)            */
/* ***************************************/
/*  Nombre y Apellidos: David Álvarez Cabezas */
/*  Correo electrónico (uniovi): UO293944 */
/* ***************************************/

class Menu {

    boton;
    menu;

    constructor() {
        this.boton = document.querySelector("header > button");
        this.menu = document.querySelector("nav");
        this.boton.addEventListener("click", this.desplegar.bind(this));
    }

    // Abre/cierra el menú de navegación en dispositivos móviles
    desplegar() {
        const nav = document.querySelector("nav");
        const abierto = nav.classList.toggle("abierto");
        this.boton.textContent = abierto ? "x" : "☰";
        this.boton.setAttribute("aria-expanded", String(abierto));
        this.boton.setAttribute("aria-label", abierto ? "Cerrar menú de navegación" : "Abrir menú de navegación");
    }
}

const menu = new Menu();
