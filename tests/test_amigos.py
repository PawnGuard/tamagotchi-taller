# Pruebas de AMIGOS (apartados/amigos.py): un duelo completo contra otro
# bichito simulado. La "radio" es comun.RadioFalsa.
import unittest

import comun
import bicho
import duelo
import juego
import menu
import radio
from apartados import amigos


def esperar(ms):
    for _ in range(ms // 50):
        juego.paso(50)


class Duelo(unittest.TestCase):
    def setUp(self):
        self.rival = duelo.Duelo("BBBB", "bicho")
        self.aire = comun.RadioFalsa(radio, self.rival)
        juego.empezar()
        juego.bicho.etapa = bicho.BEBE
        juego.tecla("a")
        juego.elegido = menu.MENU.index(amigos)
        juego.tecla("b")

    def paso(self, ms=50):
        """Avanza a los dos bichitos a la vez."""
        for _ in range(ms // 50):
            self.rival.tick(50)
            juego.paso(50)

    def textos(self):
        fb = comun.Pantalla()
        juego.dibujar(fb)
        return fb.todo()

    def test_prende_la_radio_y_la_apaga_al_salir(self):
        self.assertTrue(self.aire.encendida)
        juego.tecla("c")
        self.assertFalse(self.aire.encendida)
        self.assertEqual(juego.pantalla, juego.MENU)

    def test_encuentra_al_amigo(self):
        self.assertIn("BUSCANDO", self.textos())
        self.paso(1500)
        self.assertIn("B: retar a BBBB", self.textos())

    def test_duelo_completo_y_premio(self):
        self.paso(1500)
        juego.tecla("b")                          # lo reto
        self.paso(500)
        self.assertEqual(self.rival.estado, duelo.INVITADO)
        self.rival.aceptar()
        self.paso(500)
        self.assertIn("<PIEDRA>", self.textos())
        juego.tecla("b")                          # elijo piedra
        self.rival.siguiente()                    # el rival elige papel
        self.rival.confirmar()
        felicidad = juego.bicho.felicidad
        self.paso(3000)
        self.assertEqual(amigos.partida.resultado, duelo.PERDI)
        self.assertIn("PERDISTE", self.textos())
        self.assertEqual(juego.bicho.derrotas, 1)
        self.assertGreater(juego.bicho.felicidad, felicidad)

    def test_si_me_retan_suena_y_puedo_rechazar(self):
        self.paso(1500)
        self.rival.retar("AAAA")
        self.paso(500)
        self.assertIn("BBBB TE RETA!", self.textos())
        juego.tecla("c")
        self.paso(500)
        self.assertEqual(self.rival.resultado, duelo.RECHAZO)


if __name__ == "__main__":
    unittest.main()
