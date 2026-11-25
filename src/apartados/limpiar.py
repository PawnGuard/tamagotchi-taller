# limpiar.py — recoge las cacas. Con 3 cacas mucho rato, se enferma.
NOMBRE = "LIMPIAR"


def empezar(bicho):
    if bicho.caca == 0:
        return "YA ESTA LIMPIO"
    bicho.caca = 0
    bicho.t_sucio = 0.0
    return "LIMPIO"
