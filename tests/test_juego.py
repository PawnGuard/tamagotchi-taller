# Pruebas de las pantallas, el menu y los apartados (incluidos los del taller).
import unittest

import comun
import config
import bicho
import dibujo
import juego
import menu
import sonido
from apartados import saludar, sin_nombre, comer, estado

config.ESCALA = 60       # 1 s real = 1 minuto de juego


def bebe():
    juego.empezar()
    juego.bicho.etapa = bicho.BEBE


def abrir(apartado):
    """Navega el menu hasta ese apartado y lo elige, como un jugador."""
    juego.tecla("a")                          # abre el menu
    while menu.MENU[juego.elegido] is not apartado:
        juego.tecla("a")
    juego.tecla("b")


def pantalla():
    fb = comun.Pantalla()
    juego.dibujar(fb)
    return fb


def esperar(ms):
    for _ in range(ms // 50):
        juego.paso(50)


class Menu(unittest.TestCase):
    def setUp(self):
        bebe()

    def test_a_abre_el_menu_y_c_lo_cierra(self):
        juego.tecla("a")
        self.assertEqual(juego.pantalla, juego.MENU)
        self.assertIn("<COMER>", pantalla().todo())
        juego.tecla("c")
        self.assertEqual(juego.pantalla, juego.CASA)

    def test_a_recorre_todo_el_menu_y_da_la_vuelta(self):
        juego.tecla("a")
        for _ in range(len(menu.MENU)):
            juego.tecla("a")
        self.assertEqual(juego.elegido, 0)

    def test_accion_rapida_muestra_su_texto_y_se_queda_en_el_menu(self):
        juego.bicho.hambre = 50
        abrir(comer)
        self.assertEqual(juego.bicho.hambre, 80)
        self.assertEqual(sonido.ultima, "comer")
        self.assertIn("NAM NAM", pantalla().todo())
        esperar(juego.AVISO_MS)
        self.assertIn("<COMER>", pantalla().todo())

    def test_las_barras_no_pasan_de_100(self):
        juego.bicho.hambre = 95
        abrir(comer)
        self.assertEqual(juego.bicho.hambre, 100)

    def test_dormido_solo_acepta_luz_y_estado(self):
        juego.bicho.luz = False
        abrir(comer)
        self.assertIn("ZZZ...", pantalla().todo())
        juego.tecla("c")                      # quita el aviso
        abrir(estado)
        self.assertEqual(juego.pantalla, juego.APARTADO)

    def test_en_el_huevo_no_se_puede_jugar(self):
        juego.empezar()
        abrir(comer)
        self.assertIn("AUN NO NACE", pantalla().todo())

    def test_muerto_b_pone_otro_huevo(self):
        juego.bicho.etapa = bicho.MUERTO
        self.assertIn("R.I.P.", pantalla().todo())
        juego.tecla("a")
        self.assertEqual(juego.pantalla, juego.CASA)
        juego.tecla("b")
        self.assertEqual(juego.bicho.etapa, bicho.HUEVO)

    def test_el_tiempo_corre_en_casa_y_se_detiene_en_un_apartado(self):
        edad = juego.bicho.edad
        esperar(1000)
        self.assertAlmostEqual(juego.bicho.edad, edad + 1)
        abrir(saludar)
        esperar(5000)
        self.assertAlmostEqual(juego.bicho.edad, edad + 1)


class Saludar(unittest.TestCase):
    """EJERCICIO 1: "Saludando" en pantalla hasta que presionas C."""

    def setUp(self):
        bebe()
        abrir(saludar)

    def test_dice_saludando(self):
        self.assertEqual(juego.pantalla, juego.APARTADO)
        self.assertIn("Saludando", pantalla().todo())

    def test_a_y_b_no_lo_quitan(self):
        for t in "abab":
            juego.tecla(t)
        esperar(3000)
        self.assertEqual(juego.pantalla, juego.APARTADO)
        textos = pantalla().todo()
        self.assertTrue(any(s in textos for s in saludar.SALUDOS), textos)

    def test_c_lo_quita(self):
        juego.tecla("c")
        self.assertEqual(juego.pantalla, juego.MENU)
        self.assertNotIn("Saludando", pantalla().todo())


class SinNombre(unittest.TestCase):
    """EJERCICIO 2: bichito sonriendo y tres puntos animados abajo."""

    def setUp(self):
        bebe()
        abrir(sin_nombre)

    def puntos(self):
        return len([r for r in pantalla().rellenos if r[2:] == (4, 4) and r[1] == 54])

    def test_el_nombre_esta_en_blanco(self):
        self.assertEqual(sin_nombre.NOMBRE, "")
        juego.tecla("c")
        self.assertIn("<>", pantalla().todo())

    def test_sale_el_bichito_sonriendo(self):
        import sprites
        sonriente = sprites.bichito("bebe", "feliz")
        self.assertIn(sonriente, pantalla().imagenes)

    def test_los_puntos_se_animan(self):
        vistos = []
        for _ in range(8):
            vistos.append(self.puntos())
            esperar(sin_nombre.PUNTOS_MS)
        self.assertEqual(vistos, [0, 1, 2, 3, 0, 1, 2, 3])

    def test_c_lo_quita(self):
        juego.tecla("c")
        self.assertEqual(juego.pantalla, juego.MENU)


class Contrato(unittest.TestCase):
    """Todos los apartados del menu cumplen las reglas de apartados/__init__.py.
    Si agregas uno y esta prueba falla, el mensaje dice cual."""

    def test_todos_se_abren_dibujan_y_se_cierran(self):
        comun.RadioFalsa(__import__("radio"))
        for ap in menu.MENU:
            with self.subTest(apartado=ap.__name__):
                self.assertIsInstance(ap.NOMBRE, str)
                self.assertLessEqual(len(ap.NOMBRE), 13)
                bebe()
                abrir(ap)
                esperar(500)
                pantalla()
                for _ in range(3):
                    if juego.pantalla == juego.APARTADO:
                        juego.tecla("c")
                self.assertNotEqual(juego.pantalla, juego.APARTADO,
                                    "C no saca de %s" % ap.__name__)


if __name__ == "__main__":
    unittest.main()
