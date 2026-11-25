# Pruebas del INTRO: "Hola!" grande -> fantasmita guinando -> video -> menu.
import unittest

import comun
import bicho
import dibujo
import juego
import menu
import sonido
import sprites
from apartados import intro
from test_video import archivo_de_prueba


def esperar(ms):
    for _ in range(ms // 50):
        juego.paso(50)


def pantalla():
    fb = comun.Pantalla()
    juego.dibujar(fb)
    return fb


class Intro(unittest.TestCase):
    def setUp(self):
        self.antes = intro.ARCHIVO
        intro.ARCHIVO = archivo_de_prueba(n=6, fps=10)      # 600 ms de video
        juego.empezar()
        juego.bicho.etapa = bicho.BEBE
        juego.abrir(intro)

    def tearDown(self):
        intro.ARCHIVO = self.antes

    def test_esta_en_el_menu(self):
        self.assertIn(intro, menu.MENU)

    def test_empieza_con_hola_grande_y_sonido(self):
        self.assertEqual(intro.parte, intro.HOLA)
        self.assertEqual(sonido.ultima, "hola")
        esperar(400)
        self.assertIn(dibujo.letrero("Hola!", 3), pantalla().imagenes)

    def test_el_letrero_es_el_texto_agrandado(self):
        grande = dibujo.letrero("Hi", 3)
        self.assertEqual((grande.ancho, grande.alto), (48, 24))
        self.assertTrue(any(grande.pixel(x, y) for x in range(48) for y in range(24)))

    def test_luego_el_fantasmita_grande_guina_con_barras_y_edad(self):
        esperar(intro.HOLA_MS)
        self.assertEqual(intro.parte, intro.GUINO)
        fb = pantalla()
        self.assertIn(sprites.bichito("bebe", "feliz", intro.GRANDE), fb.imagenes)
        for letra in ("H", "F", "E"):
            self.assertIn(letra, fb.textos)
        self.assertIn(dibujo.edad(juego.bicho), fb.textos)
        esperar(intro.GUINA_DESDE)
        self.assertIn(sprites.bichito("bebe", "guino", intro.GRANDE), pantalla().imagenes)
        self.assertEqual(sonido.ultima, "guino")
        esperar(intro.GUINA_HASTA - intro.GUINA_DESDE)
        self.assertIn(sprites.bichito("bebe", "feliz", intro.GRANDE), pantalla().imagenes)

    def test_luego_el_video_y_al_terminar_vuelve_al_menu(self):
        esperar(intro.HOLA_MS + intro.GUINO_MS)
        self.assertEqual(intro.parte, intro.VIDEO)
        vistos = []
        for _ in range(5):
            juego.paso(100)
            fb = pantalla()
            vistos.append([x for x in range(10) if fb.pixel(x, 0)])
        self.assertEqual(vistos, [[1], [2], [3], [4], [5]])
        esperar(200)
        self.assertEqual(juego.pantalla, juego.MENU)

    def test_sin_video_termina_despues_del_guino(self):
        intro.ARCHIVO = "/no/existe.bin"
        esperar(intro.HOLA_MS + intro.GUINO_MS)
        self.assertEqual(juego.pantalla, juego.MENU)

    def test_a_salta_b_reinicia_c_sale(self):
        juego.tecla("a")
        self.assertEqual(intro.parte, intro.GUINO)
        juego.tecla("a")
        self.assertEqual(intro.parte, intro.VIDEO)
        juego.tecla("b")
        self.assertEqual(intro.parte, intro.HOLA)
        juego.tecla("c")
        self.assertEqual(juego.pantalla, juego.MENU)
        self.assertIsNone(intro.archivo)

    def test_el_fantasmita_cabe_entre_las_barras_y_la_edad(self):
        for forma in sprites.CUERPOS:
            filas = sprites.CUERPOS[forma].strip("\n").split("\n")
            llenas = [i for i, f in enumerate(filas) if "#" in f]
            x, y = intro.posicion(forma)
            arriba = y + llenas[0] * intro.GRANDE
            abajo = y + (llenas[-1] + 1) * intro.GRANDE + 1        # +1: cuando flota
            with self.subTest(forma=forma):
                self.assertGreaterEqual(arriba, 8)
                self.assertLessEqual(abajo, 54)
                self.assertGreaterEqual(x, 0)

    def test_sale_aunque_sea_huevo(self):
        juego.empezar()                       # huevo
        juego.abrir(intro)
        self.assertEqual(juego.pantalla, juego.APARTADO)
        esperar(intro.HOLA_MS)
        self.assertIn(sprites.bichito("bebe", "feliz", intro.GRANDE), pantalla().imagenes)


if __name__ == "__main__":
    unittest.main()
