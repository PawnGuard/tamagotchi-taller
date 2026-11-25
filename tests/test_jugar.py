# Pruebas del Pong (apartados/jugar.py).
import unittest

import comun
import botones
import bicho
import juego
import menu
from apartados import jugar
from apartados.jugar import Pong


def correr(p, ms, arriba=False, abajo=False):
    for _ in range(ms // 50):
        p.paso(50, arriba, abajo)


class Fisica(unittest.TestCase):
    def test_la_paleta_se_mueve_y_no_se_sale(self):
        p = Pong()
        y0 = p.y_yo
        correr(p, 200, arriba=True)
        self.assertLess(p.y_yo, y0)
        correr(p, 5000, abajo=True)
        self.assertEqual(p.y_yo, jugar.ALTO - jugar.PALETA)

    def test_la_bola_espera_antes_del_saque(self):
        p = Pong()
        x0 = p.bx
        correr(p, jugar.ESPERA_SAQUE - 100)
        self.assertEqual(p.bx, x0)
        correr(p, 300)
        self.assertNotEqual(p.bx, x0)

    def test_rebota_en_el_techo(self):
        p = Pong()
        p.espera, p.by, p.vx, p.vy = 0, jugar.ARRIBA + 1, 0, -100
        p.paso(50, False, False)
        self.assertGreater(p.vy, 0)

    def test_mi_paleta_la_devuelve_mas_rapido_y_la_orilla_la_inclina(self):
        p = Pong()
        p.espera, p.y_yo = 0, 30
        p.bx, p.by, p.vx, p.vy = jugar.X_YO + 3, 30, -60, 0
        v0 = p.vel
        p.paso(50, False, False)
        self.assertGreater(p.vx, 0)
        self.assertGreater(p.vel, v0)
        self.assertLess(p.vy, 0)

    def test_sin_jugar_gana_la_cpu(self):
        p = Pong(nivel=100)
        correr(p, 5 * 60 * 1000)
        self.assertTrue(p.terminado)
        self.assertEqual(p.cpu, jugar.PUNTOS_PARA_GANAR)


class EnElMenu(unittest.TestCase):
    def setUp(self):
        juego.empezar()
        juego.bicho.etapa = bicho.BEBE
        botones.apretados.clear()
        juego.tecla("a")
        juego.elegido = menu.MENU.index(jugar)
        juego.tecla("b")

    def tearDown(self):
        botones.apretados.clear()

    def test_abre_el_pong(self):
        self.assertEqual(juego.pantalla, juego.APARTADO)
        self.assertIs(juego.activo, jugar)

    def test_mantener_a_sube_mi_paleta(self):
        y0 = jugar.partida.y_yo
        botones.apretados.add("a")
        juego.paso(200)
        self.assertLess(jugar.partida.y_yo, y0)

    def test_mantener_b_5_segundos_regresa_al_menu(self):
        botones.apretados.add("b")
        for _ in range(jugar.SALIR_MS // 50 - 1):
            juego.paso(50)
        self.assertEqual(juego.pantalla, juego.APARTADO)
        juego.paso(50)
        self.assertEqual(juego.pantalla, juego.MENU)

    def test_soltar_b_reinicia_la_cuenta(self):
        botones.apretados.add("b")
        for _ in range(60):
            juego.paso(50)
        botones.apretados.discard("b")
        juego.paso(50)
        botones.apretados.add("b")
        for _ in range(60):
            juego.paso(50)
        self.assertEqual(juego.pantalla, juego.APARTADO)

    def test_ganar_alegra_cansa_y_avisa(self):
        juego.bicho.felicidad = 40.0
        energia = juego.bicho.energia
        for _ in range(jugar.PUNTOS_PARA_GANAR):
            jugar.partida.anotar(cpu=False)
        juego.paso(50)
        self.assertEqual(juego.pantalla, juego.MENU)
        self.assertGreater(juego.bicho.felicidad, 70)
        self.assertLess(juego.bicho.energia, energia)
        fb = comun.Pantalla()
        juego.dibujar(fb)
        self.assertIn("GANASTE 5-0", fb.todo())

    def test_cansado_no_juega(self):
        juego.tecla("c")
        juego.bicho.energia = 5.0
        juego.tecla("b")
        self.assertEqual(juego.pantalla, juego.MENU)
        fb = comun.Pantalla()
        juego.dibujar(fb)
        self.assertIn("CANSADO...", fb.todo())


if __name__ == "__main__":
    unittest.main()
