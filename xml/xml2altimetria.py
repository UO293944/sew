# -*- coding: utf-8 -*-
"""
xml2altimetria.py
Genera el archivo altimetria.svg (perfil altimetrico de la etapa) a partir de
etapaEsquema.xml.

- El XML se lee con xml.etree.ElementTree y los datos (distancias y altitudes)
  se obtienen con expresiones XPath usando el espacio de nombres http://www.uniovi.es.
- Programa totalmente orientado a objetos: todas las funciones son metodos de una clase.
- El perfil es una polilinea cerrada y rellena (efecto "suelo"), con cuadricula,
  ejes, lineas verticales y textos verticales para salida, hitos y meta.

Uso:  python xml2altimetria.py [etapaEsquema.xml] [altimetria.svg]
"""

import math
import os
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape


class Svg:
    """Escribe un archivo SVG mediante plantillas de texto."""

    PROLOGO = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" version="1.1"\n'
        '     width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}"\n'
        '     font-family="Arial, Helvetica, sans-serif">\n'
        '  <title>{titulo}</title>\n'
    )
    EPILOGO = '</svg>\n'
    RECTANGULO = '  <rect x="{x}" y="{y}" width="{ancho}" height="{alto}" fill="{relleno}"/>\n'
    POLILINEA = ('  <polyline points="{puntos}" fill="{relleno}" stroke="{trazo}" '
                 'stroke-width="{grosor}" stroke-linejoin="round"/>\n')
    LINEA = ('  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
             'stroke-width="{grosor}"{discontinua}/>\n')
    CIRCULO = '  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{relleno}"/>\n'
    TEXTO = ('  <text x="{x}" y="{y}" font-size="{tam}" fill="{color}" '
             'text-anchor="{ancla}" font-weight="{peso}"{transformacion}>{contenido}</text>\n')

    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.texto = []

    def escribir_prologo(self, titulo):
        self.texto.append(self.PROLOGO.format(ancho=self.ancho, alto=self.alto,
                                              titulo=escape(titulo)))

    def escribir_rectangulo(self, x, y, ancho, alto, relleno):
        self.texto.append(self.RECTANGULO.format(x=x, y=y, ancho=ancho, alto=alto,
                                                 relleno=relleno))

    def escribir_polilinea(self, puntos, relleno, trazo, grosor):
        """puntos: lista de tuplas (x, y) en coordenadas SVG."""
        cadena = ' '.join('{:.1f},{:.1f}'.format(x, y) for x, y in puntos)
        self.texto.append(self.POLILINEA.format(puntos=cadena, relleno=relleno,
                                                trazo=trazo, grosor=grosor))

    def escribir_linea(self, x1, y1, x2, y2, color, grosor=1, discontinua=False):
        extra = ' stroke-dasharray="4 3"' if discontinua else ''
        self.texto.append(self.LINEA.format(x1=round(x1, 1), y1=round(y1, 1),
                                            x2=round(x2, 1), y2=round(y2, 1),
                                            color=color, grosor=grosor, discontinua=extra))

    def escribir_circulo(self, cx, cy, r, relleno):
        self.texto.append(self.CIRCULO.format(cx=round(cx, 1), cy=round(cy, 1), r=r,
                                              relleno=relleno))

    def escribir_texto(self, x, y, contenido, tam=12, color='#222', ancla='start',
                       negrita=False, rotacion=None):
        """Si rotacion no es None el texto se gira alrededor de (x, y): texto vertical."""
        if rotacion is None:
            transformacion, xx, yy = '', round(x, 1), round(y, 1)
        else:
            transformacion = ' transform="translate({:.1f},{:.1f}) rotate({})"'.format(x, y, rotacion)
            xx, yy = 0, 0
        self.texto.append(self.TEXTO.format(x=xx, y=yy, tam=tam, color=color, ancla=ancla,
                                            peso='bold' if negrita else 'normal',
                                            transformacion=transformacion,
                                            contenido=escape(str(contenido))))

    def escribir_epilogo(self):
        self.texto.append(self.EPILOGO)

    def guardar(self, ruta):
        with open(ruta, 'w', encoding='utf-8') as archivo:
            archivo.write(''.join(self.texto))


class Altimetria:
    """Lee etapaEsquema.xml (arbol DOM + XPath) y genera altimetria.svg."""

    NS = {'u': 'http://www.uniovi.es'}

    # Geometria del dibujo (unidades SVG)
    ANCHO, ALTO = 1200, 700
    X_IZQ, X_DER = 90, 1140           # margenes horizontales del perfil
    Y_BASE, ALTURA = 560, 260         # linea del suelo y altura maxima del perfil

    COLOR_RELLENO = '#b5281c'
    COLOR_TRAZO = '#e8412c'
    COLOR_HITO = {'salida': ('#29a8e0', 'S'), 'meta': ('#e30613', 'M'),
                  'puerto': ('#a24fb5', None), 'sprint': ('#8cc63f', 'SP')}

    def __init__(self, ruta_xml, ruta_svg):
        self.ruta_xml = ruta_xml
        self.ruta_svg = ruta_svg
        self.raiz = None

    # ---------------------------------------------------------------- lectura
    def cargar_xml(self):
        try:
            self.raiz = ET.parse(self.ruta_xml).getroot()
        except (OSError, ET.ParseError) as error:
            print('No se pudo leer {}: {}'.format(self.ruta_xml, error))
            sys.exit(1)

    def valor_xpath(self, nodo, expresion):
        elemento = nodo.find(expresion, self.NS)
        if elemento is None or elemento.text is None:
            raise ValueError('Falta el elemento ' + expresion)
        return elemento.text.strip()

    def extraer_datos(self):
        """Obtiene con XPath las distancias y altitudes de la etapa."""
        self.nombre = self.valor_xpath(self.raiz, './u:nombre')
        self.numero = self.raiz.get('numero')
        self.longitud = float(self.valor_xpath(self.raiz, './u:longitud'))
        self.desnivel = self.valor_xpath(self.raiz, './u:desnivel')

        # Hitos: (tipo, etiqueta, km, altitud, categoria)
        self.hitos = []
        for clave, expresion, km in (('salida', './u:lugarSalida', 0.0),
                                     ('meta', './u:lugarLlegada', self.longitud)):
            nodo = self.raiz.find(expresion, self.NS)
            self.hitos.append((clave, self.valor_xpath(nodo, './u:nombre'), km,
                               float(self.valor_xpath(nodo, './u:coordenadas/u:altitud')), None))
        for nodo in self.raiz.findall('./u:hitos/u:puertoMontana', self.NS):
            self.hitos.append(('puerto', self.valor_xpath(nodo, './u:nombre'),
                               float(self.valor_xpath(nodo, './u:distanciaSalida')),
                               float(self.valor_xpath(nodo, './u:coordenadas/u:altitud')),
                               nodo.get('categoria')))
        for nodo in self.raiz.findall('./u:hitos/u:sprint', self.NS):
            self.hitos.append(('sprint', self.valor_xpath(nodo, './u:nombre'),
                               float(self.valor_xpath(nodo, './u:distanciaSalida')),
                               float(self.valor_xpath(nodo, './u:coordenadas/u:altitud')),
                               None))
        self.hitos.sort(key=lambda h: h[2])

        # Perfil: todos los puntos (km, altitud) ordenados por distancia
        perfil = [(h[2], h[3]) for h in self.hitos]
        for nodo in self.raiz.findall('./u:puntosAnonimos/u:punto', self.NS):
            perfil.append((float(self.valor_xpath(nodo, './u:distanciaSalida')),
                           float(self.valor_xpath(nodo, './u:coordenadas/u:altitud'))))
        perfil.sort()
        self.perfil = perfil

        maximo = max(a for _, a in perfil)
        self.alt_max = max(100, math.ceil(maximo * 1.15 / 100) * 100)   # techo de la escala

    # ---------------------------------------------------------------- escalas
    def x_de(self, km):
        return self.X_IZQ + (self.X_DER - self.X_IZQ) * km / self.longitud

    def y_de(self, altitud):
        return self.Y_BASE - self.ALTURA * altitud / self.alt_max

    @staticmethod
    def formato_km(km):
        return '{:g}'.format(round(km, 1))

    # ------------------------------------------------------------- generacion
    def dibujar_cuadricula(self, svg):
        for alt in range(0, int(self.alt_max) + 1, 100):
            y = self.y_de(alt)
            svg.escribir_linea(self.X_IZQ, y, self.X_DER, y, '#d9d9d9', 1)
            svg.escribir_texto(self.X_IZQ - 8, y + 4, alt, 11, '#555', 'end')
        svg.escribir_texto(30, self.Y_BASE - self.ALTURA / 2, 'Altitud (m)', 12, '#555',
                           'middle', rotacion=-90)

    def dibujar_perfil(self, svg):
        puntos = [(self.x_de(km), self.y_de(alt)) for km, alt in self.perfil]
        cerrada = [(self.x_de(0), self.Y_BASE)] + puntos + [(self.x_de(self.longitud), self.Y_BASE)]
        svg.escribir_polilinea(cerrada, self.COLOR_RELLENO, self.COLOR_TRAZO, 2)

    def dibujar_hitos(self, svg):
        y_marca = 268                      # centro de los circulos indicadores
        y_texto = 250                      # inicio (abajo) del texto vertical
        for tipo, nombre, km, alt, categoria in self.hitos:
            x = self.x_de(km)
            color, letra = self.COLOR_HITO[tipo]
            if tipo == 'puerto':
                letra = categoria
            svg.escribir_linea(x, y_marca + 12, x, self.Y_BASE, '#333', 1, discontinua=True)
            svg.escribir_circulo(x, y_marca, 12, color)
            svg.escribir_texto(x, y_marca + 4, letra, 11, '#fff', 'middle', negrita=True)
            svg.escribir_texto(x + 5, y_texto, '{} / {:g} m'.format(nombre, alt), 12,
                               '#222', 'start', rotacion=-90)
            svg.escribir_texto(x, self.Y_BASE + 20, self.formato_km(km), 12, '#222',
                               'middle', negrita=True)

    def generar_svg(self):
        svg = Svg(self.ANCHO, self.ALTO)
        # --- Prologo
        svg.escribir_prologo('Altimetria etapa {}: {}'.format(self.numero, self.nombre))
        svg.escribir_rectangulo(0, 0, self.ANCHO, self.ALTO, '#ffffff')
        svg.escribir_texto(self.ANCHO / 2, 32,
                           'Etapa {}: {} - {:g} km'.format(self.numero, self.nombre, self.longitud),
                           20, '#1a1a1a', 'middle', negrita=True)
        # --- Cuerpo: cuadricula, perfil (distancia/altitud) y hitos
        self.dibujar_cuadricula(svg)
        self.dibujar_perfil(svg)
        self.dibujar_hitos(svg)
        svg.escribir_linea(self.X_IZQ, self.Y_BASE, self.X_DER, self.Y_BASE, '#333', 1.5)
        svg.escribir_texto(self.X_DER + 32, self.Y_BASE + 20, 'km', 12, '#555', 'start')
        svg.escribir_texto(self.ANCHO / 2, self.Y_BASE + 75,
                           'Desnivel acumulado: {} m'.format(self.desnivel),
                           16, '#1a1a1a', 'middle', negrita=True)
        # --- Epilogo
        svg.escribir_epilogo()
        svg.guardar(self.ruta_svg)

    def main(self):
        self.cargar_xml()
        self.extraer_datos()
        self.generar_svg()
        print('Archivo generado: {}'.format(self.ruta_svg))
        print('  {} puntos en el perfil, {} hitos, escala 0-{} m'.format(
            len(self.perfil), len(self.hitos), int(self.alt_max)))


if __name__ == '__main__':
    carpeta = os.path.dirname(os.path.abspath(__file__))
    entrada = sys.argv[1] if len(sys.argv) > 1 else os.path.join(carpeta, 'etapaEsquema.xml')
    salida = sys.argv[2] if len(sys.argv) > 2 else os.path.join(carpeta, 'altimetria.svg')
    Altimetria(entrada, salida).main()
