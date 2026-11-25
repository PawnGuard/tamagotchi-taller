# curar.py — la medicina lo cura... pero sabe feo.
import sonido

NOMBRE = "CURAR"


def empezar(bicho):
    if not bicho.enfermo:
        return "ESTA SANO"
    bicho.enfermo = False
    bicho.felicidad -= 10
    sonido.tocar("curar")
    return "CURADO"
