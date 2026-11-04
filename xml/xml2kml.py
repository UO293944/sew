# -*- coding: utf-8 -*-
"""
xml2kml.py
Genera el archivo etapa.kml (planimetria de la etapa) a partir de etapaEsquema.xml.

- El XML se lee con xml.etree.ElementTree y todos los datos se obtienen con
  expresiones XPath (findall / find con el espacio de nombres http://www.uniovi.es).
- Programa totalmente orientado a objetos: todas las funciones son metodos de una clase.
- El KML se escribe por "generacion de codigo basada en plantillas":
  prologo (cabecera), cuerpo (puntos y ruta) y epilogo (etiquetas de cierre).

Colores (enunciado): rojo = salida y meta, verde = puertos de montana,
azul = sprints intermedios, amarillo = puntos anonimos.

Uso:  python xml2kml.py [etapaEsquema.xml] [etapa.kml]
"""

import os
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape


class Kml:
    """Escribe un archivo KML mediante plantillas de texto."""

    PROLOGO = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
        '<Document>\n'
        '  <name>{nombre}</name>\n'
        '  <description>{descripcion}</description>\n'
    )
    EPILOGO = '</Document>\n</kml>\n'

    ESTILO_ICONO = (
        '  <Style id="{id}">\n'
        '    <IconStyle>\n'
        '      <scale>{escala}</scale>\n'
        '      <Icon><href>{url}</href></Icon>\n'
        '    </IconStyle>\n'
        '    <LabelStyle><scale>{escala_texto}</scale></LabelStyle>\n'
        '  </Style>\n'
    )
    ESTILO_LINEA = (
        '  <Style id="{id}">\n'
        '    <LineStyle>\n'
        '      <color>{color}</color>\n'
        '      <width>{ancho}</width>\n'
        '    </LineStyle>\n'
        '  </Style>\n'
    )
    PUNTO = (
        '    <Placemark>\n'
        '      <name>{nombre}</name>\n'
        '      <description>{descripcion}</description>\n'
        '      <styleUrl>#{estilo}</styleUrl>\n'
        '      <Point>\n'
        '        <altitudeMode>clampToGround</altitudeMode>\n'
        '        <coordinates>{lon},{lat},{alt}</coordinates>\n'
        '      </Point>\n'
        '    </Placemark>\n'
    )
    LINEA = (
        '    <Placemark>\n'
        '      <name>{nombre}</name>\n'
        '      <styleUrl>#{estilo}</styleUrl>\n'
        '      <LineString>\n'
        '        <tessellate>1</tessellate>\n'
        '        <altitudeMode>clampToGround</altitudeMode>\n'
        '        <coordinates>\n{coordenadas}\n        </coordinates>\n'
        '      </LineString>\n'
        '    </Placemark>\n'
    )

    def __init__(self):
        self.texto = []

    def escribir_prologo(self, nombre, descripcion):
        self.texto.append(self.PROLOGO.format(nombre=escape(nombre),
                                              descripcion=escape(descripcion)))

    def escribir_estilo_icono(self, identificador, url, escala=1.0, escala_texto=0.9):
        self.texto.append(self.ESTILO_ICONO.format(id=identificador, url=url,
                                                   escala=escala, escala_texto=escala_texto))

    def escribir_estilo_linea(self, identificador, color, ancho):
        self.texto.append(self.ESTILO_LINEA.format(id=identificador, color=color, ancho=ancho))

    def abrir_carpeta(self, nombre):
        self.texto.append('  <Folder>\n    <name>{}</name>\n'.format(escape(nombre)))

    def cerrar_carpeta(self):
        self.texto.append('  </Folder>\n')

    def escribir_punto(self, nombre, descripcion, estilo, lon, lat, alt):
        self.texto.append(self.PUNTO.format(nombre=escape(nombre),
                                            descripcion=escape(descripcion),
                                            estilo=estilo, lon=lon, lat=lat, alt=alt))

    def escribir_linea(self, nombre, estilo, coordenadas):
        """coordenadas: lista de tuplas (lon, lat, alt)."""
        cuerpo = '\n'.join('          {},{},{}'.format(lon, lat, alt)
                           for lon, lat, alt in coordenadas)
        self.texto.append(self.LINEA.format(nombre=escape(nombre), estilo=estilo,
                                            coordenadas=cuerpo))

    def escribir_epilogo(self):
        self.texto.append(self.EPILOGO)

    def guardar(self, ruta):
        with open(ruta, 'w', encoding='utf-8') as archivo:
            archivo.write(''.join(self.texto))


class Xml2Kml:
    """Lee etapaEsquema.xml (arbol DOM + XPath) y genera etapa.kml."""

    NS = {'u': 'http://www.uniovi.es'}          # espacio de nombres del esquema
    ICONOS = 'http://maps.google.com/mapfiles/kml/paddle/'

    def __init__(self, ruta_xml, ruta_kml):
        self.ruta_xml = ruta_xml
        self.ruta_kml = ruta_kml
        self.raiz = None

    # ---------------------------------------------------------------- lectura
    def cargar_xml(self):
        """Construye en memoria el arbol DOM del archivo XML."""
        try:
            self.raiz = ET.parse(self.ruta_xml).getroot()
        except (OSError, ET.ParseError) as error:
            print('No se pudo leer {}: {}'.format(self.ruta_xml, error))
            sys.exit(1)

    def texto_xpath(self, nodo, expresion):
        """Devuelve el texto del primer nodo que cumple la expresion XPath."""
        elemento = nodo.find(expresion, self.NS)
        if elemento is None or elemento.text is None:
            raise ValueError('Falta el elemento ' + expresion)
        return elemento.text.strip()

    def extraer_coordenadas(self, nodo):
        """(longitud, latitud, altitud) de un nodo que contiene <coordenadas>."""
        lon = self.texto_xpath(nodo, './u:coordenadas/u:longitudGeo')
        lat = self.texto_xpath(nodo, './u:coordenadas/u:latitudGeo')
        alt = self.texto_xpath(nodo, './u:coordenadas/u:altitud')
        return lon, lat, alt

    def extraer_salida_y_meta(self):
        """Salida y meta: km 0 y km longitud."""
        longitud = self.texto_xpath(self.raiz, './u:longitud')
        resultado = []
        for expresion, km in (('./u:lugarSalida', '0'), ('./u:lugarLlegada', longitud)):
            nodo = self.raiz.find(expresion, self.NS)
            lon, lat, alt = self.extraer_coordenadas(nodo)
            resultado.append({'nombre': self.texto_xpath(nodo, './u:nombre'),
                              'km': km, 'lon': lon, 'lat': lat, 'alt': alt})
        return resultado

    def extraer_hitos(self, expresion):
        """Puertos (./u:hitos/u:puertoMontana) o sprints (./u:hitos/u:sprint)."""
        hitos = []
        for nodo in self.raiz.findall(expresion, self.NS):
            lon, lat, alt = self.extraer_coordenadas(nodo)
            hitos.append({'nombre': self.texto_xpath(nodo, './u:nombre'),
                          'km': self.texto_xpath(nodo, './u:distanciaSalida'),
                          'lon': lon, 'lat': lat, 'alt': alt,
                          'categoria': nodo.get('categoria'), 'tipo': nodo.get('tipo')})
        return hitos

    def extraer_puntos_anonimos(self):
        puntos = []
        for nodo in self.raiz.findall('./u:puntosAnonimos/u:punto', self.NS):
            lon, lat, alt = self.extraer_coordenadas(nodo)
            puntos.append({'km': self.texto_xpath(nodo, './u:distanciaSalida'),
                           'lon': lon, 'lat': lat, 'alt': alt})
        return puntos

    # ------------------------------------------------------------- generacion
    def construir_ruta(self, salida_meta, puertos, sprints, puntos):
        """Todos los puntos de la etapa ordenados por distancia desde la salida."""
        todos = [salida_meta[0]] + puntos + puertos + sprints + [salida_meta[1]]
        todos.sort(key=lambda p: float(p['km']))
        return [(p['lon'], p['lat'], p['alt']) for p in todos]

    def generar_kml(self):
        nombre_etapa = self.texto_xpath(self.raiz, './u:nombre')
        numero = self.raiz.get('numero')
        salida_meta = self.extraer_salida_y_meta()
        puertos = self.extraer_hitos('./u:hitos/u:puertoMontana')
        sprints = self.extraer_hitos('./u:hitos/u:sprint')
        puntos = self.extraer_puntos_anonimos()

        kml = Kml()
        # --- Prologo
        kml.escribir_prologo('Etapa {}: {}'.format(numero, nombre_etapa),
                             'Planimetria de la etapa {} de La Vuelta 2026 ({} km)'.format(
                                 numero, self.texto_xpath(self.raiz, './u:longitud')))
        kml.escribir_estilo_icono('salidaMeta', self.ICONOS + 'red-circle.png', 1.2)
        kml.escribir_estilo_icono('puerto', self.ICONOS + 'grn-circle.png', 1.1)
        kml.escribir_estilo_icono('sprint', self.ICONOS + 'blu-circle.png', 1.1)
        kml.escribir_estilo_icono('anonimo', self.ICONOS + 'ylw-circle.png', 0.6, 0)
        kml.escribir_estilo_linea('ruta', 'ff00a5ff', 4)       # naranja (aabbggrr)

        # --- Cuerpo: coordenadas de la etapa
        kml.abrir_carpeta('Salida y meta')
        for etiqueta, punto in zip(('Salida', 'Meta'), salida_meta):
            kml.escribir_punto('{}: {}'.format(etiqueta, punto['nombre']),
                               'Km {} - altitud {} m'.format(punto['km'], punto['alt']),
                               'salidaMeta', punto['lon'], punto['lat'], punto['alt'])
        kml.cerrar_carpeta()

        kml.abrir_carpeta('Puertos de montana')
        for p in puertos:
            kml.escribir_punto(p['nombre'],
                               'Categoria {} - km {} - altitud {} m'.format(
                                   p['categoria'], p['km'], p['alt']),
                               'puerto', p['lon'], p['lat'], p['alt'])
        kml.cerrar_carpeta()

        kml.abrir_carpeta('Sprints intermedios')
        for s in sprints:
            kml.escribir_punto(s['nombre'],
                               'Sprint {} - km {} - altitud {} m'.format(
                                   s['tipo'], s['km'], s['alt']),
                               'sprint', s['lon'], s['lat'], s['alt'])
        kml.cerrar_carpeta()

        kml.abrir_carpeta('Puntos anonimos')
        for i, p in enumerate(puntos, start=1):
            kml.escribir_punto('Punto {}'.format(i),
                               'Km {} - altitud {} m'.format(p['km'], p['alt']),
                               'anonimo', p['lon'], p['lat'], p['alt'])
        kml.cerrar_carpeta()

        kml.abrir_carpeta('Trazado')
        kml.escribir_linea('Recorrido de la etapa', 'ruta',
                           self.construir_ruta(salida_meta, puertos, sprints, puntos))
        kml.cerrar_carpeta()

        # --- Epilogo
        kml.escribir_epilogo()
        kml.guardar(self.ruta_kml)
        return len(puntos), len(puertos), len(sprints)

    def main(self):
        self.cargar_xml()
        n_puntos, n_puertos, n_sprints = self.generar_kml()
        print('Archivo generado: {}'.format(self.ruta_kml))
        print('  1 salida, 1 meta, {} puerto(s), {} sprint(s), {} puntos anonimos'.format(
            n_puertos, n_sprints, n_puntos))


if __name__ == '__main__':
    carpeta = os.path.dirname(os.path.abspath(__file__))
    entrada = sys.argv[1] if len(sys.argv) > 1 else os.path.join(carpeta, 'etapaEsquema.xml')
    salida = sys.argv[2] if len(sys.argv) > 2 else os.path.join(carpeta, 'etapa.kml')
    Xml2Kml(entrada, salida).main()
