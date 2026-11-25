# Pruebas del modelo: necesidades, etapas y crianza.
import unittest

import comun
import bicho
from bicho import Bicho, HUEVO, BEBE, ADULTO, MUERTO


def vivir(b, minutos):
    """Avanza de minuto en minuto (como el bucle) y junta los avisos."""
    avisos = []
    for _ in range(int(minutos)):
        a = b.vivir(1)
        if a:
            avisos.append(a)
    return avisos


def bebe():
    b = Bicho()
    vivir(b, bicho.NACE)
    return b


class Etapas(unittest.TestCase):
    def test_nace_del_huevo(self):
        b = Bicho()
        self.assertEqual(b.etapa, HUEVO)
        self.assertEqual(vivir(b, bicho.NACE - 1), [])
        self.assertEqual(vivir(b, 1), ["NACIO!"])
        self.assertEqual(b.etapa, BEBE)

    def test_en_el_huevo_no_le_da_hambre(self):
        b = Bicho()
        vivir(b, 10)
        self.assertEqual(b.hambre, 80.0)

    def test_si_lo_abandonas_se_muere(self):
        b = bebe()
        avisos = vivir(b, 12 * 60)
        self.assertEqual(b.etapa, MUERTO)
        self.assertIn("R.I.P.", avisos)

    def test_muerto_ya_no_cambia(self):
        b = bebe()
        b.etapa = MUERTO
        self.assertIsNone(b.vivir(100))
        self.assertEqual(b.edad, bicho.NACE)

    def test_bien_cuidado_crece_a_adulto(self):
        b = bebe()
        avisos = []
        for _ in range(bicho.CRECE // 30 + 1):
            b.hambre = b.felicidad = b.energia = 100.0
            b.caca = 0
            avisos += vivir(b, 30)
        self.assertEqual(b.etapa, ADULTO)
        self.assertEqual(avisos[-1], "ES ANGEL!")


class Necesidades(unittest.TestCase):
    def test_las_barras_bajan(self):
        b = bebe()
        vivir(b, 60)
        self.assertLess(b.hambre, 80)
        self.assertLess(b.felicidad, 80)
        self.assertLess(b.energia, 80)

    def test_dormido_gasta_la_mitad_y_recupera_energia(self):
        despierto, dormido = bebe(), bebe()
        dormido.luz = False
        vivir(despierto, 60)
        vivir(dormido, 60)
        self.assertGreater(dormido.hambre, despierto.hambre)
        self.assertGreater(dormido.energia, 80)

    def test_hace_caca_y_mucha_caca_enferma(self):
        b = bebe()
        vivir(b, bicho.CACA_CADA)
        self.assertEqual(b.caca, 1)
        b.caca = 3
        vivir(b, bicho.SUCIO_ENFERMA)
        self.assertTrue(b.enfermo)

    def test_limitar_corrige_lo_que_se_paso(self):
        b = bebe()
        b.felicidad, b.hambre, b.caca = 500, -3, 9
        b.limitar()
        self.assertEqual((b.felicidad, b.hambre, b.caca), (100.0, 0.0, 3))

    def test_animo(self):
        b = bebe()
        b.felicidad = b.hambre = 90
        self.assertEqual(b.animo(), "feliz")
        b.hambre = 10
        self.assertEqual(b.animo(), "triste")
        b.luz = False
        self.assertEqual(b.animo(), "dormido")


class Crianza(unittest.TestCase):
    def test_ignorarlo_cuenta_un_error_una_sola_vez(self):
        b = bebe()
        b.hambre = 10
        vivir(b, bicho.LLAMADA + 5)
        self.assertEqual(b.errores, 1)

    def test_formas_adultas(self):
        b = bebe()
        casos = ((0, 0, "angel"), (3, 0, "bicho"), (9, 0, "diablo"),
                 (2, bicho.VICTORIAS_HACKER, "hacker"), (9, 20, "diablo"))
        for errores, victorias, forma in casos:
            b.errores, b.victorias = errores, victorias
            self.assertEqual(b.forma_adulta(), forma, (errores, victorias))


class Guardar(unittest.TestCase):
    def test_ida_y_vuelta(self):
        b = bebe()
        b.hambre, b.victorias = 42.0, 3
        otro = Bicho(b.para_guardar())
        self.assertEqual(otro.para_guardar(), b.para_guardar())

    def test_un_guardado_viejo_hereda_los_campos_nuevos(self):
        b = Bicho({"etapa": BEBE, "hambre": 10.0})
        self.assertEqual(b.hambre, 10.0)
        self.assertEqual(b.victorias, 0)

    def test_memoria_en_un_archivo(self):
        import os
        import tempfile
        import config
        import memoria
        antes = config.ARCHIVO
        config.ARCHIVO = os.path.join(tempfile.mkdtemp(), "bicho.json")
        try:
            self.assertIsNone(memoria.cargar())
            memoria.guardar(bebe().para_guardar())
            self.assertEqual(Bicho(memoria.cargar()).etapa, BEBE)
        finally:
            config.ARCHIVO = antes


if __name__ == "__main__":
    unittest.main()
