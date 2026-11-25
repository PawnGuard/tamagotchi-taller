# Pruebas del protocolo de piedra-papel-tijera con dos bichitos simulados.
# La "radio" es una lista: lo que uno deja en `salida` le llega al otro.
#   python3 -m unittest discover -s tests -v
import os
import random
import sys
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "src"))

import duelo
from duelo import Duelo


class Radio:
    """Conecta bichitos entre si. perdida = probabilidad de que un paquete
    no llegue (ESP-NOW por difusion no reintenta)."""

    def __init__(self, *bichos, perdida=0.0, semilla=1):
        self.bichos = bichos
        self.perdida = perdida
        self.rng = random.Random(semilla)
        self.espia = []                  # todo lo que paso por el aire

    def paso(self, ms=50):
        for b in self.bichos:
            b.tick(ms)
        for b in self.bichos:
            enviados, b.salida = b.salida, []
            for m in enviados:
                self.espia.append(m)
                for otro in self.bichos:
                    if otro is not b and self.rng.random() >= self.perdida:
                        otro.recibir(m)

    def correr(self, ms, hasta=None):
        for _ in range(ms // 50):
            self.paso()
            if hasta and hasta():
                return True
        return False


def contador(inicio=0):
    n = [inicio]

    def azar():
        n[0] += 1
        return "%08x" % (n[0] * 2654435761 % 2**32)
    return azar


def pareja(perdida=0.0, semilla=1):
    a = Duelo("AAAA", "angel", azar=contador())
    b = Duelo("BBBB", "diablo", azar=contador(1000))
    return a, b, Radio(a, b, perdida=perdida, semilla=semilla)


def jugar(a, b, radio, mano_a, mano_b):
    radio.correr(8000, lambda: "BBBB" in a.amigos)
    a.retar("BBBB")
    radio.correr(4000, lambda: b.estado == duelo.INVITADO)
    b.aceptar()
    radio.correr(4000, lambda: a.estado == duelo.ELIGIENDO)
    a.seleccion = duelo.JUGADAS.index(mano_a)
    b.seleccion = duelo.JUGADAS.index(mano_b)
    a.confirmar()
    b.confirmar()
    radio.correr(5000, lambda: a.estado == b.estado == duelo.FIN)


class Descubrimiento(unittest.TestCase):
    def test_se_ven_con_su_forma(self):
        a, b, radio = pareja()
        radio.correr(1500)
        self.assertEqual(a.amigos["BBBB"][0], "diablo")
        self.assertEqual(b.amigos["AAAA"][0], "angel")
        self.assertEqual(a.lista(), ["BBBB"])

    def test_un_amigo_que_se_va_se_olvida(self):
        a, b, radio = pareja()
        radio.correr(1500)
        solo = Radio(a)
        solo.correr(duelo.OLVIDO_MS + 1500)
        self.assertEqual(a.amigos, {})

    def test_no_se_puede_retar_a_un_desconocido(self):
        a, b, radio = pareja()
        a.retar("ZZZZ")
        self.assertEqual(a.estado, duelo.LIBRE)


class Partida(unittest.TestCase):
    def test_todas_las_combinaciones(self):
        for ma in duelo.JUGADAS:
            for mb in duelo.JUGADAS:
                a, b, radio = pareja()
                jugar(a, b, radio, ma, mb)
                self.assertEqual(a.estado, duelo.FIN, (ma, mb))
                self.assertEqual(b.estado, duelo.FIN, (ma, mb))
                self.assertEqual(a.resultado, duelo.quien_gana(ma, mb), (ma, mb))
                self.assertEqual(b.resultado, duelo.quien_gana(mb, ma), (ma, mb))
                self.assertEqual((a.suya, b.suya), (mb, ma))

    def test_piedra_le_gana_a_tijera(self):
        self.assertEqual(duelo.quien_gana("piedra", "tijera"), duelo.GANE)
        self.assertEqual(duelo.quien_gana("tijera", "piedra"), duelo.PERDI)
        self.assertEqual(duelo.quien_gana("papel", "papel"), duelo.EMPATE)

    def test_rechazar(self):
        a, b, radio = pareja()
        radio.correr(1500)
        a.retar("BBBB")
        radio.correr(1000, lambda: b.estado == duelo.INVITADO)
        b.rechazar()
        radio.correr(1000, lambda: a.estado == duelo.FIN)
        self.assertEqual(a.resultado, duelo.RECHAZO)
        self.assertEqual(b.estado, duelo.LIBRE)

    def test_si_no_eliges_a_tiempo_va_la_seleccion(self):
        a, b, radio = pareja()
        radio.correr(1500)
        a.retar("BBBB")
        radio.correr(1000, lambda: b.estado == duelo.INVITADO)
        b.aceptar()
        radio.correr(1000, lambda: a.estado == duelo.ELIGIENDO)
        a.confirmar()
        radio.correr(duelo.ELEGIR_MS + 3000, lambda: b.estado == duelo.FIN)
        self.assertEqual(b.mia, duelo.JUGADAS[0])
        self.assertEqual(b.estado, duelo.FIN)

    def test_abandonar_avisa_al_otro(self):
        a, b, radio = pareja()
        radio.correr(1500)
        a.retar("BBBB")
        radio.correr(1000, lambda: b.estado == duelo.INVITADO)
        b.aceptar()
        radio.correr(500)
        b.abandonar()
        radio.correr(1000, lambda: a.estado == duelo.FIN)
        self.assertEqual(a.resultado, duelo.CANCELADO)

    def test_si_el_otro_desaparece_se_cancela(self):
        a, b, radio = pareja()
        radio.correr(1500)
        a.retar("BBBB")
        Radio(a).correr(duelo.PACIENCIA_MS + 500)
        self.assertEqual(a.resultado, duelo.CANCELADO)

    def test_retarse_al_mismo_tiempo(self):
        a, b, radio = pareja()
        radio.correr(1500)
        a.retar("BBBB")
        b.retar("AAAA")
        radio.correr(1000)
        self.assertEqual(a.estado, duelo.ELIGIENDO)
        self.assertEqual(b.estado, duelo.ELIGIENDO)
        self.assertEqual(a.sid, b.sid)

    def test_un_tercero_ocupado_dice_que_no(self):
        a, b, radio = pareja()
        c = Duelo("CCCC", "bicho", azar=contador(2000))
        radio = Radio(a, b, c)
        radio.correr(1500)
        a.retar("BBBB")
        radio.correr(1000, lambda: b.estado == duelo.INVITADO)
        c.retar("BBBB")
        radio.correr(1000, lambda: c.estado == duelo.FIN)
        self.assertEqual(c.resultado, duelo.RECHAZO)
        self.assertEqual(b.rival, "AAAA")


class RadioMala(unittest.TestCase):
    """ESP-NOW por difusion no confirma la entrega: hay que repetir."""

    def test_termina_aunque_se_pierda_un_tercio_de_los_paquetes(self):
        for semilla in range(30):
            a, b, radio = pareja(perdida=0.33, semilla=semilla)
            jugar(a, b, radio, "papel", "piedra")
            self.assertEqual(a.resultado, duelo.GANE, "semilla %d" % semilla)
            self.assertEqual(b.resultado, duelo.PERDI, "semilla %d" % semilla)

    def test_el_que_cierra_primero_le_sigue_contestando_al_otro(self):
        a, b, radio = pareja()
        jugar(a, b, radio, "tijera", "papel")
        # A termina y cierra; B "no recibio" la ultima revelacion
        a.cerrar()
        b.estado, b.resultado, b.suya = duelo.ESPERANDO, None, None
        radio.correr(2000, lambda: b.estado == duelo.FIN)
        self.assertEqual(b.resultado, duelo.PERDI)


class Seguridad(unittest.TestCase):
    def test_la_huella_no_revela_la_jugada(self):
        # Con sal distinta, la misma jugada da huellas distintas: no sirve
        # precalcular las 3 posibles.
        self.assertNotEqual(duelo.huella("piedra", "0001"), duelo.huella("piedra", "0002"))
        self.assertEqual(len(duelo.huella("piedra", "0001")), 16)

    def test_nadie_revela_antes_de_tener_la_huella_del_otro(self):
        a, b, radio = pareja()
        radio.correr(1500)
        a.retar("BBBB")
        radio.correr(1000, lambda: b.estado == duelo.INVITADO)
        b.aceptar()
        radio.correr(500)
        a.confirmar()                     # A elige; B todavia no
        radio.correr(3000)
        revelaciones = [m for m in radio.espia if b"|REVELO|" in m]
        self.assertEqual(revelaciones, [], "A revelo su mano sin la huella de B")

    def test_detecta_al_tramposo_que_cambia_su_jugada(self):
        a, b, radio = pareja()
        radio.correr(1500)
        a.retar("BBBB")
        radio.correr(1000, lambda: b.estado == duelo.INVITADO)
        b.aceptar()
        radio.correr(500)
        b.seleccion = 0                   # B se compromete con piedra...
        b.confirmar()
        a.seleccion = 1                   # A juega papel
        a.confirmar()
        # B le pasa su huella a A, pero se guarda su revelacion verdadera
        for m in b.salida:
            if b"|HUELLA|" in m:
                a.recibir(m)
        b.salida = []
        self.assertTrue(a._revele, "A ya deberia haber revelado su papel")
        # ...y en el aire B dice "tijera" para ganarle al papel de A
        falsa = ("T1|BBBB|AAAA|REVELO|%s|tijera|%s" % (b.sid, b.sal)).encode()
        a.recibir(falsa)
        self.assertEqual(a.resultado, duelo.TRAMPA)

    def test_detecta_al_que_cambia_su_huella(self):
        a, b, radio = pareja()
        radio.correr(1500)
        a.retar("BBBB")
        radio.correr(1000, lambda: b.estado == duelo.INVITADO)
        b.aceptar()
        radio.correr(500)
        b.confirmar()
        radio.paso()
        a.recibir(("T1|BBBB|AAAA|HUELLA|%s|0000000000000000" % b.sid).encode())
        self.assertEqual(a.resultado, duelo.TRAMPA)

    def test_si_ve_mi_mano_y_no_revela_la_suya_huyo(self):
        a, b, radio = pareja()
        radio.correr(1500)
        a.retar("BBBB")
        radio.correr(1000, lambda: b.estado == duelo.INVITADO)
        b.aceptar()
        radio.correr(500)
        a.confirmar(); b.confirmar()
        # B le da su huella a A, A revela su mano... y B se desconecta
        for m in b.salida:
            if b"|HUELLA|" in m:
                a.recibir(m)
        b.salida = []
        self.assertTrue(a._revele)
        Radio(a).correr(duelo.PACIENCIA_MS + 500)
        self.assertEqual(a.resultado, duelo.HUYO)

    def test_mensajes_basura_no_rompen_nada(self):
        a, b, radio = pareja()
        for basura in (b"", b"hola", b"T1", b"T1|x", b"T1|BBBB|AAAA|REVELO",
                       b"T1|BBBB|AAAA|HUELLA|zz", b"\xff\xfe\x00", b"T2|B|*|HOLA|x",
                       b"T1|BBBB|*|HOLA", b"T1|AAAA|*|HOLA|yo-mismo"):
            a.recibir(basura)
        self.assertEqual(a.estado, duelo.LIBRE)
        self.assertNotIn("AAAA", a.amigos)


if __name__ == "__main__":
    unittest.main()
