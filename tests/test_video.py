# Pruebas del apartado VIDEO: lee el cuadro que toca desde el archivo.
import os
import struct
import tempfile
import unittest

import comun
import bicho
import juego
import menu
from apartados import video


def archivo_de_prueba(n=5, fps=10):
    """Un video falso: el cuadro i tiene encendida la columna i."""
    ruta = os.path.join(tempfile.mkdtemp(), "video_cuadros.bin")
    with open(ruta, "wb") as f:
        f.write(b"VID1" + struct.pack("<BHBB", fps, n, 128, 64))
        for i in range(n):
            c = bytearray(1024)
            c[i] = 0xFF                    # columna i, primeros 8 pixeles
            f.write(c)
    return ruta


class Video(unittest.TestCase):
    def setUp(self):
        self.antes = video.ARCHIVO
        juego.empezar()
        juego.bicho.etapa = bicho.BEBE

    def tearDown(self):
        video.ARCHIVO = self.antes

    def abrir(self):
        juego.tecla("a")
        juego.elegido = menu.MENU.index(video)
        juego.tecla("b")

    def columna_encendida(self):
        fb = comun.Pantalla()
        juego.dibujar(fb)
        return [x for x in range(10) if fb.pixel(x, 0)]

    def test_sin_archivo_avisa(self):
        video.ARCHIVO = "/no/existe.bin"
        self.abrir()
        self.assertEqual(juego.pantalla, juego.MENU)
        fb = comun.Pantalla()
        juego.dibujar(fb)
        self.assertIn("SIN VIDEO", fb.todo())

    def test_avanza_al_ritmo_de_sus_fps_y_da_la_vuelta(self):
        video.ARCHIVO = archivo_de_prueba(n=5, fps=10)
        self.abrir()
        vistos = []
        for _ in range(7):
            juego.paso(100)                  # 10 fps = un cuadro cada 100 ms
            vistos.append(self.columna_encendida())
        self.assertEqual(vistos, [[1], [2], [3], [4], [0], [1], [2]])

    def test_a_pausa_y_c_sale(self):
        video.ARCHIVO = archivo_de_prueba()
        self.abrir()
        juego.paso(100)
        juego.tecla("a")
        juego.paso(500)
        self.assertEqual(self.columna_encendida(), [1])
        juego.tecla("c")
        self.assertEqual(juego.pantalla, juego.MENU)
        self.assertTrue(video.archivo.closed if hasattr(video.archivo, "closed") else True)


class Musica(unittest.TestCase):
    def setUp(self):
        self.antes = video.ARCHIVO
        video.ARCHIVO = archivo_de_prueba()
        juego.empezar()
        juego.bicho.etapa = bicho.BEBE
        juego.tecla("a")
        juego.elegido = menu.MENU.index(video)
        juego.tecla("b")

    def tearDown(self):
        if juego.pantalla == juego.APARTADO:
            juego.tecla("c")                     # cierra el archivo del video
        video.ARCHIVO = self.antes

    def test_suena_al_abrir(self):
        import sonido
        self.assertEqual(sonido.ultima, "video")
        self.assertTrue(sonido.sonando())

    def test_la_pausa_calla_y_b_reinicia(self):
        import sonido
        juego.tecla("a")
        self.assertFalse(sonido.sonando())
        juego.tecla("b")
        self.assertTrue(sonido.sonando())

    def test_salir_calla(self):
        import sonido
        juego.tecla("c")
        self.assertFalse(sonido.sonando())

    def test_la_melodia_usa_notas_y_duraciones_validas(self):
        for nota, ms in video.MELODIA:
            self.assertTrue(nota == 0 or 100 <= nota <= 2000, nota)
            self.assertGreater(ms, 0)


if __name__ == "__main__":
    unittest.main()
